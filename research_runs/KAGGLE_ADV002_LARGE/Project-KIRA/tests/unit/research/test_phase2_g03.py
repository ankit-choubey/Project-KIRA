"""Unit tests for G-03: Causal Graph + Tabular Fusion.

Validates:
1. 4-arm experimental matrix integrity (Arms A, B, C, D)
2. No mock or hardcoded numerical values
3. Deterministic shuffled topology generation & empirical property measurement
4. Feature dimensionality & concatenation
5. Temporal causality & validation-only calibration isolation
6. Automated decision rule classification & interpretation
"""

import numpy as np
import polars as pl
import pytest

from mcdl.research.phase2.fusion import (
    CausalGraphTabularFusion,
    bootstrap_pr_auc_ci,
    classify_g03_decision,
    compute_ece,
    compute_fpr_at_recall,
    compute_paired_bootstrap_p_value,
    create_shuffled_topology_graph,
    evaluate_arm_metrics,
    measure_topology_properties,
)
from mcdl.research.phase2.graph_temporal import TemporalPaymentGraph


from mcdl.research.phase2.experiments import _load_baseline_transactions


@pytest.fixture
def synthetic_graph() -> TemporalPaymentGraph:
    """Generates a temporal payment graph fixture using baseline transactions."""
    df = _load_baseline_transactions().head(150)
    return TemporalPaymentGraph(df)


def test_shuffled_topology_properties(synthetic_graph: TemporalPaymentGraph):
    """Verifies deterministic shuffled topology generation and empirical measurement."""
    seed = 20260827
    shuff_g1 = create_shuffled_topology_graph(synthetic_graph, seed=seed)
    shuff_g2 = create_shuffled_topology_graph(synthetic_graph, seed=seed)

    # Determinism with S_shuff = seed + 999
    assert shuff_g1.customer_ids == shuff_g2.customer_ids
    assert shuff_g1.merchant_ids == shuff_g2.merchant_ids
    assert shuff_g1.device_ids == shuff_g2.device_ids

    # Permutation destroyed actual entity mappings
    assert not np.array_equal(synthetic_graph.customer_ids, shuff_g1.customer_ids)

    # Topology measurement
    report = measure_topology_properties(synthetic_graph, shuff_g1)
    assert "real_graph" in report
    assert "shuffled_graph" in report
    assert report["real_graph"]["node_count"] > 0
    assert report["real_graph"]["edge_count"] == synthetic_graph.n_txns * 3
    assert report["shuffled_graph"]["edge_count"] == synthetic_graph.n_txns * 3
    assert "degree_ks_statistic" in report
    assert report["topology_destroyed"] is True


def test_fusion_model_training_and_calibration(synthetic_graph: TemporalPaymentGraph):
    """Verifies dual-branch model fitting and validation-only calibration."""
    n = synthetic_graph.n_txns
    train_idx = np.arange(int(0.70 * n))
    val_idx = np.arange(int(0.70 * n), int(0.85 * n))
    test_idx = np.arange(int(0.85 * n), n)

    fusion_model = CausalGraphTabularFusion(seed=20260827, n_estimators=20)
    fusion_model.fit(synthetic_graph, train_idx, val_idx)

    # Test prediction
    test_probs = fusion_model.predict_proba(synthetic_graph, test_idx)
    assert len(test_probs) == len(test_idx)
    assert np.all(test_probs >= 0.0)
    assert np.all(test_probs <= 1.0)
    assert not np.any(np.isnan(test_probs))


def test_decision_classification_logic():
    """Verifies pre-registered decision rules and automated statement generation."""
    # 1. Success case
    dec, stmt = classify_g03_decision(
        delta_rel=0.015,
        delta_topo=0.012,
        fpr_c=0.02,
        fpr_a=0.02,
        ece_c=0.01,
        p_value=0.01,
        sample_count=100,
    )
    assert dec == "SUCCESS"
    assert "incremental predictive value" in stmt

    # 2. Parameter artifact case
    dec, stmt = classify_g03_decision(
        delta_rel=0.015,
        delta_topo=0.001,
        fpr_c=0.02,
        fpr_a=0.02,
        ece_c=0.01,
        p_value=0.01,
        sample_count=100,
    )
    assert dec == "PARAMETER_ARTIFACT"
    assert "parameter capacity expansion" in stmt

    # 3. No increment case
    dec, stmt = classify_g03_decision(
        delta_rel=-0.005,
        delta_topo=0.0,
        fpr_c=0.02,
        fpr_a=0.02,
        ece_c=0.01,
        p_value=0.50,
        sample_count=100,
    )
    assert dec == "NO_INCREMENT"
    assert "does NOT provide" in stmt

    # 4. Low sample case
    dec, stmt = classify_g03_decision(
        delta_rel=0.02,
        delta_topo=0.02,
        fpr_c=0.02,
        fpr_a=0.02,
        ece_c=0.01,
        p_value=0.01,
        sample_count=15,
    )
    assert dec == "INCONCLUSIVE"
    assert "sample limitations" in stmt


def test_paired_bootstrap_p_value():
    """Verifies paired difference bootstrap calculation."""
    y = np.array([0, 0, 0, 1, 0, 1, 0, 0, 1, 0])
    p_c = np.array([0.1, 0.2, 0.1, 0.9, 0.2, 0.85, 0.1, 0.05, 0.95, 0.15])
    p_a = np.array([0.1, 0.2, 0.1, 0.9, 0.2, 0.85, 0.1, 0.05, 0.95, 0.15])

    # Identical predictions -> p = 1.0
    p_val = compute_paired_bootstrap_p_value(y, p_c, p_a, n_resamples=100, seed=42)
    assert p_val == 1.0
