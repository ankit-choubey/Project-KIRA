"""Strict Out-of-Time Temporal Splitter for Blue Team ML.

Guarantees:
max(train.timestamp) < min(valid.timestamp) < min(test.timestamp)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import polars as pl


@dataclass(frozen=True)
class SplitSummary:
    name: str
    row_count: int
    fraud_count: int
    legit_count: int
    fraud_rate: float
    min_ts: datetime
    max_ts: datetime


@dataclass(frozen=True)
class TemporalSplit:
    train_df: pl.DataFrame
    valid_df: pl.DataFrame
    test_df: pl.DataFrame
    train_summary: SplitSummary
    valid_summary: SplitSummary
    test_summary: SplitSummary


def _make_summary(name: str, df: pl.DataFrame) -> SplitSummary:
    row_count = len(df)
    if row_count == 0:
        raise ValueError(f"Split {name} is empty")
    fraud_count = int(df["is_fraud"].sum())
    legit_count = row_count - fraud_count
    fraud_rate = float(fraud_count / row_count)
    min_ts = df["timestamp"].min()
    max_ts = df["timestamp"].max()
    return SplitSummary(
        name=name,
        row_count=row_count,
        fraud_count=fraud_count,
        legit_count=legit_count,
        fraud_rate=fraud_rate,
        min_ts=min_ts,
        max_ts=max_ts,
    )


def temporal_split(
    df: pl.DataFrame,
    train_ratio: float = 0.70,
    valid_ratio: float = 0.15,
) -> TemporalSplit:
    """Partitions feature DataFrame into strict out-of-time train, valid, and test sets."""
    if len(df) < 10:
        raise ValueError(f"Dataset too small to split: {len(df)} rows")

    # Enforce deterministic chronological sorting
    sorted_df = df.sort(["timestamp", "txn_id"])

    n = len(sorted_df)
    raw_train_idx = int(n * train_ratio)
    raw_valid_idx = int(n * (train_ratio + valid_ratio))

    # Adjust train boundary to ensure max(train.ts) < min(valid.ts)
    # Find next index where timestamp is strictly greater
    train_ts = sorted_df["timestamp"][raw_train_idx]
    # Move train boundary to end of this timestamp group
    same_ts_mask = sorted_df["timestamp"] == train_ts
    train_split_idx = int(sorted_df.filter(pl.col("timestamp") <= train_ts).height)

    # If train consumed too much, fall back to strictly before train_ts if possible
    if train_split_idx >= n - 2:
        train_split_idx = int(sorted_df.filter(pl.col("timestamp") < train_ts).height)

    # Adjust valid boundary similarly
    valid_slice = sorted_df[train_split_idx:]
    if len(valid_slice) < 2:
        raise ValueError("Not enough data points after train split")

    target_valid_len = max(1, int(n * valid_ratio))
    target_valid_idx = min(train_split_idx + target_valid_len, n - 1)
    valid_ts = sorted_df["timestamp"][target_valid_idx]
    valid_split_idx = int(sorted_df.filter(pl.col("timestamp") <= valid_ts).height)

    if valid_split_idx >= n:
        valid_split_idx = int(sorted_df.filter(pl.col("timestamp") < valid_ts).height)

    train_df = sorted_df[:train_split_idx]
    valid_df = sorted_df[train_split_idx:valid_split_idx]
    test_df = sorted_df[valid_split_idx:]

    # Assert non-empty splits
    if len(train_df) == 0 or len(valid_df) == 0 or len(test_df) == 0:
        raise ValueError(f"Split resulted in empty partition: train={len(train_df)}, valid={len(valid_df)}, test={len(test_df)}")

    # Formal assertion of strict temporal separation
    assert train_df["timestamp"].max() < valid_df["timestamp"].min(), (
        f"Temporal leakage: train max {train_df['timestamp'].max()} >= valid min {valid_df['timestamp'].min()}"
    )
    assert valid_df["timestamp"].max() < test_df["timestamp"].min(), (
        f"Temporal leakage: valid max {valid_df['timestamp'].max()} >= test min {test_df['timestamp'].min()}"
    )

    return TemporalSplit(
        train_df=train_df,
        valid_df=valid_df,
        test_df=test_df,
        train_summary=_make_summary("train", train_df),
        valid_summary=_make_summary("valid", valid_df),
        test_summary=_make_summary("test", test_df),
    )
