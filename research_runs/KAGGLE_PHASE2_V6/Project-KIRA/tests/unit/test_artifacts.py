"""Unit tests for artifact serialization, loading, schema validation, and integrity checking."""

import json
from pathlib import Path
import pytest

from mcdl.artifacts import (
    calculate_sha256,
    canonical_json_dumps,
    deterministic_run_id,
    generate_provenance_manifest,
    is_run_finalized,
    load_evaluation,
    load_manifest,
    make_manifest,
    mark_run_finalized,
    validate_artifacts,
    verify_run_integrity,
    write_evaluation,
    write_granular_artifacts,
)
from mcdl.config import load_config
from mcdl.evaluation.anchor import evaluate_external_anchor, get_external_anchor_metadata
from mcdl.features.spec import FEATURE_SPECS, get_feature_schema
from mcdl.schemas import (
    BlueDecision,
    BlueMetrics,
    Decision,
    EvaluationResult,
    FidelityReport,
    RedMetrics,
    RoundResult,
    RunManifest,
    Transaction,
)


def test_sha256_calculation(tmp_path: Path) -> None:
    test_file = tmp_path / "test.txt"
    test_file.write_text("Mastercard AI Defense Lab", encoding="utf-8")
    h1 = calculate_sha256(test_file)
    assert len(h1) == 64
    assert isinstance(h1, str)

    # Identical content yields identical hash
    test_file2 = tmp_path / "test2.txt"
    test_file2.write_text("Mastercard AI Defense Lab", encoding="utf-8")
    assert calculate_sha256(test_file2) == h1


def test_deterministic_run_id() -> None:
    r1 = deterministic_run_id("tiny", 20260827, "a1b2c3d4e5", "abc1234")
    r2 = deterministic_run_id("tiny", 20260827, "a1b2c3d4e5", "abc1234")
    assert r1 == r2
    assert "tiny" in r1
    assert "20260827" in r1
    assert "a1b2c3d4" in r1


def test_provenance_and_integrity_verification(tmp_path: Path) -> None:
    run_dir = tmp_path / "test_run"
    run_dir.mkdir()

    (run_dir / "manifest.json").write_text('{"run_id": "test_run"}', encoding="utf-8")
    (run_dir / "metrics.json").write_text('{"accuracy": 0.99}', encoding="utf-8")

    prov = generate_provenance_manifest(run_dir)
    assert prov["artifact_count"] == 2
    (run_dir / "provenance.json").write_text(json.dumps(prov), encoding="utf-8")

    # Integrity verification should pass
    ok, errors = verify_run_integrity(run_dir)
    assert ok is True
    assert len(errors) == 0

    # Corrupt a file -> should fail integrity check
    (run_dir / "metrics.json").write_text('{"accuracy": 0.50}', encoding="utf-8")
    ok_corrupted, errors_corrupted = verify_run_integrity(run_dir)
    assert ok_corrupted is False
    assert any("HASH_MISMATCH:metrics.json" in e for e in errors_corrupted)


def test_external_anchor_schema_and_metadata() -> None:
    anchor = evaluate_external_anchor()
    assert anchor.pr_auc is not None
    assert 0.0 <= anchor.pr_auc <= 1.0
    assert anchor.roc_auc is not None
    assert 0.0 <= anchor.roc_auc <= 1.0
    assert anchor.fpr is not None
    assert 0.0 <= anchor.fpr <= 1.0
    assert anchor.decision_counts["ALLOW"] > 0

    meta = get_external_anchor_metadata()
    assert meta["namespace"] == "REAL_WORLD"
    assert "ULB" in meta["source_organization"]
    assert meta["transaction_count"] == 284807
    assert meta["fraud_count"] == 492
    assert "10.1109/SSCI.2015.33" in meta["doi"]
    assert meta["used_in_training"] is False
    assert len(meta["comparability_limitations"]) > 0


def test_dynamic_feature_schema() -> None:
    schema = get_feature_schema()
    assert schema["schema_version"] == "0.1.0"
    assert schema["feature_count"] == len(FEATURE_SPECS)
    assert len(schema["features"]) == len(FEATURE_SPECS)
    assert schema["label_delay_lag_seconds"] == 604800


def test_overwrite_protection(tmp_path: Path) -> None:
    run_d = tmp_path / "finalized_run"
    run_d.mkdir()

    mark_run_finalized(run_d)
    assert is_run_finalized(run_d) is True

    cfg = load_config(scale="tiny")
    manifest = make_manifest(cfg, "finalized_run")
    eval_res = EvaluationResult(
        manifest=manifest,
        fidelity=FidelityReport(l1_violations=0, l1_checks={}),
        rounds=[],
        anchor=None,
        ablations={},
    )

    with pytest.raises(PermissionError):
        write_granular_artifacts(
            d=run_d,
            evaluation=eval_res,
            transactions=[],
            decisions=[],
            world_summary={},
            coevolution_reports=[],
            attack_summary={},
            sample_txns_with_shap=[],
            overwrite=False,
        )

