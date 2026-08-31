import json
import os
import shutil
from pathlib import Path

import numpy as np
import polars as pl
import pytest

from mcdl.research.phase2 import experiments as exp
from mcdl.research.phase2.graph_temporal import TemporalPaymentGraph
from mcdl.research.phase2.state import CheckpointManager, PHASE2_DIR
from mcdl.research.phase2.validation import (
    get_exact_feature_dimensions,
    verify_acd_fairness,
    verify_authoritative_baseline_integrity,
)


@pytest.fixture
def clean_manager(tmp_path):
    os.environ["MCDL_SCALE"] = "tiny"
    if PHASE2_DIR.exists():
        shutil.rmtree(PHASE2_DIR)
    
    manager = CheckpointManager(
        run_id="test_s02_s04_clean",
        git_commit="test_sha_12345",
        baseline_run_id="run_tiny_s20260827_193f7897_40997ab",
        baseline_git_commit="40997ab",
    )
    yield manager
    if PHASE2_DIR.exists():
        shutil.rmtree(PHASE2_DIR)


def test_authoritative_baseline_integrity():
    report = verify_authoritative_baseline_integrity(exp.BASELINE_RUN_DIR)
    assert report["status"] == "PASS"
    assert report["expected_file_count"] == 22
    assert report["actual_file_count"] == 22
    assert len(report["passed_files"]) == 22
    assert len(report["missing_files"]) == 0
    assert len(report["hash_mismatches"]) == 0


def test_feature_dimensions():
    df = exp._load_baseline_transactions()
    graph = TemporalPaymentGraph(df)
    dim_info = get_exact_feature_dimensions(graph)
    assert dim_info["canonical_feature_count"] == 25
    assert len(dim_info["canonical_feature_names"]) == 25
    assert dim_info["graph_embedding_dim"] == 16
    assert dim_info["fusion_input_dim"] == 41
    assert dim_info["arm_a_input_dim"] == 25
    assert dim_info["arm_c_input_dim"] == 41
    assert dim_info["arm_d_input_dim"] == 41


def test_acd_fairness():
    df = exp._load_baseline_transactions()
    real_graph = TemporalPaymentGraph(df)
    shuff_graph = exp.create_shuffled_topology_graph(real_graph, seed=20260827)
    
    n = real_graph.n_txns
    train_indices = np.arange(int(0.70 * n))
    val_indices = np.arange(int(0.70 * n), int(0.85 * n))
    test_indices = np.arange(int(0.85 * n), n)

    fairness = verify_acd_fairness(real_graph, shuff_graph, train_indices, val_indices, test_indices)
    assert fairness["all_passed"] is True
    assert fairness["same_transactions"] is True
    assert fairness["same_labels"] is True
    assert fairness["same_timestamps"] is True
    assert fairness["same_tabular_features"] is True
    assert fairness["temporal_ordering_valid"] is True
    assert fairness["topology_destroyed"] is True


def test_s02_per_arm_checkpointing_and_resume(clean_manager):
    # Run S-02
    exp.run_s02(clean_manager)
    assert clean_manager.get_state("S02") == "COMPLETED"

    s02_dir = PHASE2_DIR / "S02"
    assert (s02_dir / "integrity.json").exists()
    assert (s02_dir / "feature_dimensions.json").exists()
    assert (s02_dir / "metrics.json").exists()

    # Check granular per-arm checkpoints for primary seed
    seed_dir = s02_dir / "seed_20260827"
    assert (seed_dir / "fairness.json").exists()
    assert (seed_dir / "estimands.json").exists()

    for arm in ["arm_A", "arm_C", "arm_D"]:
        arm_dir = seed_dir / arm
        assert (arm_dir / "config.json").exists()
        assert (arm_dir / "status.json").exists()
        assert (arm_dir / "metrics.json").exists()
        assert (arm_dir / "provenance.json").exists()
        assert (arm_dir / "test_probs.npy").exists()
        
        status_data = json.loads((arm_dir / "status.json").read_text())
        assert status_data["status"] == "COMPLETED"

    # Test resume idempotence
    exp.run_s02(clean_manager)
    assert clean_manager.get_state("S02") == "COMPLETED"


def test_s03_zero_day_metrics(clean_manager):
    exp.run_s03(clean_manager)
    assert clean_manager.get_state("S03") == "COMPLETED"

    s03_metrics_path = PHASE2_DIR / "S03" / "metrics.json"
    assert s03_metrics_path.exists()
    s03_data = json.loads(s03_metrics_path.read_text())

    wc = s03_data["world_c_zero_day"]
    assert "sample_count" in wc
    assert "total_attack_count" in wc
    assert "per_family_attack_count" in wc
    assert "asr_arm_a_baseline" in wc
    assert "asr_arm_c_fusion" in wc
    assert "robustness_delta" in wc
    assert "status" in wc
    assert wc["status"] in ("EVALUATED", "LOW_SAMPLE")
    # Missing values must remain None / null, not 0
    if wc["status"] == "LOW_SAMPLE":
        assert wc["confidence_interval_95"] is None
        assert wc["med"] is None
        assert wc["median_med"] is None


def test_s04_structured_claims_reconciliation(clean_manager):
    exp.run_s00(clean_manager)
    exp.run_s01(clean_manager)
    exp.run_g03(clean_manager)
    exp.run_s02(clean_manager)
    exp.run_s03(clean_manager)
    exp.run_s04(clean_manager)

    assert clean_manager.get_state("S04") == "COMPLETED"
    s04_dir = PHASE2_DIR / "S04"

    assert (s04_dir / "integrity.json").exists()
    assert (s04_dir / "master_results.json").exists()
    assert (s04_dir / "comparison_table.json").exists()
    assert (s04_dir / "evidence_report.md").exists()

    master = json.loads((s04_dir / "master_results.json").read_text())
    assert master["baseline_integrity_verified"] is True
    claims = master["claims_registry"]
    assert len(claims) >= 6

    valid_classifications = {
        "MEASURED",
        "MEASURED_WITH_CAVEAT",
        "INCONCLUSIVE",
        "LOW_SAMPLE",
        "NOT_MEASURED",
        "FAILURE_FINDING",
        "NOT_RUN",
        "SUCCESS",
        "CALIBRATION_OR_FPR_DEGRADATION",
        "PARAMETER_ARTIFACT",
        "NO_INCREMENT",
        "EVALUATED",
    }

    for c in claims:
        assert "claim_id" in c
        assert "claim_name" in c
        assert "experiment_id" in c
        assert "dataset_id" in c
        assert "scale" in c
        assert "world_seed" in c
        assert "model_seed" in c
        assert "metric_name" in c
        assert "classification" in c
        assert "artifact_path" in c
        assert "git_sha" in c
        assert c["classification"] in valid_classifications


def test_s02_forced_arm_failure_resilience(clean_manager, monkeypatch):
    # Pre-populate Arm A as completed with all 4 required files
    seed_dir = PHASE2_DIR / "S02" / "seed_20260827"
    arm_a_dir = seed_dir / "arm_A"
    arm_a_dir.mkdir(parents=True, exist_ok=True)
    
    (arm_a_dir / "status.json").write_text(json.dumps({"status": "COMPLETED"}))
    (arm_a_dir / "metrics.json").write_text(json.dumps({"pr_auc": 0.99, "roc_auc": 0.99, "fpr": 0.01, "ece": 0.01, "brier": 0.01}))
    (arm_a_dir / "provenance.json").write_text(json.dumps({"arm": "arm_A"}))
    np.save(arm_a_dir / "test_probs.npy", np.array([0.1, 0.9]))

    # Monkeypatch CausalGraphTabularFusion to force failure on Arm C
    def mock_fit(*args, **kwargs):
        raise RuntimeError("Forced OOM/Failure in Arm C")

    monkeypatch.setattr(exp.CausalGraphTabularFusion, "fit", mock_fit)

    exp.run_s02(clean_manager)
    assert clean_manager.get_state("S02") == "FAILED"

    # Verify Arm A remained intact
    assert json.loads((arm_a_dir / "status.json").read_text())["status"] == "COMPLETED"
    
    # Verify Arm C was marked FAILED
    arm_c_dir = seed_dir / "arm_C"
    assert (arm_c_dir / "status.json").exists()
    status_c = json.loads((arm_c_dir / "status.json").read_text())
    assert status_c["status"] == "FAILED"
    assert "Forced OOM/Failure in Arm C" in status_c["error"]


def test_s02_timeout_enforcement(clean_manager, monkeypatch):
    # Monkeypatch time.monotonic to simulate timeout during Arm A fit
    real_monotonic = exp.time.monotonic
    call_count = {"count": 0}

    def mock_monotonic():
        call_count["count"] += 1
        if call_count["count"] > 3:
            return real_monotonic() + 8000.0  # Exceeds 7200s budget
        return real_monotonic()

    monkeypatch.setattr(exp.time, "monotonic", mock_monotonic)

    exp.run_s02(clean_manager)
    assert clean_manager.get_state("S02") in ("TIMEOUT", "FAILED")

    # Status should reflect TIMEOUT
    seed_dir = PHASE2_DIR / "S02" / "seed_20260827"
    arm_a_status = seed_dir / "arm_A" / "status.json"
    if arm_a_status.exists():
        status_data = json.loads(arm_a_status.read_text())
        assert status_data["status"] in ("TIMEOUT", "FAILED")

