"""Causal Feature Store — Single Source of Truth Specification.

Freezes mathematical definitions, causal ordering, time-window boundaries,
label-delay availability, and default/first-history semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Literal
import polars as pl

from mcdl.schemas import Transaction


# --------------------------------------------------------------------------- #
# Causal Ordering Contract
# --------------------------------------------------------------------------- #
# Deterministic causal order is strictly (timestamp, txn_id) ascending.
# For any two transactions A and B:
#   A < B  <=>  (A.timestamp < B.timestamp) or (A.timestamp == B.timestamp and A.txn_id < B.txn_id)
# 
# A transaction T_i can observe history H(T_i) = { T_j | T_j < T_i in causal order }.
# T_i NEVER observes itself in historical aggregations (no self-leakage).
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    group: Literal["transaction", "temporal", "spatial", "velocity", "behavioral", "entity", "relational", "delegation"]
    dtype: pl.DataType
    description: str
    mathematical_formula: str
    inputs: list[str]
    state_required: str
    causal_boundary: str
    first_event_default: Any
    includes_current_txn: bool
    requires_labels: bool


# --------------------------------------------------------------------------- #
# Canonical Feature Registry
# --------------------------------------------------------------------------- #

FEATURE_SPECS: list[FeatureSpec] = [
    # --- 1. Transaction & Spatial ------------------------------------------ #
    FeatureSpec(
        name="amount",
        group="transaction",
        dtype=pl.Float64,
        description="Raw transaction amount in USD",
        mathematical_formula="T_i.amount",
        inputs=["amount"],
        state_required="None (stateless)",
        causal_boundary="Current event T_i",
        first_event_default=0.0,
        includes_current_txn=True,
        requires_labels=False,
    ),
    FeatureSpec(
        name="log_amount",
        group="transaction",
        dtype=pl.Float64,
        description="Natural logarithm of (1 + amount)",
        mathematical_formula="ln(1.0 + T_i.amount)",
        inputs=["amount"],
        state_required="None (stateless)",
        causal_boundary="Current event T_i",
        first_event_default=0.0,
        includes_current_txn=True,
        requires_labels=False,
    ),
    FeatureSpec(
        name="hour_of_day",
        group="temporal",
        dtype=pl.Int64,
        description="Hour of transaction in UTC (0..23)",
        mathematical_formula="T_i.timestamp.hour",
        inputs=["timestamp"],
        state_required="None (stateless)",
        causal_boundary="Current event T_i",
        first_event_default=0,
        includes_current_txn=True,
        requires_labels=False,
    ),
    FeatureSpec(
        name="day_of_week",
        group="temporal",
        dtype=pl.Int64,
        description="Day of week (0=Monday, 6=Sunday)",
        mathematical_formula="T_i.timestamp.weekday()",
        inputs=["timestamp"],
        state_required="None (stateless)",
        causal_boundary="Current event T_i",
        first_event_default=0,
        includes_current_txn=True,
        requires_labels=False,
    ),
    FeatureSpec(
        name="is_weekend",
        group="temporal",
        dtype=pl.Int64,
        description="Binary flag for Saturday/Sunday (1 if weekday >= 5 else 0)",
        mathematical_formula="1 if T_i.timestamp.weekday() >= 5 else 0",
        inputs=["timestamp"],
        state_required="None (stateless)",
        causal_boundary="Current event T_i",
        first_event_default=0,
        includes_current_txn=True,
        requires_labels=False,
    ),
    FeatureSpec(
        name="dist_from_home_km",
        group="spatial",
        dtype=pl.Float64,
        description="Haversine distance between customer home and transaction coordinates",
        mathematical_formula="haversine(C.home_lat, C.home_lon, T_i.lat, T_i.lon)",
        inputs=["lat", "lon", "customer_id"],
        state_required="Customer static profile (home_lat, home_lon)",
        causal_boundary="Current event T_i + Customer creation time",
        first_event_default=0.0,
        includes_current_txn=True,
        requires_labels=False,
    ),
    FeatureSpec(
        name="dist_from_prev_txn_km",
        group="spatial",
        dtype=pl.Float64,
        description="Haversine distance from previous customer transaction in causal order",
        mathematical_formula="haversine(T_prev.lat, T_prev.lon, T_i.lat, T_i.lon) if T_prev exists else 0.0",
        inputs=["lat", "lon", "customer_id", "timestamp", "txn_id"],
        state_required="Customer previous transaction location (T_prev.lat, T_prev.lon)",
        causal_boundary="T_prev strictly < T_i",
        first_event_default=0.0,
        includes_current_txn=False,
        requires_labels=False,
    ),
    FeatureSpec(
        name="time_since_prev_txn_seconds",
        group="spatial",
        dtype=pl.Float64,
        description="Elapsed seconds since previous customer transaction in causal order",
        mathematical_formula="(T_i.timestamp - T_prev.timestamp).total_seconds() if T_prev exists else -1.0",
        inputs=["customer_id", "timestamp", "txn_id"],
        state_required="Customer previous transaction timestamp",
        causal_boundary="T_prev strictly < T_i",
        first_event_default=-1.0,
        includes_current_txn=False,
        requires_labels=False,
    ),
    FeatureSpec(
        name="speed_kmh",
        group="spatial",
        dtype=pl.Float64,
        description="Implied travel speed in km/h from previous transaction",
        mathematical_formula="(dist_from_prev_txn_km / (time_since_prev_txn_seconds / 3600.0)) if time > 0 else 0.0",
        inputs=["lat", "lon", "customer_id", "timestamp", "txn_id"],
        state_required="Customer previous transaction location and timestamp",
        causal_boundary="T_prev strictly < T_i",
        first_event_default=0.0,
        includes_current_txn=False,
        requires_labels=False,
    ),

    # --- 2. Customer Rolling Velocity Windows (Strictly Prior Events) ------ #
    # Window definition: W_delta(T_i) = { T_j | T_j < T_i and (t_i - delta) <= t_j <= t_i }
    FeatureSpec(
        name="cust_velocity_1h_count",
        group="velocity",
        dtype=pl.Int64,
        description="Count of customer transactions in trailing 1h window strictly prior to T_i",
        mathematical_formula="| { T_j in C | T_j < T_i and (t_i - 3600s) <= t_j <= t_i } |",
        inputs=["customer_id", "timestamp", "txn_id"],
        state_required="Customer event queue for trailing 1h",
        causal_boundary="T_j strictly < T_i",
        first_event_default=0,
        includes_current_txn=False,
        requires_labels=False,
    ),
    FeatureSpec(
        name="cust_velocity_1h_sum",
        group="velocity",
        dtype=pl.Float64,
        description="Sum of customer transaction amounts in trailing 1h window strictly prior to T_i",
        mathematical_formula="sum( T_j.amount for T_j in C where T_j < T_i and (t_i - 3600s) <= t_j <= t_i )",
        inputs=["customer_id", "amount", "timestamp", "txn_id"],
        state_required="Customer event amount queue for trailing 1h",
        causal_boundary="T_j strictly < T_i",
        first_event_default=0.0,
        includes_current_txn=False,
        requires_labels=False,
    ),
    FeatureSpec(
        name="cust_velocity_6h_count",
        group="velocity",
        dtype=pl.Int64,
        description="Count of customer transactions in trailing 6h window strictly prior to T_i",
        mathematical_formula="| { T_j in C | T_j < T_i and (t_i - 21600s) <= t_j <= t_i } |",
        inputs=["customer_id", "timestamp", "txn_id"],
        state_required="Customer event queue for trailing 6h",
        causal_boundary="T_j strictly < T_i",
        first_event_default=0,
        includes_current_txn=False,
        requires_labels=False,
    ),
    FeatureSpec(
        name="cust_velocity_6h_sum",
        group="velocity",
        dtype=pl.Float64,
        description="Sum of customer transaction amounts in trailing 6h window strictly prior to T_i",
        mathematical_formula="sum( T_j.amount for T_j in C where T_j < T_i and (t_i - 21600s) <= t_j <= t_i )",
        inputs=["customer_id", "amount", "timestamp", "txn_id"],
        state_required="Customer event amount queue for trailing 6h",
        causal_boundary="T_j strictly < T_i",
        first_event_default=0.0,
        includes_current_txn=False,
        requires_labels=False,
    ),
    FeatureSpec(
        name="cust_velocity_24h_count",
        group="velocity",
        dtype=pl.Int64,
        description="Count of customer transactions in trailing 24h window strictly prior to T_i",
        mathematical_formula="| { T_j in C | T_j < T_i and (t_i - 86400s) <= t_j <= t_i } |",
        inputs=["customer_id", "timestamp", "txn_id"],
        state_required="Customer event queue for trailing 24h",
        causal_boundary="T_j strictly < T_i",
        first_event_default=0,
        includes_current_txn=False,
        requires_labels=False,
    ),
    FeatureSpec(
        name="cust_velocity_24h_sum",
        group="velocity",
        dtype=pl.Float64,
        description="Sum of customer transaction amounts in trailing 24h window strictly prior to T_i",
        mathematical_formula="sum( T_j.amount for T_j in C where T_j < T_i and (t_i - 86400s) <= t_j <= t_i )",
        inputs=["customer_id", "amount", "timestamp", "txn_id"],
        state_required="Customer event amount queue for trailing 24h",
        causal_boundary="T_j strictly < T_i",
        first_event_default=0.0,
        includes_current_txn=False,
        requires_labels=False,
    ),

    # --- 3. Merchant Rolling Velocity Windows ------------------------------ #
    FeatureSpec(
        name="merch_velocity_1h_count",
        group="velocity",
        dtype=pl.Int64,
        description="Count of merchant transactions in trailing 1h window strictly prior to T_i",
        mathematical_formula="| { T_j in M | T_j < T_i and (t_i - 3600s) <= t_j <= t_i } |",
        inputs=["merchant_id", "timestamp", "txn_id"],
        state_required="Merchant event queue for trailing 1h",
        causal_boundary="T_j strictly < T_i",
        first_event_default=0,
        includes_current_txn=False,
        requires_labels=False,
    ),
    FeatureSpec(
        name="merch_velocity_24h_count",
        group="velocity",
        dtype=pl.Int64,
        description="Count of merchant transactions in trailing 24h window strictly prior to T_i",
        mathematical_formula="| { T_j in M | T_j < T_i and (t_i - 86400s) <= t_j <= t_i } |",
        inputs=["merchant_id", "timestamp", "txn_id"],
        state_required="Merchant event queue for trailing 24h",
        causal_boundary="T_j strictly < T_i",
        first_event_default=0,
        includes_current_txn=False,
        requires_labels=False,
    ),

    # --- 4. Behavioral & Cumulative Historical Statistics ------------------ #
    FeatureSpec(
        name="cust_avg_amount_hist",
        group="behavioral",
        dtype=pl.Float64,
        description="Cumulative average amount of all customer transactions strictly prior to T_i",
        mathematical_formula="mean( T_j.amount for T_j in C where T_j < T_i ) if history exists else T_i.amount",
        inputs=["customer_id", "amount", "timestamp", "txn_id"],
        state_required="Customer cumulative amount sum and count strictly prior to T_i",
        causal_boundary="T_j strictly < T_i",
        first_event_default="T_i.amount",
        includes_current_txn=False,
        requires_labels=False,
    ),
    FeatureSpec(
        name="cust_amount_to_avg_ratio",
        group="behavioral",
        dtype=pl.Float64,
        description="Ratio of current amount to customer historical average amount",
        mathematical_formula="T_i.amount / cust_avg_amount_hist",
        inputs=["amount", "customer_id", "timestamp", "txn_id"],
        state_required="Customer historical mean amount strictly prior to T_i",
        causal_boundary="T_j strictly < T_i (evaluating T_i.amount)",
        first_event_default=1.0,
        includes_current_txn=False,  # History calculation excludes current txn
        requires_labels=False,
    ),
    FeatureSpec(
        name="balance_utilization",
        group="behavioral",
        dtype=pl.Float64,
        description="Fraction of customer credit limit utilized at event time",
        mathematical_formula="T_i.balance_before / C.credit_limit",
        inputs=["balance_before", "customer_id"],
        state_required="Customer credit_limit",
        causal_boundary="Current event T_i (observable balance_before)",
        first_event_default=0.0,
        includes_current_txn=True,
        requires_labels=False,
    ),

    # --- 5. Entity & Graph Features ---------------------------------------- #
    FeatureSpec(
        name="is_new_device",
        group="entity",
        dtype=pl.Int64,
        description="Binary flag (1 if customer has never used this device_id prior to T_i, else 0)",
        mathematical_formula="1 if device_id not in C.known_devices_prior_to_t else 0",
        inputs=["customer_id", "device_id", "timestamp", "txn_id"],
        state_required="Set of devices used by customer strictly prior to T_i",
        causal_boundary="T_j strictly < T_i",
        first_event_default=0,
        includes_current_txn=False,
        requires_labels=False,
    ),
    FeatureSpec(
        name="device_cust_count",
        group="relational",
        dtype=pl.Int64,
        description="Count of distinct customers who used this device strictly prior to T_i",
        mathematical_formula="| { T_j.customer_id | T_j.device_id == T_i.device_id and T_j < T_i } |",
        inputs=["device_id", "customer_id", "timestamp", "txn_id"],
        state_required="Set of customers per device strictly prior to T_i",
        causal_boundary="T_j strictly < T_i",
        first_event_default=0,
        includes_current_txn=False,
        requires_labels=False,
    ),
    FeatureSpec(
        name="auth_failed_count",
        group="entity",
        dtype=pl.Int64,
        description="Number of failed authentication attempts reported on current transaction",
        mathematical_formula="T_i.auth_failed_count",
        inputs=["auth_failed_count"],
        state_required="None (stateless)",
        causal_boundary="Current event T_i",
        first_event_default=0,
        includes_current_txn=True,
        requires_labels=False,
    ),

    # --- 6. Agent Delegation Features -------------------------------------- #
    FeatureSpec(
        name="is_agent_initiated",
        group="delegation",
        dtype=pl.Int64,
        description="Binary flag: 1 if payment was initiated by an autonomous agent, else 0",
        mathematical_formula="1 if T_i.agent_id is not None else 0",
        inputs=["agent_id"],
        state_required="None (stateless)",
        causal_boundary="Current event T_i",
        first_event_default=0,
        includes_current_txn=True,
        requires_labels=False,
    ),

    # --- 7. Label-Delay Realism (7-day Lag) --------------------------------- #
    # Strict 7-day chargeback availability constraint:
    # A label for transaction T_j at timestamp t_j is CONFIRMED and readable at t_i
    # if and only if t_j <= t_i - 7 days (t_j <= t_i - 604,800 seconds).
    # Any transaction with t_i - 7d < t_j <= t_i has UNCONFIRMED label status (treated as non-fraudulent / unknown).
    FeatureSpec(
        name="merch_fraud_rate_7d_lag",
        group="relational",
        dtype=pl.Float64,
        description="Historical fraud rate at this merchant using only labels confirmed >= 7 days prior to T_i",
        mathematical_formula=(
            "sum(T_j.is_fraud for T_j in M where t_j <= t_i - 7d) / "
            "count(T_j for T_j in M where t_j <= t_i - 7d) if count > 0 else 0.0"
        ),
        inputs=["merchant_id", "timestamp", "is_fraud"],
        state_required="Confirmed fraud labels per merchant strictly older than 7 days (604,800s)",
        causal_boundary="t_j <= t_i - 7 days (inclusive 7-day cutoff)",
        first_event_default=0.0,
        includes_current_txn=False,
        requires_labels=True,
    ),
]

FEATURE_NAMES: list[str] = [spec.name for spec in FEATURE_SPECS]
FEATURE_NAME_TO_SPEC: dict[str, FeatureSpec] = {spec.name: spec for spec in FEATURE_SPECS}


def get_feature_schema() -> dict[str, Any]:
    """Returns the canonical feature store schema specification with dynamic feature count."""
    return {
        "schema_version": "0.1.0",
        "feature_count": len(FEATURE_SPECS),
        "causal_ordering": "strictly (timestamp, txn_id) ascending",
        "label_delay_lag_seconds": 604800,
        "features": [
            {
                "name": spec.name,
                "group": spec.group,
                "dtype": str(spec.dtype),
                "description": spec.description,
                "mathematical_formula": spec.mathematical_formula,
                "inputs": spec.inputs,
                "state_required": spec.state_required,
                "causal_boundary": spec.causal_boundary,
                "first_event_default": str(spec.first_event_default),
                "includes_current_txn": spec.includes_current_txn,
                "requires_labels": spec.requires_labels,
            }
            for spec in FEATURE_SPECS
        ],
    }

