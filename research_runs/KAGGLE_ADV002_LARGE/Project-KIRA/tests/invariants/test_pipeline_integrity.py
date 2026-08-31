"""Invariant tests for the complete end-to-end pipeline and cross-artifact consistency."""

import json
from pathlib import Path
import pytest

from mcdl.artifacts import (
    load_decisions,
    load_evaluation,
    load_manifest,
    load_transactions,
    validate_artifacts,
    verify_run_integrity,
)
from mcdl.pipeline import run_pipeline


@pytest.mark.slow
def test_pipeline_end_to_end_and_integrity(tmp_path: Path) -> None:
    """Executes the complete pipeline and verifies full cross-artifact consistency."""
    run_dir = run_pipeline(scale="tiny", seed=20260827, n_rounds=4, out_dir=tmp_path, overwrite=True)

    assert run_dir.is_dir()
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "evaluation.json").exists()
    assert (run_dir / "world_summary.json").exists()
    assert (run_dir / "feature_schema.json").exists()
    assert (run_dir / "blue_metrics.json").exists()
    assert (run_dir / "red_metrics.json").exists()
    assert (run_dir / "coevolution_metrics.json").exists()
    assert (run_dir / "policy_metrics.json").exists()
    assert (run_dir / "attack_summary.json").exists()
    assert (run_dir / "sample_transactions.json").exists()
    assert (run_dir / "calibration.json").exists()
    assert (run_dir / "external_anchor.json").exists()
    assert (run_dir / "evidence_pack.md").exists()
    assert (run_dir / "transactions.json").exists()
    assert (run_dir / "decisions.json").exists()
    assert (run_dir / "provenance.json").exists()

    # 1. Manifest verification
    manifest = load_manifest(run_dir)
    assert manifest.is_fixture is False
    assert manifest.scale == "tiny"
    assert manifest.git_commit != "unknown"
    assert len(manifest.stages_completed) >= 5

    # 2. Evaluation verification
    eval_res = load_evaluation(run_dir)
    assert len(eval_res.rounds) == 4
    assert eval_res.anchor is not None
    assert eval_res.anchor.pr_auc == 0.8640

    # 3. Cross-Artifact Consistency & Schema Validation
    valid_ok, valid_errs = validate_artifacts(run_dir)
    assert valid_ok is True, f"Artifact validation failed: {valid_errs}"

    # 4. Cryptographic Provenance & Hash Integrity
    ok, errors = verify_run_integrity(run_dir)
    assert ok is True, f"Integrity check failed: {errors}"


@pytest.mark.slow
def test_pipeline_deterministic_reproducibility(tmp_path: Path) -> None:
    """Verifies that two runs with the same seed yield bit-for-bit identical deterministic metrics."""
    dir1 = tmp_path / "run_one"
    dir2 = tmp_path / "run_two"

    r1 = run_pipeline(scale="tiny", seed=20260827, n_rounds=4, out_dir=dir1, overwrite=True)
    r2 = run_pipeline(scale="tiny", seed=20260827, n_rounds=4, out_dir=dir2, overwrite=True)

    # 1. Exact identical content for purely deterministic schema and policy files
    exact_files = [
        "world_summary.json",
        "feature_schema.json",
        "policy_metrics.json",
        "calibration.json",
        "external_anchor.json",
    ]
    for fname in exact_files:
        content1 = (r1 / fname).read_text(encoding="utf-8")
        content2 = (r2 / fname).read_text(encoding="utf-8")
        assert content1 == content2, f"Discrepancy in deterministic file {fname}"

    # 2. Compare ML and Red Metrics (excluding volatile CPU latency timings)
    b1 = json.loads((r1 / "blue_metrics.json").read_text(encoding="utf-8"))
    b2 = json.loads((r2 / "blue_metrics.json").read_text(encoding="utf-8"))
    for k in ["pr_auc", "roc_auc", "precision", "recall", "fpr", "ece", "brier", "decision_counts"]:
        assert b1.get(k) == b2.get(k), f"Discrepancy in blue_metrics.{k}: {b1.get(k)} vs {b2.get(k)}"

    r_met1 = json.loads((r1 / "red_metrics.json").read_text(encoding="utf-8"))
    r_met2 = json.loads((r2 / "red_metrics.json").read_text(encoding="utf-8"))
    assert r_met1 == r_met2, f"Discrepancy in red_metrics: {r_met1} vs {r_met2}"

    coev1 = json.loads((r1 / "coevolution_metrics.json").read_text(encoding="utf-8"))
    coev2 = json.loads((r2 / "coevolution_metrics.json").read_text(encoding="utf-8"))
    assert coev1 == coev2, f"Discrepancy in coevolution_metrics"

    # 3. Compare Transaction Decisions (excluding volatile single-transaction scoring latency_ms)
    dec1 = json.loads((r1 / "decisions.json").read_text(encoding="utf-8"))
    dec2 = json.loads((r2 / "decisions.json").read_text(encoding="utf-8"))
    assert len(dec1) == len(dec2)

    for d_a, d_b in zip(dec1, dec2):
        for k in ["txn_id", "risk_score", "calibrated_score", "decision", "reason_codes", "intent_drift_score"]:
            assert d_a.get(k) == d_b.get(k), f"Decision mismatch on {d_a.get('txn_id')} key {k}"


