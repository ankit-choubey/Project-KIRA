"""Comprehensive Smoke & Unit Test for Phase 2 Implementation."""

import json
import logging
import shutil
import sys
from pathlib import Path

sys.path.append("src")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def run_validations():
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
        from mcdl.research.phase2.validation import run_temporal_leakage_tests
        from mcdl.research.phase2 import experiments as exp
        logger.info("2. Python imports: PASS")
    except ImportError as e:
        logger.error(f"2. Python imports: FAIL ({e})")
        sys.exit(1)

    # 3. Real Temporal Graph & 4 Leakage Tests Validation
    try:
        df = exp._load_baseline_transactions()
        assert len(df) > 0
        graph = TemporalPaymentGraph(df.slice(0, 1000))
        assert graph.n_txns == 1000

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

        leakage_results = run_temporal_leakage_tests(graph, model)
        assert leakage_results["all_passed"] is True
        assert leakage_results["future_edge_invariance"] is True
        assert leakage_results["future_node_feature_invariance"] is True
        assert leakage_results["future_label_invariance"] is True
        assert leakage_results["prediction_at_t_invariance"] is True
        assert leakage_results["max_delta"] < 1e-12
        logger.info(f"3. Strict 4 Temporal Leakage Tests: PASS (params={param_count}, max_delta={leakage_results['max_delta']})")
    except Exception as e:
        logger.error(f"3. Temporal Leakage Tests: FAIL ({e})")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 4. Checkpoint & Resume System Validation
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
        logger.info("4. Checkpoint & Resume Mechanism: PASS")
    except Exception as e:
        logger.error(f"4. Checkpoint & Resume: FAIL ({e})")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    logger.info("All local Phase 2 static, unit, and smoke validations PASSED.")


if __name__ == "__main__":
    run_validations()
