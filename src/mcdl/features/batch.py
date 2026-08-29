"""Batch Vectorised Feature Extractor — Independent Training Pipeline.

Computes exact mathematical features across transaction datasets in Polars.
Independently implemented from spec.py without referencing StreamingFeatureExtractor.
"""

from __future__ import annotations

import math
from typing import Any
import numpy as np
import polars as pl

from mcdl.features.spec import FEATURE_NAMES
from mcdl.schemas import Customer, Transaction


def _vectorized_haversine(lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """Computes great-circle distance in km between arrays of lat/lon."""
    r = 6371.0
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = (
        np.sin(delta_phi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return r * c


def _compute_customer_velocity_vectorized(
    timestamps_sec: np.ndarray,
    amounts: np.ndarray,
    deltas: list[float],
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Vectorized calculation of trailing causal velocity counts and sums for an entity."""
    n = len(timestamps_sec)
    if n == 0:
        return [(np.empty(0, dtype=np.int64), np.empty(0, dtype=np.float64)) for _ in deltas]

    prefix_amounts = np.zeros(n + 1, dtype=np.float64)
    prefix_amounts[1:] = np.cumsum(amounts)

    results = []
    for delta in deltas:
        left_idx = np.searchsorted(timestamps_sec, timestamps_sec - delta, side="left")
        counts = (np.arange(n) - left_idx).astype(np.int64)
        sums = prefix_amounts[np.arange(n)] - prefix_amounts[left_idx]
        results.append((counts, sums))
    return results


def _compute_merchant_velocity_and_lag_vectorized(
    timestamps_sec: np.ndarray,
    is_fraud_arr: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized calculation of merchant velocity (1h, 24h) and 7-day label lag."""
    n = len(timestamps_sec)
    if n == 0:
        return (
            np.empty(0, dtype=np.int64),
            np.empty(0, dtype=np.int64),
            np.empty(0, dtype=np.float64),
        )

    # 1h (3600s) and 24h (86400s) counts
    left_1h = np.searchsorted(timestamps_sec, timestamps_sec - 3600.0, side="left")
    left_24h = np.searchsorted(timestamps_sec, timestamps_sec - 86400.0, side="left")
    v1_count = (np.arange(n) - left_1h).astype(np.int64)
    v24_count = (np.arange(n) - left_24h).astype(np.int64)

    # 7-day label lag (7 * 86400 = 604800s)
    # Available labels are events with t_j <= t_i - 604800s (inclusive cutoff)
    seven_days_sec = 604800.0
    cutoff_indices = np.searchsorted(timestamps_sec, timestamps_sec - seven_days_sec, side="right")

    prefix_fraud = np.zeros(n + 1, dtype=np.float64)
    prefix_fraud[1:] = np.cumsum(is_fraud_arr.astype(np.float64))

    confirmed_fraud = prefix_fraud[cutoff_indices]
    confirmed_total = cutoff_indices.astype(np.float64)

    lag_fraud_rate = np.zeros(n, dtype=np.float64)
    valid_mask = confirmed_total > 0
    lag_fraud_rate[valid_mask] = confirmed_fraud[valid_mask] / confirmed_total[valid_mask]

    return v1_count, v24_count, lag_fraud_rate


def compute_batch_features(
    transactions: list[Transaction] | pl.DataFrame,
    customers: dict[str, Customer] | pl.DataFrame | None = None,
) -> pl.DataFrame:
    """Computes full feature matrix in batch mode matching exact causal specifications.

    Independently implemented using Polars and vectorised array operations.
    """
    # 1. Convert transactions to Polars DataFrame if list
    if isinstance(transactions, list):
        records = []
        for t in transactions:
            records.append({
                "txn_id": t.txn_id,
                "customer_id": t.customer_id,
                "merchant_id": t.merchant_id,
                "device_id": t.device_id,
                "timestamp": t.timestamp,
                "amount": float(t.amount),
                "mcc": str(t.mcc),
                "channel": t.channel.value if hasattr(t.channel, "value") else str(t.channel),
                "lat": float(t.lat),
                "lon": float(t.lon),
                "ip_prefix": str(t.ip_prefix),
                "is_new_device": bool(t.is_new_device),
                "auth_failed_count": int(t.auth_failed_count),
                "agent_id": t.agent_id,
                "mandate_id": t.mandate_id,
                "balance_before": float(t.balance_before),
                "available_credit": float(t.available_credit),
                "is_fraud": bool(t.is_fraud),
            })
        schema = {
            "txn_id": pl.Utf8,
            "customer_id": pl.Utf8,
            "merchant_id": pl.Utf8,
            "device_id": pl.Utf8,
            "timestamp": pl.Datetime,
            "amount": pl.Float64,
            "mcc": pl.Utf8,
            "channel": pl.Utf8,
            "lat": pl.Float64,
            "lon": pl.Float64,
            "ip_prefix": pl.Utf8,
            "is_new_device": pl.Boolean,
            "auth_failed_count": pl.Int64,
            "agent_id": pl.Utf8,
            "mandate_id": pl.Utf8,
            "balance_before": pl.Float64,
            "available_credit": pl.Float64,
            "is_fraud": pl.Boolean,
        }
        df = pl.DataFrame(records, schema=schema)
    elif isinstance(transactions, pl.DataFrame):
        df = transactions.clone()
    else:
        raise TypeError(f"Expected list[Transaction] or pl.DataFrame, got {type(transactions)}")

    if len(df) == 0:
        # Return empty schema with feature columns
        schema_dict = {
            "txn_id": pl.Utf8,
            "customer_id": pl.Utf8,
            "merchant_id": pl.Utf8,
            "timestamp": pl.Datetime,
            "is_fraud": pl.Boolean,
        }
        for name in FEATURE_NAMES:
            schema_dict[name] = pl.Float64
        return pl.DataFrame(schema=schema_dict)

    # 2. Enforce deterministic lexicographical causal order: (timestamp, txn_id)
    df = df.sort(["timestamp", "txn_id"])

    # 3. Resolve customer metadata (home_lat, home_lon, credit_limit)
    if customers is not None:
        if isinstance(customers, dict):
            cust_rows = []
            for c_id, cust in customers.items():
                cust_rows.append({
                    "customer_id": c_id,
                    "home_lat": float(cust.home_lat),
                    "home_lon": float(cust.home_lon),
                    "credit_limit": float(cust.credit_limit),
                })
            cust_df = pl.DataFrame(cust_rows)
        elif isinstance(customers, pl.DataFrame):
            cust_df = customers
        else:
            raise TypeError(f"Unsupported customers type: {type(customers)}")
        df = df.join(cust_df, on="customer_id", how="left")
    else:
        # Fallback if customer profile is not explicitly passed
        df = df.with_columns([
            pl.col("lat").alias("home_lat"),
            pl.col("lon").alias("home_lon"),
            (pl.col("balance_before") + pl.col("available_credit")).alias("credit_limit"),
        ])

    # Fill any null customer profile fields
    df = df.with_columns([
        pl.col("home_lat").fill_null(pl.col("lat")),
        pl.col("home_lon").fill_null(pl.col("lon")),
        pl.col("credit_limit").fill_null(pl.col("balance_before") + pl.col("available_credit")),
    ])

    # 4. Compute Stateless and Direct Temporal Features
    df = df.with_columns([
        pl.col("amount").cast(pl.Float64),
        (1.0 + pl.col("amount")).log().alias("log_amount"),
        pl.col("timestamp").dt.hour().cast(pl.Int64).alias("hour_of_day"),
        (pl.col("timestamp").dt.weekday() - 1).cast(pl.Int64).alias("day_of_week"),
        pl.col("auth_failed_count").cast(pl.Int64),
        pl.col("agent_id").is_not_null().cast(pl.Int64).alias("is_agent_initiated"),
    ])
    df = df.with_columns([
        (pl.col("day_of_week") >= 5).cast(pl.Int64).alias("is_weekend"),
    ])

    # 5. Spatial Distance from Home and Balance Utilization
    home_lat_arr = df["home_lat"].to_numpy()
    home_lon_arr = df["home_lon"].to_numpy()
    lat_arr = df["lat"].to_numpy()
    lon_arr = df["lon"].to_numpy()
    dist_home = _vectorized_haversine(home_lat_arr, home_lon_arr, lat_arr, lon_arr)

    df = df.with_columns([
        pl.Series("dist_from_home_km", dist_home, dtype=pl.Float64),
        pl.when(pl.col("credit_limit") > 0)
        .then(pl.col("balance_before") / pl.col("credit_limit"))
        .otherwise(0.0)
        .alias("balance_utilization"),
    ])

    # 6. Sequential Customer History (Shifted by 1 over customer_id)
    # Distance from previous, time since previous, speed, cumulative average
    df = df.with_columns([
        pl.col("lat").shift(1).over("customer_id").alias("prev_lat"),
        pl.col("lon").shift(1).over("customer_id").alias("prev_lon"),
        pl.col("timestamp").shift(1).over("customer_id").alias("prev_ts"),
        pl.col("amount").cum_sum().shift(1).over("customer_id").fill_null(0.0).alias("cum_amount_prior"),
        pl.cum_count("txn_id").shift(1).over("customer_id").fill_null(0).alias("cum_count_prior"),
    ])

    prev_lat_arr = df["prev_lat"].to_numpy()
    prev_lon_arr = df["prev_lon"].to_numpy()
    has_prev = ~df["prev_lat"].is_null().to_numpy()

    dist_prev = np.zeros(len(df), dtype=np.float64)
    if has_prev.any():
        dist_prev[has_prev] = _vectorized_haversine(
            prev_lat_arr[has_prev],
            prev_lon_arr[has_prev],
            lat_arr[has_prev],
            lon_arr[has_prev],
        )

    df = df.with_columns([
        pl.Series("dist_from_prev_txn_km", dist_prev, dtype=pl.Float64),
        pl.when(pl.col("prev_ts").is_not_null())
        .then((pl.col("timestamp") - pl.col("prev_ts")).dt.total_microseconds() / 1_000_000.0)
        .otherwise(-1.0)
        .alias("time_since_prev_txn_seconds"),
        pl.when(pl.col("cum_count_prior") > 0)
        .then(pl.col("cum_amount_prior") / pl.col("cum_count_prior"))
        .otherwise(pl.col("amount"))
        .alias("cust_avg_amount_hist"),
    ])

    df = df.with_columns([
        pl.when(pl.col("time_since_prev_txn_seconds") > 0)
        .then(pl.col("dist_from_prev_txn_km") / (pl.col("time_since_prev_txn_seconds") / 3600.0))
        .otherwise(0.0)
        .alias("speed_kmh"),
        pl.when(pl.col("cum_count_prior") > 0)
        .then(pl.col("amount") / pl.col("cust_avg_amount_hist"))
        .otherwise(1.0)
        .alias("cust_amount_to_avg_ratio"),
    ])

    # 7. Device Graph Features
    # is_new_device: first time device appears for customer (after customer's first transaction)
    # device_cust_count: distinct customers on device strictly prior to this transaction
    df = df.with_columns([
        pl.col("txn_id").cum_count().over(["customer_id", "device_id"]).alias("dev_occurrence"),
        pl.col("txn_id").cum_count().over("customer_id").alias("cust_overall_occurrence"),
        (pl.col("txn_id").cum_count().over(["device_id", "customer_id"]) == 1).cast(pl.Int64).alias("is_first_dev_cust"),
    ])

    df = df.with_columns([
        pl.when((pl.col("cust_overall_occurrence") > 1) & (pl.col("dev_occurrence") == 1))
        .then(1)
        .otherwise(0)
        .cast(pl.Int64)
        .alias("is_new_device"),
        pl.col("is_first_dev_cust").cum_sum().shift(1).over("device_id").fill_null(0).cast(pl.Int64).alias("device_cust_count"),
    ])

    # 8. Customer Velocity Windows (1h, 6h, 24h) via Vectorized Epoch Seconds
    # Convert timestamps to float epoch seconds for exact sub-microsecond interval matching
    ts_seconds = (df["timestamp"].dt.epoch("us").to_numpy().astype(np.float64)) / 1_000_000.0
    amounts_arr = df["amount"].to_numpy()
    cust_ids = df["customer_id"].to_numpy()

    cust_v1_count = np.zeros(len(df), dtype=np.int64)
    cust_v1_sum = np.zeros(len(df), dtype=np.float64)
    cust_v6_count = np.zeros(len(df), dtype=np.int64)
    cust_v6_sum = np.zeros(len(df), dtype=np.float64)
    cust_v24_count = np.zeros(len(df), dtype=np.int64)
    cust_v24_sum = np.zeros(len(df), dtype=np.float64)

    # Partition indices by customer_id (preserves sorted timestamp order)
    unique_custs, cust_inverse = np.unique(cust_ids, return_inverse=True)
    for c_idx in range(len(unique_custs)):
        mask = (cust_inverse == c_idx)
        indices = np.where(mask)[0]
        c_ts = ts_seconds[indices]
        c_amt = amounts_arr[indices]

        c_results = _compute_customer_velocity_vectorized(
            c_ts, c_amt, deltas=[3600.0, 21600.0, 86400.0]
        )
        cust_v1_count[indices] = c_results[0][0]
        cust_v1_sum[indices] = c_results[0][1]
        cust_v6_count[indices] = c_results[1][0]
        cust_v6_sum[indices] = c_results[1][1]
        cust_v24_count[indices] = c_results[2][0]
        cust_v24_sum[indices] = c_results[2][1]

    # 9. Merchant Velocity Windows & 7-Day Label Lag
    merch_ids = df["merchant_id"].to_numpy()
    is_fraud_arr = df["is_fraud"].to_numpy()

    merch_v1_count = np.zeros(len(df), dtype=np.int64)
    merch_v24_count = np.zeros(len(df), dtype=np.int64)
    merch_lag_fraud_rate = np.zeros(len(df), dtype=np.float64)

    unique_merchs, merch_inverse = np.unique(merch_ids, return_inverse=True)
    for m_idx in range(len(unique_merchs)):
        mask = (merch_inverse == m_idx)
        indices = np.where(mask)[0]
        m_ts = ts_seconds[indices]
        m_fraud = is_fraud_arr[indices]

        v1_c, v24_c, lag_f = _compute_merchant_velocity_and_lag_vectorized(m_ts, m_fraud)
        merch_v1_count[indices] = v1_c
        merch_v24_count[indices] = v24_c
        merch_lag_fraud_rate[indices] = lag_f

    # Add velocity and lag columns to DataFrame
    df = df.with_columns([
        pl.Series("cust_velocity_1h_count", cust_v1_count, dtype=pl.Int64),
        pl.Series("cust_velocity_1h_sum", cust_v1_sum, dtype=pl.Float64),
        pl.Series("cust_velocity_6h_count", cust_v6_count, dtype=pl.Int64),
        pl.Series("cust_velocity_6h_sum", cust_v6_sum, dtype=pl.Float64),
        pl.Series("cust_velocity_24h_count", cust_v24_count, dtype=pl.Int64),
        pl.Series("cust_velocity_24h_sum", cust_v24_sum, dtype=pl.Float64),
        pl.Series("merch_velocity_1h_count", merch_v1_count, dtype=pl.Int64),
        pl.Series("merch_velocity_24h_count", merch_v24_count, dtype=pl.Int64),
        pl.Series("merch_fraud_rate_7d_lag", merch_lag_fraud_rate, dtype=pl.Float64),
    ])

    # Select canonical identifiers and 25 feature columns in exact spec order
    output_columns = [
        "txn_id",
        "customer_id",
        "merchant_id",
        "timestamp",
        "is_fraud",
        *FEATURE_NAMES,
    ]

    return df.select(output_columns)
