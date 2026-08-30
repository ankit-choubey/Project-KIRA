"""Temporal Causality & Invariance Leakage Test Suite.

Provides rigorous scientific verification of temporal causality:
1. Feature-Level Temporal Causality Invariance:
   Mutates all future transaction fields strictly after timestamp t and verifies
   that every canonical feature produced by compute_batch_features for transaction t
   is numerically identical (delta <= 1e-9).

2. Graph-Level Leakage Invariance (4 tests):
   - Future-edge invariance
   - Future-node-feature invariance
   - Future-label invariance
   - Prediction-at-t invariance

3. Temporal Split Integrity:
   Verifies max(train.ts) < min(val.ts) < min(test.ts) and disjoint transaction sets.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from mcdl.features.batch import compute_batch_features
from mcdl.features.spec import FEATURE_NAMES
from mcdl.research.phase2.graph_temporal import TemporalPaymentGraph
from mcdl.research.phase2.model import CausalGraphSAGE

logger = logging.getLogger(__name__)


# =============================================================================
# 1. Feature-Level Temporal Causality Invariance Test
# =============================================================================
def run_feature_level_temporal_causality_test(
    df: pl.DataFrame,
    target_indices: list[int] | None = None,
    tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Tests that mutating future transactions strictly after t does not alter features at t."""
    if "timestamp" in df.columns and df["timestamp"].dtype == pl.String:
        clean_df = df.with_columns(pl.col("timestamp").str.to_datetime()).sort(["timestamp", "txn_id"])
    else:
        clean_df = df.sort(["timestamp", "txn_id"])

    n_total = len(clean_df)
    if target_indices is None:
        # Sample transactions across timeline
        target_indices = [
            int(0.20 * n_total),
            int(0.35 * n_total),
            int(0.50 * n_total),
            int(0.65 * n_total),
            int(0.80 * n_total),
        ]

    # Baseline features
    base_features = compute_batch_features(clean_df)
    feature_cols = [c for c in FEATURE_NAMES if c in base_features.columns]

    per_feature_max_deltas: dict[str, float] = {col: 0.0 for col in feature_cols}
    global_max_delta = 0.0
    failed_features: list[dict[str, Any]] = []

    for t_idx in target_indices:
        target_ts = clean_df["timestamp"][t_idx]
        target_txn_id = clean_df["txn_id"][t_idx]

        # Construct mutated dataset where everything strictly AFTER t_idx is radically altered
        mutated_rows = []
        for i in range(n_total):
            row = clean_df.row(i, named=True)
            if i > t_idx:
                # Radically mutate future event
                row["amount"] = float(row["amount"] * 100.0 + 777.77)
                row["lat"] = float(row["lat"] + 35.0)
                row["lon"] = float(row["lon"] - 45.0)
                row["device_id"] = f"dev_mutated_{i}"
                row["merchant_id"] = f"m_mutated_{i % 5}"
                row["is_fraud"] = not row["is_fraud"]
                row["auth_failed_count"] = int(row["auth_failed_count"] + 7)
                row["is_new_device"] = not row["is_new_device"]
                row["channel"] = "pos" if row["channel"] == "ecommerce" else "ecommerce"
                row["mcc"] = "7995"
                row["balance_before"] = float(row["balance_before"] * 0.05)
                row["available_credit"] = float(row["available_credit"] * 10.0)
                row["ip_prefix"] = "10.99.99"
                row["agent_id"] = f"agent_mutated_{i}"
            mutated_rows.append(row)

        mutated_df = pl.DataFrame(mutated_rows, infer_schema_length=None)
        if "timestamp" in mutated_df.columns and mutated_df["timestamp"].dtype == pl.String:
            mutated_df = mutated_df.with_columns(pl.col("timestamp").str.to_datetime())

        mut_features = compute_batch_features(mutated_df)

        # Check all features for target transaction
        for col in feature_cols:
            val_base = float(base_features[col][t_idx])
            val_mut = float(mut_features[col][t_idx])
            delta = abs(val_base - val_mut)

            per_feature_max_deltas[col] = max(per_feature_max_deltas[col], delta)
            global_max_delta = max(global_max_delta, delta)

            if delta > tolerance:
                failed_features.append({
                    "target_index": t_idx,
                    "target_txn_id": target_txn_id,
                    "feature": col,
                    "val_base": val_base,
                    "val_mutated": val_mut,
                    "delta": delta,
                })

    all_passed = len(failed_features) == 0 and (global_max_delta <= tolerance)

    result = {
        "test_name": "feature_level_temporal_causality",
        "sample_count": len(target_indices),
        "target_indices": target_indices,
        "features_evaluated_count": len(feature_cols),
        "tolerance": tolerance,
        "global_max_delta": float(global_max_delta),
        "per_feature_max_deltas": {k: float(v) for k, v in per_feature_max_deltas.items()},
        "failed_feature_count": len(failed_features),
        "status": "PASS" if all_passed else "FAIL",
        "passed": all_passed,
    }

    if not all_passed:
        logger.error(f"Feature-Level Causality Test FAILED: global max delta = {global_max_delta}, failures: {failed_features}")
    else:
        logger.info(f"Feature-Level Causality Test PASSED: global max delta = {global_max_delta:.2e} across {len(feature_cols)} features.")

    return result


# =============================================================================
# 2. Graph-Level Leakage Invariance Test Suite (4 Tests)
# =============================================================================
def run_temporal_leakage_tests(
    graph: TemporalPaymentGraph,
    model: CausalGraphSAGE,
    eval_indices: list[int] | None = None,
    tolerance: float = 1e-12,
) -> dict[str, Any]:
    """Executes the four strict graph temporal leakage invariance tests on real graph data and model."""
    if eval_indices is None or len(eval_indices) == 0:
        n = graph.n_txns
        eval_indices = list(range(n // 4, n // 2, max(1, n // 20)))

    results: dict[str, Any] = {
        "test_suite": "graph_temporal_leakage_invariance",
        "tolerance": tolerance,
        "eval_sample_count": len(eval_indices),
        "tests": {},
        "all_passed": False,
        "global_max_delta": 0.0,
    }

    # Base predictions for evaluation indices
    base_probs = model.predict_proba(graph, eval_indices)

    # -------------------------------------------------------------------------
    # Test A: Future-edge invariance
    # -------------------------------------------------------------------------
    max_eval_idx = max(eval_indices)
    max_eval_ts = graph.timestamps[max_eval_idx]
    
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
    diff_edges = float(np.max(np.abs(base_probs - aug_probs)))
    pass_edges = bool(diff_edges <= tolerance)
    results["tests"]["future_edge_invariance"] = {
        "max_delta": diff_edges,
        "tolerance": tolerance,
        "sample_count": len(eval_indices),
        "status": "PASS" if pass_edges else "FAIL",
    }
    results["global_max_delta"] = max(results["global_max_delta"], diff_edges)

    # -------------------------------------------------------------------------
    # Test B: Future-node-feature invariance
    # -------------------------------------------------------------------------
    mutated_graph = TemporalPaymentGraph(graph.raw_df)
    mutated_graph.x_txn[max_eval_idx + 1:] = np.random.randn(*mutated_graph.x_txn[max_eval_idx + 1:].shape) * 1000.0

    mut_probs = model.predict_proba(mutated_graph, eval_indices)
    diff_feats = float(np.max(np.abs(base_probs - mut_probs)))
    pass_feats = bool(diff_feats <= tolerance)
    results["tests"]["future_node_feature_invariance"] = {
        "max_delta": diff_feats,
        "tolerance": tolerance,
        "sample_count": len(eval_indices),
        "status": "PASS" if pass_feats else "FAIL",
    }
    results["global_max_delta"] = max(results["global_max_delta"], diff_feats)

    # -------------------------------------------------------------------------
    # Test C: Future-label invariance
    # -------------------------------------------------------------------------
    label_graph = TemporalPaymentGraph(graph.raw_df)
    label_graph.is_fraud[max_eval_idx + 1:] = 1 - label_graph.is_fraud[max_eval_idx + 1:]

    lbl_probs = model.predict_proba(label_graph, eval_indices)
    diff_labels = float(np.max(np.abs(base_probs - lbl_probs)))
    pass_labels = bool(diff_labels <= tolerance)
    results["tests"]["future_label_invariance"] = {
        "max_delta": diff_labels,
        "tolerance": tolerance,
        "sample_count": len(eval_indices),
        "status": "PASS" if pass_labels else "FAIL",
    }
    results["global_max_delta"] = max(results["global_max_delta"], diff_labels)

    # -------------------------------------------------------------------------
    # Test D: Prediction-at-t invariance
    # -------------------------------------------------------------------------
    truncated_df = graph.raw_df.slice(0, max_eval_idx + 1)
    truncated_graph = TemporalPaymentGraph(truncated_df)

    trunc_probs = model.predict_proba(truncated_graph, eval_indices)
    diff_snapshot = float(np.max(np.abs(base_probs - trunc_probs)))
    pass_snapshot = bool(diff_snapshot <= tolerance)
    results["tests"]["prediction_at_t_invariance"] = {
        "max_delta": diff_snapshot,
        "tolerance": tolerance,
        "sample_count": len(eval_indices),
        "status": "PASS" if pass_snapshot else "FAIL",
    }
    results["global_max_delta"] = max(results["global_max_delta"], diff_snapshot)

    all_passed = pass_edges and pass_feats and pass_labels and pass_snapshot
    results["all_passed"] = all_passed
    results["status"] = "PASS" if all_passed else "FAIL"

    if all_passed:
        logger.info(f"All 4 graph leakage invariance tests PASSED with global max delta = {results['global_max_delta']:.2e}.")
    else:
        logger.error(f"Graph leakage invariance tests FAILED: {results}")

    return results


# =============================================================================
# 3. Temporal Split Semantics Verification
# =============================================================================
def verify_temporal_split_semantics(
    df: pl.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
) -> dict[str, Any]:
    """Verifies strict out-of-time temporal ordering and disjoint split partitions."""
    if "timestamp" in df.columns and df["timestamp"].dtype == pl.String:
        clean_df = df.with_columns(pl.col("timestamp").str.to_datetime()).sort(["timestamp", "txn_id"])
    else:
        clean_df = df.sort(["timestamp", "txn_id"])

    n = len(clean_df)
    train_end = int(train_ratio * n)
    val_end = int((train_ratio + val_ratio) * n)

    train_df = clean_df.slice(0, train_end)
    val_df = clean_df.slice(train_end, val_end - train_end)
    test_df = clean_df.slice(val_end, n - val_end)

    max_train_ts = train_df["timestamp"].max()
    min_val_ts = val_df["timestamp"].min()
    max_val_ts = val_df["timestamp"].max()
    min_test_ts = test_df["timestamp"].min()

    out_of_time_valid = bool((max_train_ts < min_val_ts) and (max_val_ts < min_test_ts))

    train_ids = set(train_df["txn_id"].to_list())
    val_ids = set(val_df["txn_id"].to_list())
    test_ids = set(test_df["txn_id"].to_list())

    disjoint_valid = (
        len(train_ids.intersection(val_ids)) == 0
        and len(val_ids.intersection(test_ids)) == 0
        and len(train_ids.intersection(test_ids)) == 0
        and (len(train_ids) + len(val_ids) + len(test_ids) == n)
    )

    all_passed = out_of_time_valid and disjoint_valid

    res = {
        "test_name": "temporal_split_semantics",
        "total_transactions": n,
        "train_count": len(train_df),
        "val_count": len(val_df),
        "test_count": len(test_df),
        "train_fraud_count": int(train_df["is_fraud"].sum()) if "is_fraud" in train_df.columns else 0,
        "val_fraud_count": int(val_df["is_fraud"].sum()) if "is_fraud" in val_df.columns else 0,
        "test_fraud_count": int(test_df["is_fraud"].sum()) if "is_fraud" in test_df.columns else 0,
        "max_train_ts": str(max_train_ts),
        "min_val_ts": str(min_val_ts),
        "max_val_ts": str(max_val_ts),
        "min_test_ts": str(min_test_ts),
        "out_of_time_valid": out_of_time_valid,
        "disjoint_splits_valid": disjoint_valid,
        "status": "PASS" if all_passed else "FAIL",
        "passed": all_passed,
    }

    if all_passed:
        logger.info("Temporal split semantics PASSED: strict out-of-time ordering & disjoint partitions.")
    else:
        logger.error(f"Temporal split semantics FAILED: {res}")

    return res


# =============================================================================
# 4. Authoritative Baseline Artifact Integrity Verification (22/22 Artifacts)
# =============================================================================
def verify_authoritative_baseline_integrity(
    baseline_dir: Path | str = Path("artifacts/run_tiny_s20260827_193f7897_40997ab"),
) -> dict[str, Any]:
    """Verifies SHA-256 cryptographic hashes of all authoritative baseline artifacts."""
    import hashlib
    import json

    baseline_path = Path(baseline_dir)
    prov_file = baseline_path / "provenance.json"
    if not prov_file.exists():
        return {
            "baseline_run_id": baseline_path.name,
            "status": "FAIL",
            "reason": f"Baseline provenance file missing: {prov_file}",
            "expected_file_count": 0,
            "actual_file_count": 0,
            "passed_files": [],
            "missing_files": [],
            "unexpected_files": [],
            "hash_mismatches": [],
        }

    with open(prov_file, "r", encoding="utf-8") as f:
        prov = json.load(f)

    expected_artifacts = prov.get("artifacts", {})
    expected_count = len(expected_artifacts)

    passed_files = []
    missing_files = []
    hash_mismatches = []

    for filename, meta in sorted(expected_artifacts.items()):
        file_path = baseline_path / filename
        if not file_path.exists():
            missing_files.append(filename)
            continue

        expected_sha = meta.get("sha256")
        h = hashlib.sha256()
        with open(file_path, "rb") as f_in:
            for chunk in iter(lambda: f_in.read(4096), b""):
                h.update(chunk)
        actual_sha = h.hexdigest()

        if expected_sha and actual_sha != expected_sha:
            hash_mismatches.append({
                "file": filename,
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
            })
        else:
            passed_files.append(filename)

    actual_files = [f.name for f in baseline_path.iterdir() if f.is_file()]
    ignored_extras = {".finalized", "provenance.json", "intent_ablation.json", "latency_benchmark.json"}
    unexpected_files = sorted([f for f in actual_files if f not in expected_artifacts and f not in ignored_extras])

    is_pass = bool(
        len(missing_files) == 0
        and len(hash_mismatches) == 0
        and len(passed_files) == expected_count
    )

    return {
        "baseline_run_id": prov.get("run_id", baseline_path.name),
        "status": "PASS" if is_pass else "FAIL",
        "expected_file_count": expected_count,
        "actual_file_count": len(passed_files),
        "passed_files": passed_files,
        "missing_files": missing_files,
        "unexpected_files": unexpected_files,
        "hash_mismatches": hash_mismatches,
    }


# =============================================================================
# 5. A/C/D Experimental Fairness Verification
# =============================================================================
def verify_acd_fairness(
    real_graph: TemporalPaymentGraph,
    shuffled_graph: TemporalPaymentGraph,
    train_indices: np.ndarray,
    val_indices: np.ndarray,
    test_indices: np.ndarray,
    world_c_families: set[str] | None = None,
) -> dict[str, Any]:
    """Verifies that Arm A, Arm C, and Arm D operate under strictly identical experimental conditions."""
    if world_c_families is None:
        world_c_families = {"cross_merchant_fanout", "agent_subversion"}

    same_txns = (real_graph.txn_ids == shuffled_graph.txn_ids)
    same_labels = np.array_equal(real_graph.is_fraud, shuffled_graph.is_fraud)
    same_timestamps = np.array_equal(real_graph.timestamps, shuffled_graph.timestamps)
    same_features = np.array_equal(real_graph.x_txn, shuffled_graph.x_txn)

    train_ts = real_graph.timestamps[train_indices]
    val_ts = real_graph.timestamps[val_indices]
    test_ts = real_graph.timestamps[test_indices]

    temporal_order = bool(np.max(train_ts) < np.min(val_ts) and np.max(val_ts) < np.min(test_ts))

    test_pop = len(test_indices)
    test_frauds = int(np.sum(real_graph.is_fraud[test_indices]))

    train_fams = {real_graph.attack_families[i] for i in train_indices}
    val_fams = {real_graph.attack_families[i] for i in val_indices}
    world_c_clean = bool(not train_fams.intersection(world_c_families) and not val_fams.intersection(world_c_families))

    topo_diff = not np.array_equal(real_graph.customer_ids, shuffled_graph.customer_ids)

    all_passed = bool(
        same_txns
        and same_labels
        and same_timestamps
        and same_features
        and temporal_order
        and world_c_clean
        and topo_diff
    )

    return {
        "all_passed": all_passed,
        "status": "PASS" if all_passed else "FAIL",
        "same_transactions": same_txns,
        "same_labels": same_labels,
        "same_timestamps": same_timestamps,
        "same_tabular_features": same_features,
        "temporal_ordering_valid": temporal_order,
        "test_sample_count": test_pop,
        "test_fraud_count": test_frauds,
        "world_c_isolation_valid": world_c_clean,
        "topology_destroyed": topo_diff,
    }


# =============================================================================
# 6. Feature Dimension Inspector
# =============================================================================
def get_exact_feature_dimensions(graph: TemporalPaymentGraph) -> dict[str, Any]:
    """Inspects and returns exact input/embedding dimensions across all arms."""
    canonical_features = list(FEATURE_NAMES)
    canonical_count = len(canonical_features)
    graph_embed_dim = 16
    fusion_dim = canonical_count + graph_embed_dim

    return {
        "canonical_feature_count": canonical_count,
        "canonical_feature_names": canonical_features,
        "graph_embedding_dim": graph_embed_dim,
        "fusion_input_dim": fusion_dim,
        "arm_a_input_dim": canonical_count,
        "arm_c_input_dim": fusion_dim,
        "arm_d_input_dim": fusion_dim,
    }

