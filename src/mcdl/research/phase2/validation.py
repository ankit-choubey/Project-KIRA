"""Temporal Causality & Invariance Leakage Test Suite.

Implements the 4 mandatory leakage tests for G-01:
1. Future-edge invariance: Adding future edges strictly > t does not alter prediction(t).
2. Future-node-feature invariance: Mutating node features of future events > t does not alter prediction(t).
3. Future-label invariance: Flipping fraud labels of future events > t does not alter prediction(t).
4. Prediction-at-t invariance: Evaluating transaction t on the full timeline vs. a snapshot strictly <= t yields identical prediction (|delta| < 1e-12).
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import polars as pl

from mcdl.research.phase2.graph_temporal import TemporalPaymentGraph
from mcdl.research.phase2.model import CausalGraphSAGE

logger = logging.getLogger(__name__)


def run_temporal_leakage_tests(
    graph: TemporalPaymentGraph,
    model: CausalGraphSAGE,
    eval_indices: list[int] | None = None,
) -> dict[str, Any]:
    """Executes the four strict temporal leakage invariance tests on real graph data and model."""
    if eval_indices is None or len(eval_indices) == 0:
        # Sample mid-timeline transactions for evaluation
        n = graph.n_txns
        eval_indices = list(range(n // 4, n // 2, max(1, n // 20)))

    results: dict[str, Any] = {
        "future_edge_invariance": False,
        "future_node_feature_invariance": False,
        "future_label_invariance": False,
        "prediction_at_t_invariance": False,
        "all_passed": False,
        "max_delta": 0.0,
        "eval_sample_count": len(eval_indices),
    }

    # Base predictions for evaluation indices
    base_probs = model.predict_proba(graph, eval_indices)

    # -------------------------------------------------------------------------
    # Test 1: Future-edge invariance
    # Add fake future transactions (connecting customers/merchants in the future)
    # -------------------------------------------------------------------------
    max_eval_idx = max(eval_indices)
    max_eval_ts = graph.timestamps[max_eval_idx]
    from datetime import datetime, timezone
    future_txns = []
    for i in range(50):
        future_ts = datetime.fromtimestamp(max_eval_ts + 1000.0 + i * 10.0, tz=timezone.utc).replace(tzinfo=None)
        future_txns.append({
            "txn_id": f"tx_fake_future_{i:04d}",
            "customer_id": graph.customer_ids[i % len(graph.customer_ids)],
            "merchant_id": graph.merchant_ids[i % len(graph.merchant_ids)],
            "device_id": graph.device_ids[i % len(graph.device_ids)],
            "timestamp": future_ts,
            "amount": 999.99,
            "mcc": "5411",
            "channel": "ecommerce",
            "lat": 40.0, "lon": -74.0,
            "ip_prefix": "192.168",
            "is_new_device": True,
            "auth_failed_count": 2,
            "agent_id": None,
            "mandate_id": None,
            "balance_before": 5000.0,
            "available_credit": 5000.0,
            "is_fraud": True,
            "attack_family": "synthetic_identity",
        })
    future_df = pl.DataFrame(future_txns)
    augmented_raw = pl.concat([graph.raw_df, future_df], how="diagonal")
    augmented_graph = TemporalPaymentGraph(augmented_raw)

    aug_probs = model.predict_proba(augmented_graph, eval_indices)
    diff_edges = np.max(np.abs(base_probs - aug_probs))
    results["future_edge_invariance"] = bool(diff_edges < 1e-12)
    results["max_delta"] = max(results["max_delta"], float(diff_edges))

    if not results["future_edge_invariance"]:
        logger.error(f"Future-edge invariance FAILED: max delta = {diff_edges}")
        return results

    # -------------------------------------------------------------------------
    # Test 2: Future-node-feature invariance
    # Mutate feature tensors of future transactions strictly > max_eval_idx
    # -------------------------------------------------------------------------
    mutated_graph = TemporalPaymentGraph(graph.raw_df)
    # Corrupt all transaction features strictly after the evaluated timestamps
    mutated_graph.x_txn[max_eval_idx + 1:] = np.random.randn(*mutated_graph.x_txn[max_eval_idx + 1:].shape) * 1000.0

    mut_probs = model.predict_proba(mutated_graph, eval_indices)
    diff_feats = np.max(np.abs(base_probs - mut_probs))
    results["future_node_feature_invariance"] = bool(diff_feats < 1e-12)
    results["max_delta"] = max(results["max_delta"], float(diff_feats))

    if not results["future_node_feature_invariance"]:
        logger.error(f"Future-node-feature invariance FAILED: max delta = {diff_feats}")
        return results

    # -------------------------------------------------------------------------
    # Test 3: Future-label invariance
    # Flip labels of all future transactions strictly > max_eval_idx
    # -------------------------------------------------------------------------
    label_graph = TemporalPaymentGraph(graph.raw_df)
    label_graph.is_fraud[max_eval_idx + 1:] = 1 - label_graph.is_fraud[max_eval_idx + 1:]

    lbl_probs = model.predict_proba(label_graph, eval_indices)
    diff_labels = np.max(np.abs(base_probs - lbl_probs))
    results["future_label_invariance"] = bool(diff_labels < 1e-12)
    results["max_delta"] = max(results["max_delta"], float(diff_labels))

    if not results["future_label_invariance"]:
        logger.error(f"Future-label invariance FAILED: max delta = {diff_labels}")
        return results

    # -------------------------------------------------------------------------
    # Test 4: Prediction-at-t invariance
    # Build a truncated graph containing strictly transactions <= max_eval_idx
    # -------------------------------------------------------------------------
    truncated_df = graph.raw_df.slice(0, max_eval_idx + 1)
    truncated_graph = TemporalPaymentGraph(truncated_df)

    trunc_probs = model.predict_proba(truncated_graph, eval_indices)
    diff_snapshot = np.max(np.abs(base_probs - trunc_probs))
    results["prediction_at_t_invariance"] = bool(diff_snapshot < 1e-12)
    results["max_delta"] = max(results["max_delta"], float(diff_snapshot))

    if not results["prediction_at_t_invariance"]:
        logger.error(f"Prediction-at-t invariance FAILED: max delta = {diff_snapshot}")
        return results

    results["all_passed"] = True
    logger.info("All 4 temporal leakage tests PASSED with max delta = 0.0.")
    return results
