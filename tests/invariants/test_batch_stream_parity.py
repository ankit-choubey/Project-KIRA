"""Invariant tests for Batch/Stream Parity and Causal Non-Future-Reading."""

from datetime import datetime, timedelta
import numpy as np
import polars as pl
import pytest

from mcdl.config import load_config
from mcdl.features.batch import compute_batch_features
from mcdl.features.spec import FEATURE_NAMES
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.world.generator import generate_world


def test_batch_stream_exact_parity():
    """Asserts that batch and streaming feature pipelines produce identical values <= 1e-9."""
    cfg = load_config(scale="tiny")
    world = generate_world(cfg)
    txns = world.transactions
    assert len(txns) >= 1000, f"Expected >= 1000 transactions, got {len(txns)}"

    # 1. Compute batch features
    batch_df = compute_batch_features(txns, customers=world.customers)
    assert len(batch_df) == len(txns)

    # 2. Compute streaming features sequentially on causally sorted transactions
    sorted_txns = sorted(txns, key=lambda t: (t.timestamp, t.txn_id))
    stream_extractor = StreamingFeatureExtractor(customers=world.customers)
    stream_feature_rows = []
    for t in sorted_txns:
        stream_feature_rows.append(stream_extractor.extract(t))

    # 3. Compare every feature column across all transactions
    for feat_name in FEATURE_NAMES:
        batch_vals = batch_df[feat_name].to_numpy()
        stream_vals = np.array([r[feat_name] for r in stream_feature_rows])

        if np.issubdtype(batch_vals.dtype, np.number):
            diff = np.abs(batch_vals - stream_vals)
            max_diff = float(np.max(diff))
            assert max_diff <= 1e-9, f"Parity mismatch for feature {feat_name}: max_diff={max_diff}"
        else:
            assert (batch_vals == stream_vals).all(), f"Categorical parity mismatch for {feat_name}"


def test_causal_no_future_reads():
    """Asserts that modifying or inserting future events (t > t_i) has ZERO effect on features at t_i."""
    cfg = load_config(scale="tiny")
    world = generate_world(cfg)
    sorted_txns = sorted(world.transactions, key=lambda t: (t.timestamp, t.txn_id))

    mid_idx = len(sorted_txns) // 2
    target_txn = sorted_txns[mid_idx]

    # Baseline features at target_txn
    ext_base = StreamingFeatureExtractor(customers=world.customers)
    base_features = {}
    for t in sorted_txns[: mid_idx + 1]:
        f = ext_base.extract(t)
        if t.txn_id == target_txn.txn_id:
            base_features = f

    # Perturbed world: insert huge future anomalies after target_txn
    future_perturbed_txns = sorted_txns[: mid_idx + 1].copy()
    # Add a massive future transaction
    future_ts = target_txn.timestamp + timedelta(hours=2)
    from mcdl.schemas import Transaction
    fake_future_txn = Transaction(
        txn_id="tx_future_anomaly",
        customer_id=target_txn.customer_id,
        merchant_id=target_txn.merchant_id,
        device_id=target_txn.device_id,
        timestamp=future_ts,
        amount=999999.0,
        mcc="5411",
        channel="card_present",
        lat=target_txn.lat,
        lon=target_txn.lon,
        ip_prefix="10.0",
        is_new_device=True,
        auth_failed_count=5,
        balance_before=100.0,
        available_credit=5000.0,
        is_fraud=True,
    )
    future_perturbed_txns.append(fake_future_txn)

    # Compute batch features on perturbed history
    perturbed_df = compute_batch_features(future_perturbed_txns, customers=world.customers)
    target_row_perturbed = perturbed_df.filter(pl.col("txn_id") == target_txn.txn_id).to_dicts()[0]

    # Assert exact match with baseline
    for feat_name in FEATURE_NAMES:
        base_val = base_features[feat_name]
        pert_val = target_row_perturbed[feat_name]
        if isinstance(base_val, float):
            assert abs(base_val - pert_val) <= 1e-9, f"Causality leak detected in {feat_name}: {base_val} vs {pert_val}"
        else:
            assert base_val == pert_val, f"Causality leak detected in {feat_name}: {base_val} vs {pert_val}"
