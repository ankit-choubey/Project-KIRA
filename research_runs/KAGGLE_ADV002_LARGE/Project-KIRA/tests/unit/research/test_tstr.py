"""Unit tests for TSTR transfer evaluation."""

import numpy as np
from mcdl.research.tstr import evaluate_tstr_transfer


def test_evaluate_tstr_transfer():
    rng = np.random.RandomState(42)
    syn_X = rng.randn(100, 4)
    syn_y = (syn_X[:, 0] > 0.5).astype(int)
    
    real_test_X = rng.randn(50, 4)
    real_test_y = (real_test_X[:, 0] > 0.5).astype(int)
    
    res = evaluate_tstr_transfer(syn_X, syn_y, real_test_X, real_test_y, seed=42)
    assert res["status"] == "COMPLETE"
    assert "tstr" in res
    assert "pr_auc" in res["tstr"]
    assert res["tstr"]["pr_auc"] >= 0.0
    assert "roc_auc" in res["tstr"]
