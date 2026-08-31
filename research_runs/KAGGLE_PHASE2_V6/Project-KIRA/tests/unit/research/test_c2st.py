"""Unit tests for Classifier Two-Sample Test (C2ST)."""

import numpy as np
from mcdl.research.c2st import run_c2st_evaluation


def test_c2st_evaluation_distinguishable():
    # Synthetic from N(0, 1), Real from N(5, 1) -> easily distinguished (AUC ~ 1.0)
    syn = np.random.RandomState(42).randn(100, 3)
    real = np.random.RandomState(42).randn(100, 3) + 5.0
    
    res = run_c2st_evaluation(syn, real, feature_names=["f1", "f2", "f3"], n_bootstrap=10)
    assert res["status"] == "COMPLETE"
    assert res["c2st_auc"] > 0.9
    assert len(res["ci_95"]) == 2
    assert len(res["feature_importances_top10"]) == 3


def test_c2st_evaluation_empty():
    syn = np.empty((0, 3))
    real = np.random.randn(10, 3)
    res = run_c2st_evaluation(syn, real)
    assert res["status"] == "INCOMPLETE"
    assert res["c2st_auc"] is None
