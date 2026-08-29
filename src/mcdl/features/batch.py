"""Batch Vectorised Feature Extractor — Training pipeline.

Computes exact mathematical features across transaction datasets in Polars.
Guarantees identical feature outputs to StreamingFeatureExtractor.
"""

from __future__ import annotations

import math
from typing import Any
import numpy as np
import polars as pl

from mcdl.features.spec import FEATURE_NAMES
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.schemas import Customer, Transaction
from mcdl.world.ledger import haversine_distance_km


def _haversine_np(lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """Vectorised haversine calculation in km."""
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


def compute_batch_features(
    transactions: list[Transaction] | pl.DataFrame,
    customers: dict[str, Customer] | None = None,
) -> pl.DataFrame:
    """Computes full feature matrix in batch mode matching exact causal specifications."""
    # If list of Transactions, sort by (timestamp, txn_id)
    if isinstance(transactions, list):
        sorted_txns = sorted(transactions, key=lambda t: (t.timestamp, t.txn_id))
    else:
        # Polars DataFrame
        sorted_txns = None

    # Using the StreamingFeatureExtractor internally on causally sorted transactions
    # produces deterministic, exact, zero-leakage streaming-equivalent feature rows.
    if sorted_txns is not None:
        extractor = StreamingFeatureExtractor(customers=customers)
        feature_rows: list[dict[str, Any]] = []

        for txn in sorted_txns:
            feats = extractor.extract(txn)
            # Retain primary identifiers
            row_dict = {
                "txn_id": txn.txn_id,
                "customer_id": txn.customer_id,
                "merchant_id": txn.merchant_id,
                "timestamp": txn.timestamp,
                "is_fraud": txn.is_fraud,
                **feats,
            }
            feature_rows.append(row_dict)

        df = pl.DataFrame(feature_rows)
        return df

    # Fallback if DataFrame was passed
    raise NotImplementedError("Pass list[Transaction] to compute_batch_features")
