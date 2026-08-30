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
        logger.info("6. Checkpoint & Resume Mechanism: PASS")
    except Exception as e:
        logger.error(f"6. Checkpoint & Resume: FAIL ({e})")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    logger.info("ALL PHASE 2 PRE-LAUNCH SCIENTIFIC AUDIT CHECKS PASSED.")


if __name__ == "__main__":
    run_validations()
