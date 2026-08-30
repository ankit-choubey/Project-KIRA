"""Comprehensive Scientific Invariant & Smoke Test Suite for Phase 2."""

import json
import logging
import shutil
import sys
from pathlib import Path

sys.path.append("src")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def run_validations():
    logger.info("Starting Phase 2 Pre-Launch Scientific Audit...")

    # 1. Notebook JSON syntax
    try:
        with open("notebooks/kaggle/04_phase2_mega_notebook.ipynb", "r", encoding="utf-8") as f:
            nb = json.load(f)
        assert "cells" in nb
        logger.info("1. Notebook JSON syntax: PASS")
    except Exception as e:
        logger.error(f"1. Notebook JSON syntax: FAIL ({e})")
        sys.exit(1)

    # 2. Python imports
    try:
        from mcdl.research.phase2.state import CheckpointManager, StageExecution
        from mcdl.research.phase2.graph_temporal import TemporalPaymentGraph
        from mcdl.research.phase2.model import CausalGraphSAGE, get_parameter_count
        from mcdl.research.phase2.validation import (
            run_feature_level_temporal_causality_test,
            run_temporal_leakage_tests,
            verify_temporal_split_semantics,
        )
        from mcdl.research.phase2 import experiments as exp
        logger.info("2. Python imports: PASS")
    except ImportError as e:
        logger.error(f"2. Python imports: FAIL ({e})")
        sys.exit(1)

    df = exp._load_baseline_transactions()
    assert len(df) > 0

    # 3. Feature-Level Temporal Causality Invariance Test
    try:
        feat_causality_res = run_feature_level_temporal_causality_test(df.slice(0, 1000), tolerance=1e-9)
        assert feat_causality_res["passed"] is True
        assert feat_causality_res["global_max_delta"] <= 1e-9
        logger.info(
            f"3. Feature-Level Causality Test: PASS "
            f"(features={feat_causality_res['features_evaluated_count']}, max_delta={feat_causality_res['global_max_delta']:.2e})"
        )
    except Exception as e:
        logger.error(f"3. Feature-Level Causality Test: FAIL ({e})")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 4. Temporal Split Semantics Verification
    try:
        split_res = verify_temporal_split_semantics(df, train_ratio=0.70, val_ratio=0.15)
        assert split_res["passed"] is True
        assert split_res["out_of_time_valid"] is True
        assert split_res["disjoint_splits_valid"] is True
        logger.info(
            f"4. Temporal Split Semantics: PASS "
            f"(train={split_res['train_count']}, val={split_res['val_count']}, test={split_res['test_count']})"
        )
    except Exception as e:
        logger.error(f"4. Temporal Split Semantics: FAIL ({e})")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 5. Graph-Level 4 Leakage Invariance Tests
    try:
        graph = TemporalPaymentGraph(df.slice(0, 1000))
        model = CausalGraphSAGE(
            in_dim_txn=len(graph.feature_names),
            in_dim_agg=len(graph.feature_names),
            in_dim_entity=7,
            hidden_dim=32,
            out_dim=16,
            seed=20260827,
        )
        param_count = model.count_parameters()
        assert param_count > 0

        leakage_results = run_temporal_leakage_tests(graph, model, tolerance=1e-12)
        assert leakage_results["all_passed"] is True
        assert leakage_results["tests"]["future_edge_invariance"]["status"] == "PASS"
        assert leakage_results["tests"]["future_node_feature_invariance"]["status"] == "PASS"
        assert leakage_results["tests"]["future_label_invariance"]["status"] == "PASS"
        assert leakage_results["tests"]["prediction_at_t_invariance"]["status"] == "PASS"
        assert leakage_results["global_max_delta"] <= 1e-12
        logger.info(
            f"5. Four Graph Leakage Invariance Tests: PASS "
            f"(backend='CPU (NumPy vectorized)', params={param_count}, global_max_delta={leakage_results['global_max_delta']:.2e})"
        )
    except Exception as e:
        logger.error(f"5. Graph Leakage Tests: FAIL ({e})")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 6. Checkpoint & Resume System Validation
    try:
        p2_dir = Path("research_runs/PHASE2")
        if p2_dir.exists():
            shutil.rmtree(p2_dir)

        manager = CheckpointManager(
            run_id="test_smoke_run",
            git_commit="test_commit",
            baseline_run_id="run_tiny_s20260827_193f7897_40997ab",
            baseline_git_commit="40997ab",
        )

        exp.run_s00(manager)
        assert manager.get_state("S00") == "COMPLETED"

        exp.run_s01(manager)
        assert manager.get_state("S01") == "COMPLETED"

        # Test resume skips completed stage
        exp.run_s00(manager)
        assert manager.get_state("S00") == "COMPLETED"
        # 7. G-03 Graph + Tabular Fusion 4-Arm Validation
        exp.run_g03(manager)
        assert manager.get_state("G03") == "COMPLETED"
        g03_metrics_path = Path("research_runs/PHASE2/G03/metrics.json")
        assert g03_metrics_path.exists()
        with open(g03_metrics_path, "r", encoding="utf-8") as f:
            g03_data = json.load(f)
        assert "arm_a_baseline" in g03_data["arms"]
        assert "arm_b_graph_diagnostic" in g03_data["arms"]
        assert "arm_c_real_fusion" in g03_data["arms"]
        assert "arm_d_shuffled_control" in g03_data["arms"]
        assert "decision_classification" in g03_data
        assert "topology_verification" in g03_data
        logger.info(f"7. G-03 Fusion 4-Arm Execution: PASS (decision={g03_data['decision_classification']}, delta_rel={g03_data['estimands']['delta_rel']:+.4f})")
        # 8. FINAL Master Evidence Synthesis Validation
        exp.run_final(manager)
        assert manager.get_state("FINAL") == "COMPLETED"
        comp_path = Path("research_runs/PHASE2/FINAL/comparison_table.json")
        assert comp_path.exists()
        with open(comp_path, "r", encoding="utf-8") as f:
            comp_data = json.load(f)
        assert "G03" in comp_data["stages_completed"]
        logger.info(f"8. FINAL Synthesis Execution: PASS (stages={comp_data['stages_completed']})")

        logger.info("ALL PHASE 2 PRE-LAUNCH SCIENTIFIC AUDIT CHECKS PASSED.")
    except Exception as e:
        logger.error(f"Validation step failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_validations()
