"""Unit tests for the Causal Feature Store specification contract."""

from datetime import datetime, timedelta
import pytest
import polars as pl

from mcdl.features.spec import (
    FEATURE_NAMES,
    FEATURE_SPECS,
    FEATURE_NAME_TO_SPEC,
    FeatureSpec,
)


def test_feature_spec_registry_integrity():
    """Validates that all feature specs have unique names, valid groups, and dtypes."""
    assert len(FEATURE_SPECS) > 0
    assert len(FEATURE_NAMES) == len(FEATURE_SPECS)
    assert len(set(FEATURE_NAMES)) == len(FEATURE_NAMES), "Duplicate feature names found"

    for spec in FEATURE_SPECS:
        assert isinstance(spec.name, str) and len(spec.name) > 0
        assert spec.group in ["transaction", "temporal", "spatial", "velocity", "behavioral", "entity", "relational", "delegation"]
        assert isinstance(spec.dtype, (pl.DataType, type))
        assert len(spec.inputs) > 0
        assert len(spec.mathematical_formula) > 0
        assert len(spec.causal_boundary) > 0


def test_lexicographic_causal_ordering():
    """Tests that (timestamp, txn_id) defines a strict total ordering."""
    ts0 = datetime(2026, 1, 1, 12, 0, 0)
    ts1 = datetime(2026, 1, 1, 12, 0, 1)

    # Key function representing the ordering
    def sort_key(event: tuple[datetime, str]) -> tuple[datetime, str]:
        return (event[0], event[1])

    # Distinct timestamps
    e_early = (ts0, "tx_99")
    e_late = (ts1, "tx_01")
    assert sort_key(e_early) < sort_key(e_late)

    # Same timestamp, different txn_ids
    e_same_ts_1 = (ts0, "tx_01")
    e_same_ts_2 = (ts0, "tx_02")
    assert sort_key(e_same_ts_1) < sort_key(e_same_ts_2)

    # Equality only when both timestamp and txn_id match
    e_same_ts_1_dup = (ts0, "tx_01")
    assert sort_key(e_same_ts_1) == sort_key(e_same_ts_1_dup)


def test_rolling_window_boundary_filter():
    """Tests the exact mathematical boundary for sliding time windows W_delta."""
    t_curr = datetime(2026, 1, 2, 12, 0, 0)
    curr_id = "tx_current"
    delta_1h = timedelta(hours=1)

    # Define candidate events (timestamp, txn_id, amount)
    candidates = [
        # Exactly at boundary t_curr - 1h (3600s prior) -> INCLUDED
        (t_curr - timedelta(seconds=3600), "tx_00", 10.0, True),
        # 1 second outside boundary (3601s prior) -> EXCLUDED
        (t_curr - timedelta(seconds=3601), "tx_past", 20.0, False),
        # Inside window (1800s prior) -> INCLUDED
        (t_curr - timedelta(seconds=1800), "tx_mid", 30.0, True),
        # Same timestamp, earlier txn_id -> INCLUDED
        (t_curr, "tx_a_earlier", 40.0, True),
        # Current transaction itself -> EXCLUDED (no self-leakage)
        (t_curr, "tx_current", 50.0, False),
        # Same timestamp, later txn_id -> EXCLUDED
        (t_curr, "tx_z_later", 60.0, False),
        # Future timestamp -> EXCLUDED
        (t_curr + timedelta(seconds=1), "tx_future", 70.0, False),
    ]

    def in_window(ts: datetime, txn_id: str) -> bool:
        # Causal precedence
        is_prior = (ts < t_curr) or (ts == t_curr and txn_id < curr_id)
        # Window lower bound
        is_in_time = (t_curr - delta_1h) <= ts <= t_curr
        return is_prior and is_in_time

    for ts, txn_id, amt, expected_inclusion in candidates:
        actual = in_window(ts, txn_id)
        assert actual == expected_inclusion, f"Failed for ({ts}, {txn_id}): got {actual}, expected {expected_inclusion}"


def test_label_delay_7day_boundary():
    """Tests exact 7-day (604,800s) chargeback availability boundary."""
    t_curr = datetime(2026, 1, 10, 12, 0, 0)
    seven_days = timedelta(days=7)  # exactly 604,800 seconds

    # Exact boundary timestamps
    ts_exactly_7d = t_curr - seven_days
    ts_7d_minus_1s = ts_exactly_7d - timedelta(seconds=1)  # 7 days and 1 sec ago (older)
    ts_7d_plus_1s = ts_exactly_7d + timedelta(seconds=1)   # 6 days 23h 59m 59s ago (too recent)
    ts_current = t_curr

    def is_label_available(ts: datetime) -> bool:
        # Confirmed label cutoff: event must have occurred >= 7 days prior
        return ts <= (t_curr - seven_days)

    # 1. Just before 7 days (older than 7 days) -> Available
    assert is_label_available(ts_7d_minus_1s) is True

    # 2. Exactly 7 days (inclusive boundary) -> Available
    assert is_label_available(ts_exactly_7d) is True

    # 3. Just after 7 days (6d 23h 59m 59s - within unconfirmed window) -> Unavailable
    assert is_label_available(ts_7d_plus_1s) is False

    # 4. Current transaction -> Unavailable
    assert is_label_available(ts_current) is False


def test_first_event_defaults_coverage():
    """Verifies that all historical/stateful features define default semantics."""
    for spec in FEATURE_SPECS:
        if not spec.includes_current_txn:
            # Historical feature must define a non-null default
            assert spec.first_event_default is not None, f"Feature {spec.name} missing first_event_default"
