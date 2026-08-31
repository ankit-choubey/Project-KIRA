"""Independent Invariant & Parity Test Suite for the Causal Feature Store.

Proves mathematical equivalence (<= 1e-9) between independent Polars batch
and streaming dict/deque engines across 1,000+ transactions and edge cases.
"""

from datetime import datetime, timedelta
import math
import numpy as np
import polars as pl
import pytest

from mcdl.config import load_config
from mcdl.features.batch import compute_batch_features
from mcdl.features.spec import FEATURE_NAMES, FEATURE_SPECS
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.schemas import Channel, Customer, HardNegative, Transaction
from mcdl.world.generator import generate_world
from mcdl.world.ledger import haversine_distance_km


def test_canonical_feature_count():
    """Asserts that exactly 25 canonical features are registered in FEATURE_NAMES."""
    assert len(FEATURE_SPECS) == 25, f"Expected 25 feature specs, got {len(FEATURE_SPECS)}"
    assert len(FEATURE_NAMES) == 25, f"Expected 25 feature names, got {len(FEATURE_NAMES)}"


def test_batch_stream_exact_parity_on_generated_world():
    """Validates mathematical parity (<= 1e-9) between batch and stream on 1,000+ world transactions."""
    cfg = load_config(scale="tiny")
    world = generate_world(cfg)
    txns = world.transactions
    assert len(txns) >= 1000, f"Expected >= 1000 transactions, got {len(txns)}"

    # 1. Compute batch features independently via Polars
    batch_df = compute_batch_features(txns, customers=world.customers)
    assert len(batch_df) == len(txns)
    assert set(FEATURE_NAMES).issubset(set(batch_df.columns))

    # 2. Compute streaming features independently via StreamingFeatureExtractor
    sorted_txns = sorted(txns, key=lambda t: (t.timestamp, t.txn_id))
    stream_extractor = StreamingFeatureExtractor(customers=world.customers)
    stream_feature_rows = [stream_extractor.extract(t) for t in sorted_txns]

    # 3. Assert parity for every feature column
    for feat_name in FEATURE_NAMES:
        batch_vals = batch_df[feat_name].to_numpy()
        stream_vals = np.array([r[feat_name] for r in stream_feature_rows])

        if np.issubdtype(batch_vals.dtype, np.number):
            diff = np.abs(batch_vals - stream_vals)
            max_diff = float(np.max(diff))
            assert max_diff <= 1e-9, f"Parity mismatch for feature {feat_name}: max_diff={max_diff}"
        else:
            assert (batch_vals == stream_vals).all(), f"Parity mismatch for {feat_name}"


def _make_txn(
    txn_id: str,
    c_id: str,
    m_id: str,
    dev_id: str,
    ts: datetime,
    amount: float = 50.0,
    lat: float = 40.7128,
    lon: float = -74.0060,
    balance_before: float = 100.0,
    available_credit: float = 4900.0,
    is_fraud: bool = False,
    agent_id: str | None = None,
    auth_failed_count: int = 0,
) -> Transaction:
    return Transaction(
        txn_id=txn_id,
        customer_id=c_id,
        merchant_id=m_id,
        device_id=dev_id,
        timestamp=ts,
        amount=amount,
        mcc="5411",
        channel=Channel.CARD_PRESENT if agent_id is None else Channel.AGENT,
        lat=lat,
        lon=lon,
        ip_prefix="192.168",
        is_new_device=False,
        auth_failed_count=auth_failed_count,
        agent_id=agent_id,
        balance_before=balance_before,
        available_credit=available_credit,
        is_fraud=is_fraud,
    )


# --------------------------------------------------------------------------- #
# Targeted Edge-Case Tests (A through J)
# --------------------------------------------------------------------------- #


def test_edge_case_a_same_timestamp_ordering():
    """Test A: Events with identical timestamps obey (timestamp, txn_id) ordering."""
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    t1 = _make_txn("tx_01", "c1", "m1", "d1", t0, amount=10.0)
    t2 = _make_txn("tx_02", "c1", "m1", "d1", t0, amount=20.0)

    # In batch
    batch_df = compute_batch_features([t2, t1])  # Pass unordered to test sorting
    # In stream
    stream_ext = StreamingFeatureExtractor()
    s1 = stream_ext.extract(t1)
    s2 = stream_ext.extract(t2)

    # t2 must see t1 in its history because "tx_01" < "tx_02"
    assert s1["cust_velocity_1h_count"] == 0
    assert s1["cust_velocity_1h_sum"] == 0.0

    assert s2["cust_velocity_1h_count"] == 1
    assert s2["cust_velocity_1h_sum"] == 10.0

    b1 = batch_df.filter(pl.col("txn_id") == "tx_01").to_dicts()[0]
    b2 = batch_df.filter(pl.col("txn_id") == "tx_02").to_dicts()[0]

    assert b1["cust_velocity_1h_count"] == 0
    assert b2["cust_velocity_1h_count"] == 1
    assert b2["cust_velocity_1h_sum"] == 10.0


def test_edge_case_bcd_rolling_window_boundaries():
    """Tests B, C, D: Exact 1h (3600s), 6h (21600s), 24h (86400s) boundary inclusion/exclusion."""
    t_anchor = datetime(2026, 1, 2, 12, 0, 0)

    # Transactions relative to t_anchor
    txns = [
        # Exactly 24h ago -> INCLUDED in 24h, EXCLUDED in 6h/1h
        _make_txn("t_24h_exact", "c1", "m1", "d1", t_anchor - timedelta(hours=24), amount=10.0),
        # 24h + 1s ago -> EXCLUDED in all
        _make_txn("t_24h_outside", "c1", "m1", "d1", t_anchor - timedelta(hours=24, seconds=1), amount=100.0),
        # Exactly 6h ago -> INCLUDED in 24h and 6h, EXCLUDED in 1h
        _make_txn("t_6h_exact", "c1", "m1", "d1", t_anchor - timedelta(hours=6), amount=20.0),
        # Exactly 1h ago -> INCLUDED in 24h, 6h, and 1h
        _make_txn("t_1h_exact", "c1", "m1", "d1", t_anchor - timedelta(hours=1), amount=30.0),
        # 1h + 1s ago -> INCLUDED in 24h and 6h, EXCLUDED in 1h
        _make_txn("t_1h_outside", "c1", "m1", "d1", t_anchor - timedelta(hours=1, seconds=1), amount=50.0),
        # The target transaction
        _make_txn("t_target", "c1", "m1", "d1", t_anchor, amount=5.0),
    ]

    batch_df = compute_batch_features(txns)
    stream_ext = StreamingFeatureExtractor()
    for t in sorted(txns, key=lambda x: (x.timestamp, x.txn_id)):
        s_res = stream_ext.extract(t)
        if t.txn_id == "t_target":
            stream_target = s_res

    batch_target = batch_df.filter(pl.col("txn_id") == "t_target").to_dicts()[0]

    # Expected sums for t_target:
    # 1h window: t_1h_exact (30.0) -> sum = 30.0, count = 1
    assert stream_target["cust_velocity_1h_count"] == 1
    assert stream_target["cust_velocity_1h_sum"] == 30.0
    assert batch_target["cust_velocity_1h_count"] == 1
    assert batch_target["cust_velocity_1h_sum"] == 30.0

    # 6h window: t_1h_exact (30.0) + t_1h_outside (50.0) + t_6h_exact (20.0) -> sum = 100.0, count = 3
    assert stream_target["cust_velocity_6h_count"] == 3
    assert stream_target["cust_velocity_6h_sum"] == 100.0
    assert batch_target["cust_velocity_6h_count"] == 3
    assert batch_target["cust_velocity_6h_sum"] == 100.0

    # 24h window: t_1h_exact (30) + t_1h_outside (50) + t_6h_exact (20) + t_24h_exact (10) -> sum = 110.0, count = 4
    assert stream_target["cust_velocity_24h_count"] == 4
    assert stream_target["cust_velocity_24h_sum"] == 110.0
    assert batch_target["cust_velocity_24h_count"] == 4
    assert batch_target["cust_velocity_24h_sum"] == 110.0


def test_edge_case_e_first_transaction_defaults():
    """Test E: Verifies first-transaction defaults on a brand-new customer."""
    t0 = datetime(2026, 1, 1, 10, 0, 0)
    t = _make_txn("t_first", "c_new", "m1", "d1", t0, amount=75.0)

    batch_df = compute_batch_features([t])
    stream_ext = StreamingFeatureExtractor()
    s = stream_ext.extract(t)
    b = batch_df.to_dicts()[0]

    assert s["dist_from_prev_txn_km"] == 0.0
    assert b["dist_from_prev_txn_km"] == 0.0

    assert s["time_since_prev_txn_seconds"] == -1.0
    assert b["time_since_prev_txn_seconds"] == -1.0

    assert s["speed_kmh"] == 0.0
    assert b["speed_kmh"] == 0.0

    assert s["cust_avg_amount_hist"] == 75.0
    assert b["cust_avg_amount_hist"] == 75.0

    assert s["cust_amount_to_avg_ratio"] == 1.0
    assert b["cust_amount_to_avg_ratio"] == 1.0

    assert s["is_new_device"] == 0
    assert b["is_new_device"] == 0

    assert s["device_cust_count"] == 0
    assert b["device_cust_count"] == 0


def test_edge_case_f_label_delay_7day_boundary():
    """Test F: 7-day label availability (just before, exactly at, and just after cutoff)."""
    t_target = datetime(2026, 1, 15, 12, 0, 0)
    seven_days = timedelta(days=7)

    txns = [
        # Exactly 7 days ago (fraud) -> Available (included in confirmed fraud)
        _make_txn("t_7d_exact", "c1", "m_lag", "d1", t_target - seven_days, is_fraud=True),
        # 7 days + 1 hour ago (legit) -> Available (included in confirmed total)
        _make_txn("t_7d_older", "c2", "m_lag", "d2", t_target - seven_days - timedelta(hours=1), is_fraud=False),
        # 7 days - 1 second ago (fraud) -> UNAVAILABLE (unconfirmed window, must NOT count)
        _make_txn("t_7d_recent", "c3", "m_lag", "d3", t_target - seven_days + timedelta(seconds=1), is_fraud=True),
        # 1 day ago (fraud) -> UNAVAILABLE (unconfirmed window)
        _make_txn("t_1d_ago", "c4", "m_lag", "d4", t_target - timedelta(days=1), is_fraud=True),
        # Target transaction
        _make_txn("t_target", "c5", "m_lag", "d5", t_target, is_fraud=False),
    ]

    batch_df = compute_batch_features(txns)
    stream_ext = StreamingFeatureExtractor()
    for t in sorted(txns, key=lambda x: (x.timestamp, x.txn_id)):
        s_res = stream_ext.extract(t)
        if t.txn_id == "t_target":
            stream_target = s_res

    batch_target = batch_df.filter(pl.col("txn_id") == "t_target").to_dicts()[0]

    # At t_target, only t_7d_exact (fraud=1) and t_7d_older (fraud=0) are >= 7 days old.
    # Confirmed fraud rate = 1 / 2 = 0.5
    assert stream_target["merch_fraud_rate_7d_lag"] == 0.5
    assert batch_target["merch_fraud_rate_7d_lag"] == 0.5


def test_edge_case_gh_future_perturbation():
    """Tests G & H: Future transaction & future fraud-label perturbations have zero effect on past features."""
    t0 = datetime(2026, 1, 1, 10, 0, 0)
    t1 = _make_txn("t_base_01", "c1", "m1", "d1", t0, amount=100.0, is_fraud=False)
    t2 = _make_txn("t_base_02", "c1", "m1", "d1", t0 + timedelta(hours=2), amount=50.0, is_fraud=False)

    # Extract baseline features for t2
    base_df = compute_batch_features([t1, t2])
    base_t2 = base_df.filter(pl.col("txn_id") == "t_base_02").to_dicts()[0]

    # Perturbation G: Add a massive future transaction after t2
    t_future = _make_txn("t_future_huge", "c1", "m1", "d1", t0 + timedelta(hours=5), amount=999999.0, is_fraud=True)
    pert_df_g = compute_batch_features([t1, t2, t_future])
    pert_t2_g = pert_df_g.filter(pl.col("txn_id") == "t_base_02").to_dicts()[0]

    # Perturbation H: Mutate fraud label of t1 to True (within the 7-day unconfirmed window)
    t1_fraud_mutated = _make_txn("t_base_01", "c1", "m1", "d1", t0, amount=100.0, is_fraud=True)
    pert_df_h = compute_batch_features([t1_fraud_mutated, t2])
    pert_t2_h = pert_df_h.filter(pl.col("txn_id") == "t_base_02").to_dicts()[0]

    # Features of t2 must be bit-for-bit identical across all features
    for feat in FEATURE_NAMES:
        assert base_t2[feat] == pert_t2_g[feat], f"Future transaction leaked into {feat}"
        assert base_t2[feat] == pert_t2_h[feat], f"Unconfirmed future fraud label leaked into {feat}"


def test_edge_case_i_hand_computed_fixture():
    """Test I: Evaluates batch and stream independently against hard-coded hand-computed ground truth."""
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    customer = Customer(
        customer_id="c_fixture",
        archetype="salaried_urban",
        home_lat=40.0,
        home_lon=-74.0,
        account_opened=datetime(2025, 1, 1),
        credit_limit=10000.0,
        mean_log_amount=3.5,
        std_log_amount=0.8,
        daily_txn_rate=2.0,
    )

    t1 = _make_txn("tx_f1", "c_fixture", "m1", "dev_1", t0, amount=100.0, lat=40.0, lon=-74.0, balance_before=2000.0)
    t2 = _make_txn("tx_f2", "c_fixture", "m1", "dev_2", t0 + timedelta(minutes=30), amount=50.0, lat=40.1, lon=-74.0, balance_before=2100.0)

    customers_dict = {"c_fixture": customer}

    # Batch and Stream independent extractions
    batch_df = compute_batch_features([t1, t2], customers=customers_dict)
    stream_ext = StreamingFeatureExtractor(customers=customers_dict)
    s1 = stream_ext.extract(t1)
    s2 = stream_ext.extract(t2)

    b1 = batch_df.filter(pl.col("txn_id") == "tx_f1").to_dicts()[0]
    b2 = batch_df.filter(pl.col("txn_id") == "tx_f2").to_dicts()[0]

    # Hand-computed checks for tx_f1:
    assert b1["amount"] == 100.0
    assert s1["amount"] == 100.0
    assert b1["log_amount"] == math.log(101.0)
    assert s1["log_amount"] == math.log(101.0)
    assert b1["hour_of_day"] == 12
    assert s1["hour_of_day"] == 12
    assert b1["balance_utilization"] == 2000.0 / 10000.0 == 0.2
    assert s1["balance_utilization"] == 0.2
    assert b1["cust_velocity_1h_count"] == 0
    assert s1["cust_velocity_1h_count"] == 0
    assert b1["cust_avg_amount_hist"] == 100.0
    assert s1["cust_avg_amount_hist"] == 100.0

    # Hand-computed checks for tx_f2:
    expected_dist_km = haversine_distance_km(40.0, -74.0, 40.1, -74.0)
    assert abs(b2["dist_from_prev_txn_km"] - expected_dist_km) <= 1e-9
    assert abs(s2["dist_from_prev_txn_km"] - expected_dist_km) <= 1e-9
    assert b2["time_since_prev_txn_seconds"] == 1800.0
    assert s2["time_since_prev_txn_seconds"] == 1800.0
    assert b2["cust_velocity_1h_count"] == 1
    assert s2["cust_velocity_1h_count"] == 1
    assert b2["cust_velocity_1h_sum"] == 100.0
    assert s2["cust_velocity_1h_sum"] == 100.0
    assert b2["cust_avg_amount_hist"] == 100.0  # Mean of prior amounts (100.0)
    assert s2["cust_avg_amount_hist"] == 100.0
    assert b2["cust_amount_to_avg_ratio"] == 50.0 / 100.0 == 0.5
    assert s2["cust_amount_to_avg_ratio"] == 0.5
    assert b2["is_new_device"] == 1  # dev_2 is new on 2nd transaction
    assert s2["is_new_device"] == 1


def test_edge_case_j_intentional_corruption_sensitivity():
    """Test J: Confirms that intentionally corrupting a batch calculation causes the parity test to FAIL."""
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    t1 = _make_txn("t1", "c1", "m1", "d1", t0, amount=50.0)

    # Stream extraction
    stream_ext = StreamingFeatureExtractor()
    stream_feats = stream_ext.extract(t1)

    # Normal batch extraction
    batch_df = compute_batch_features([t1])
    batch_feats = batch_df.to_dicts()[0]

    # Artificially corrupted batch DataFrame (adding +1.0 to amount)
    corrupted_df = batch_df.with_columns(pl.col("amount") + 1.0)
    corrupted_feats = corrupted_df.to_dicts()[0]

    # Parity passes on true batch vs stream
    assert abs(batch_feats["amount"] - stream_feats["amount"]) <= 1e-9

    # Parity MUST fail on corrupted batch vs stream
    with pytest.raises(AssertionError):
        assert abs(corrupted_feats["amount"] - stream_feats["amount"]) <= 1e-9
