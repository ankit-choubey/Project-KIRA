"""Real-World Sparkov Reference Ingestion & Multi-Track Evaluator.

Loads and preprocesses the Sparkov reference dataset (CC0 1.0 Universal,
kartik2112/fraud-detection) for:
- S-02: Real-World L3 Behavioral Fidelity (P1–P4)
- S-03: Real-vs-Synthetic Classifier Two-Sample Test (C2ST)
- S-04: Actual TSTR & TRTR Transfer Testing
"""

from __future__ import annotations

import csv
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

from mcdl.research.budget import BudgetContext, check_kill_switch
from mcdl.research.c2st import run_c2st_evaluation
from mcdl.research.checkpoint import atomic_write_json, atomic_write_text, save_stage_checkpoint
from mcdl.research.l3_fidelity import (
    compute_p1_interarrival,
    compute_p2_burstiness,
    compute_p4_velocity_triggers,
    parse_timestamp_to_seconds,
)
from mcdl.research.provenance import Namespace, compute_file_sha256, create_dataset_provenance
from mcdl.research.tstr import evaluate_tstr_transfer


def find_sparkov_dataset_path(search_dirs: Optional[list[Path | str]] = None) -> tuple[Optional[Path], Optional[Path]]:
    """Locates Sparkov fraudTest.csv and fraudTrain.csv files across standard local/Kaggle paths."""
    candidates = search_dirs or [
        Path("/kaggle/input/fraud-detection"),
        Path("/kaggle/input/credit-card-transactions-fraud-detection-dataset"),
        Path("data"),
        Path("../data"),
    ]
    test_path, train_path = None, None
    for d in candidates:
        d_path = Path(d)
        if not d_path.exists():
            continue
        p_test = d_path / "fraudTest.csv"
        p_train = d_path / "fraudTrain.csv"
        if p_test.exists() and test_path is None:
            test_path = p_test
        if p_train.exists() and train_path is None:
            train_path = p_train

    return test_path, train_path


def load_sparkov_transactions(
    csv_path: Path | str,
    max_rows: Optional[int] = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Loads Sparkov CSV transactions and normalizes them into aligned schemas."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Sparkov CSV not found at: {path}")

    transactions = []
    fraud_count = 0
    total_rows = 0

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            is_fraud = int(row.get("is_fraud", 0))
            if is_fraud == 1:
                fraud_count += 1

            # Parse unix_time or trans_date_trans_time
            unix_time = row.get("unix_time")
            if unix_time:
                ts = float(unix_time)
            else:
                ts = parse_timestamp_to_seconds(row.get("trans_date_trans_time", 0.0))

            amt = float(row.get("amt", row.get("amount", 0.0)))
            c_id = str(row.get("cc_num", row.get("customer_id", "")))
            m_id = str(row.get("merchant", row.get("merchant_id", "")))
            cat = str(row.get("category", ""))

            transactions.append({
                "txn_id": str(row.get("trans_num", f"real_{total_rows}")),
                "timestamp": ts,
                "amount": amt,
                "customer_id": c_id,
                "merchant_id": m_id,
                "category": cat,
                "is_fraud": is_fraud,
                "namespace": "REAL_WORLD",
            })

            if max_rows and total_rows >= max_rows:
                break

    manifest = create_dataset_provenance(
        dataset_name="Sparkov Credit Card Fraud Benchmark",
        source_url="https://kaggle.com/datasets/kartik2112/fraud-detection",
        license_type="CC0 1.0 Universal",
        namespace=Namespace.REAL_WORLD,
        sample_count=len(transactions),
        positive_count=fraud_count,
        split_method="file_split",
        file_path=path,
        extra_metadata={
            "file_name": path.name,
            "total_rows_scanned": total_rows,
        },
    )

    return transactions, manifest


def run_real_world_l3_evaluation(
    synthetic_txns: list[dict[str, Any]],
    real_txns: list[dict[str, Any]],
) -> dict[str, Any]:
    """S-02: Evaluates P1–P4 behavioral fidelity of KIRA Synthetic vs Sparkov Real."""
    syn_ts = np.array([parse_timestamp_to_seconds(t.get("timestamp", 0.0)) for t in synthetic_txns], dtype=float)
    syn_amt = np.array([float(t.get("amount", 0.0)) for t in synthetic_txns], dtype=float)

    real_ts = np.array([parse_timestamp_to_seconds(t.get("timestamp", 0.0)) for t in real_txns], dtype=float)
    real_amt = np.array([float(t.get("amount", 0.0)) for t in real_txns], dtype=float)

    # P1: Inter-event timing
    syn_p1 = compute_p1_interarrival(syn_ts)
    real_p1 = compute_p1_interarrival(real_ts)
    p1_ratio = round(syn_p1["mean_dt"] / max(1e-6, real_p1["mean_dt"]), 4)

    # P2: Burstiness
    syn_p2 = compute_p2_burstiness(syn_ts)
    real_p2 = compute_p2_burstiness(real_ts)
    # B in [-1, 1], compare distance or offset ratio
    p2_diff = round(syn_p2["burstiness_coeff"] - real_p2["burstiness_coeff"], 4)

    # P3: Shared entity density
    # Sparkov has no device_id column -> shared device is NOT_COMPARABLE
    syn_merchants: dict[str, set[str]] = {}
    for t in synthetic_txns:
        syn_merchants.setdefault(str(t.get("merchant_id", "")), set()).add(str(t.get("customer_id", "")))
    syn_shared_m = sum(1 for custs in syn_merchants.values() if len(custs) > 1)
    syn_m_ratio = round(syn_shared_m / max(1, len(syn_merchants)), 4)

    real_merchants: dict[str, set[str]] = {}
    for t in real_txns:
        real_merchants.setdefault(str(t.get("merchant_id", "")), set()).add(str(t.get("customer_id", "")))
    real_shared_m = sum(1 for custs in real_merchants.values() if len(custs) > 1)
    real_m_ratio = round(real_shared_m / max(1, len(real_merchants)), 4)

    p3_ratio = round(syn_m_ratio / max(1e-6, real_m_ratio), 4)

    # P4: Velocity triggers (amount > 1000)
    syn_p4 = compute_p4_velocity_triggers(syn_amt, syn_ts, amount_threshold=1000.0)
    real_p4 = compute_p4_velocity_triggers(real_amt, real_ts, amount_threshold=1000.0)
    p4_ratio = round(syn_p4["trigger_rate"] / max(1e-6, real_p4["trigger_rate"]), 4)

    return {
        "status": "MEASURED_REAL_COMPARISON",
        "sample_counts": {
            "synthetic": len(synthetic_txns),
            "real": len(real_txns),
        },
        "p1_interarrival": {
            "synthetic_mean_dt_sec": syn_p1["mean_dt"],
            "real_mean_dt_sec": real_p1["mean_dt"],
            "ratio": p1_ratio,
            "interpretation": f"Synthetic events occur every {syn_p1['mean_dt']:.1f}s vs real {real_p1['mean_dt']:.1f}s (ratio: {p1_ratio})",
        },
        "p2_burstiness": {
            "synthetic_burstiness": syn_p2["burstiness_coeff"],
            "real_burstiness": real_p2["burstiness_coeff"],
            "difference": p2_diff,
            "interpretation": f"Synthetic burstiness {syn_p2['burstiness_coeff']} vs real {real_p2['burstiness_coeff']}",
        },
        "p3_shared_entity_motifs": {
            "shared_device": "NOT_COMPARABLE (Sparkov reference schema contains no client device telemetry column)",
            "synthetic_shared_merchant_ratio": syn_m_ratio,
            "real_shared_merchant_ratio": real_m_ratio,
            "shared_merchant_ratio": p3_ratio,
        },
        "p4_velocity_triggers": {
            "synthetic_trigger_rate": syn_p4["trigger_rate"],
            "real_trigger_rate": real_p4["trigger_rate"],
            "ratio": p4_ratio,
            "threshold": "$1,000.00",
        },
    }


def run_real_world_c2st_evaluation(
    synthetic_txns: list[dict[str, Any]],
    real_txns: list[dict[str, Any]],
    n_bootstrap: int = 1000,
    seed: int = 20260827,
) -> dict[str, Any]:
    """S-03: Evaluates C2ST Discriminator between KIRA Synthetic (0) and Sparkov Real (1)."""
    # Build aligned feature matrix using strictly common features
    def extract_aligned_features(txns: list[dict[str, Any]]) -> np.ndarray:
        feats = []
        for t in txns:
            amt = float(t.get("amount", 0.0))
            ts = parse_timestamp_to_seconds(t.get("timestamp", 0.0))
            log_amt = math.log1p(max(0.0, amt))
            time_of_day = ts % 86400.0
            day_of_week = (ts // 86400.0) % 7.0
            feats.append([log_amt, time_of_day, day_of_week])
        return np.array(feats, dtype=float)

    syn_feats = extract_aligned_features(synthetic_txns)
    real_feats = extract_aligned_features(real_txns)

    # Subsample real if much larger than synthetic to balance discriminator
    n_samples = min(len(syn_feats), len(real_feats), 20000)
    rng = np.random.RandomState(seed)
    
    syn_sub = syn_feats[rng.choice(len(syn_feats), size=n_samples, replace=False)] if len(syn_feats) > n_samples else syn_feats
    real_sub = real_feats[rng.choice(len(real_feats), size=n_samples, replace=False)] if len(real_feats) > n_samples else real_feats

    c2st_res = run_c2st_evaluation(
        synthetic_features=syn_sub,
        real_features=real_sub,
        feature_names=["log_amount", "time_of_day_sec", "day_of_week"],
        n_bootstrap=n_bootstrap,
        seed=seed,
    )
    c2st_res["experiment_id"] = "RES-C2ST-REAL"
    c2st_res["dataset_comparison"] = "KIRA Synthetic (0) vs Sparkov Real (1)"
    return c2st_res


def run_real_world_tstr_evaluation(
    synthetic_txns: list[dict[str, Any]],
    real_test_txns: list[dict[str, Any]],
    real_train_txns: Optional[list[dict[str, Any]]] = None,
    seed: int = 20260827,
) -> dict[str, Any]:
    """S-04: Evaluates TSTR (Train Synthetic -> Test Real) & TRTR (Train Real -> Test Real)."""
    def extract_features_and_labels(txns: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
        X, y = [], []
        for t in txns:
            amt = float(t.get("amount", 0.0))
            ts = parse_timestamp_to_seconds(t.get("timestamp", 0.0))
            log_amt = math.log1p(max(0.0, amt))
            time_of_day = ts % 86400.0
            day_of_week = (ts // 86400.0) % 7.0
            X.append([log_amt, time_of_day, day_of_week])
            y.append(int(t.get("is_fraud", 0)))
        return np.array(X, dtype=float), np.array(y, dtype=int)

    syn_X, syn_y = extract_features_and_labels(synthetic_txns)
    real_test_X, real_test_y = extract_features_and_labels(real_test_txns)

    real_train_X, real_train_y = None, None
    if real_train_txns:
        # Subsample real train to reasonable size if very large (e.g. 50k)
        r_X, r_y = extract_features_and_labels(real_train_txns)
        if len(r_y) > 30000:
            rng = np.random.RandomState(seed)
            # Stratified subsample
            pos_idx = np.where(r_y == 1)[0]
            neg_idx = np.where(r_y == 0)[0]
            sampled_neg = rng.choice(neg_idx, size=min(len(neg_idx), 29000), replace=False)
            keep_idx = np.sort(np.concatenate([pos_idx, sampled_neg]))
            real_train_X = r_X[keep_idx]
            real_train_y = r_y[keep_idx]
        else:
            real_train_X, real_train_y = r_X, r_y

    tstr_res = evaluate_tstr_transfer(
        synthetic_train_X=syn_X,
        synthetic_train_y=syn_y,
        real_test_X=real_test_X,
        real_test_y=real_test_y,
        real_train_X=real_train_X,
        real_train_y=real_train_y,
        seed=seed,
    )
    tstr_res["experiment_id"] = "RES-TSTR-REAL"
    tstr_res["target_namespace"] = "REAL_WORLD (Sparkov)"
    return tstr_res
