"""Temporal-Causal Payment Graph Representation & Slicing.

Implements transaction-centric heterogeneous temporal graph structures:
Nodes:
- transaction (28 canonical features)
- customer (causal historical aggregates strictly < t)
- merchant (causal historical aggregates strictly < t)
- device (causal historical aggregates strictly < t)
- agent (causal historical aggregates strictly < t)

Edges:
- customer -> transaction
- transaction -> merchant
- transaction -> device
- agent -> transaction (if present)

Strict Temporal Causality Rule:
G(t) contains ONLY nodes, edges, aggregates, and features available strictly before timestamp t.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from mcdl.features.batch import compute_batch_features
from mcdl.features.spec import FEATURE_NAMES


@dataclass
class TemporalEntityState:
    """Maintains causal aggregate state for an entity up to timestamp t."""
    tx_count: int = 0
    amount_sum: float = 0.0
    fraud_count: int = 0
    last_seen_ts: float = 0.0
    recent_tx_indices: list[int] = field(default_factory=list)


class TemporalPaymentGraph:
    """Transaction-centric heterogeneous graph with strict causal snapshot semantics."""

    def __init__(
        self,
        transactions_df: pl.DataFrame | list[Any],
        features_df: pl.DataFrame | None = None,
    ) -> None:
        if isinstance(transactions_df, list):
            records = []
            for t in transactions_df:
                if isinstance(t, dict):
                    records.append(t)
                elif hasattr(t, "model_dump"):
                    records.append(t.model_dump())
                else:
                    records.append({
                        "txn_id": getattr(t, "txn_id", ""),
                        "customer_id": getattr(t, "customer_id", ""),
                        "merchant_id": getattr(t, "merchant_id", ""),
                        "device_id": getattr(t, "device_id", ""),
                        "timestamp": getattr(t, "timestamp", ""),
                        "amount": float(getattr(t, "amount", 0.0)),
                        "currency": getattr(t, "currency", "USD"),
                        "mcc": getattr(t, "mcc", "5411"),
                        "channel": getattr(t, "channel", "pos"),
                        "is_fraud": bool(getattr(t, "is_fraud", False)),
                        "attack_family": getattr(t, "attack_family", None),
                    })
            transactions_df = pl.DataFrame(records)

        # Ensure transactions are sorted strictly in causal order (timestamp, txn_id)
        if "timestamp" in transactions_df.columns and transactions_df["timestamp"].dtype == pl.String:
            try:
                df = transactions_df.with_columns(pl.col("timestamp").str.to_datetime(time_zone="UTC"))
            except Exception:
                df = transactions_df.with_columns(pl.col("timestamp").str.to_datetime())
        else:
            df = transactions_df.clone()

        self.raw_df = df.sort(["timestamp", "txn_id"])
        
        # Compute canonical 28 features if not provided
        if features_df is None:
            self.features_df = compute_batch_features(self.raw_df)
        else:
            self.features_df = features_df.clone()

        # Align features
        feature_cols = [c for c in FEATURE_NAMES if c in self.features_df.columns]
        self.feature_names = feature_cols
        
        # Extract numpy arrays for fast vectorized causal traversal
        self.n_txns = len(self.raw_df)
        self.txn_ids = self.raw_df["txn_id"].to_list()
        
        # Convert timestamp to float seconds
        ts_series = self.raw_df["timestamp"]
        if ts_series.dtype == pl.Datetime:
            # Datetime in nanoseconds or microseconds to seconds
            self.timestamps = (ts_series.dt.epoch("ms") / 1000.0).to_numpy()
        else:
            self.timestamps = ts_series.cast(pl.Float64).to_numpy()

        self.customer_ids = self.raw_df["customer_id"].to_list()
        self.merchant_ids = self.raw_df["merchant_id"].to_list()
        self.device_ids = self.raw_df["device_id"].to_list()
        self.agent_ids = [str(a) if a is not None else "" for a in self.raw_df["agent_id"].to_list()]
        

        if "is_fraud" in self.raw_df.columns:
            self.is_fraud = self.raw_df["is_fraud"].cast(pl.Int64).to_numpy().copy()
        else:
            self.is_fraud = np.zeros(self.n_txns, dtype=np.int64)

        if "attack_family" in self.raw_df.columns:
            self.attack_families = [str(f) if f is not None else "benign" for f in self.raw_df["attack_family"].to_list()]
        else:
            self.attack_families = ["benign"] * self.n_txns

        self.x_txn = self.features_df.select(self.feature_names).to_numpy().astype(np.float64).copy()

        # Replace NaNs/Infs with 0.0
        self.x_txn = np.nan_to_num(self.x_txn, nan=0.0, posinf=0.0, neginf=0.0)

        # Build entity-to-transaction index lists (strictly in causal ascending order)
        self._build_causal_indices()

    def _build_causal_indices(self) -> None:
        """Indexes transactions by entity strictly in causal chronological order."""
        self.cust_to_txns: dict[str, list[int]] = {}
        self.merch_to_txns: dict[str, list[int]] = {}
        self.dev_to_txns: dict[str, list[int]] = {}
        self.agent_to_txns: dict[str, list[int]] = {}

        for idx in range(self.n_txns):
            c_id = self.customer_ids[idx]
            m_id = self.merchant_ids[idx]
            d_id = self.device_ids[idx]
            a_id = self.agent_ids[idx]

            self.cust_to_txns.setdefault(c_id, []).append(idx)
            self.merch_to_txns.setdefault(m_id, []).append(idx)
            self.dev_to_txns.setdefault(d_id, []).append(idx)
            if a_id:
                self.agent_to_txns.setdefault(a_id, []).append(idx)

    def get_causal_entity_aggregates(self, txn_idx: int) -> np.ndarray:
        """Computes causal entity aggregates strictly before event timestamp t_i.
        
        Returns a vector containing:
        - Customer historical count & amount sum (strictly < t_i)
        - Merchant historical count & amount sum (strictly < t_i)
        - Device historical unique customer count (strictly < t_i)
        - Agent historical count (strictly < t_i)
        Total 7 features.
        """
        c_id = self.customer_ids[txn_idx]
        m_id = self.merchant_ids[txn_idx]
        d_id = self.device_ids[txn_idx]
        a_id = self.agent_ids[txn_idx]

        # 1. Customer history
        c_hist = [i for i in self.cust_to_txns.get(c_id, []) if i < txn_idx]
        c_cnt = len(c_hist)
        c_sum = sum(self.x_txn[i, 0] for i in c_hist) if c_hist else 0.0

        # 2. Merchant history
        m_hist = [i for i in self.merch_to_txns.get(m_id, []) if i < txn_idx]
        m_cnt = len(m_hist)
        m_sum = sum(self.x_txn[i, 0] for i in m_hist) if m_hist else 0.0

        # 3. Device history (unique customers seen strictly < t_i)
        d_hist = [i for i in self.dev_to_txns.get(d_id, []) if i < txn_idx]
        d_unique_cust = len({self.customer_ids[i] for i in d_hist})
        d_cnt = len(d_hist)

        # 4. Agent history
        a_cnt = 0
        if a_id:
            a_hist = [i for i in self.agent_to_txns.get(a_id, []) if i < txn_idx]
            a_cnt = len(a_hist)

        return np.array([c_cnt, c_sum, m_cnt, m_sum, d_cnt, d_unique_cust, a_cnt], dtype=np.float64)

    def get_relational_neighbors(self, txn_idx: int, max_neighbors: int = 10) -> list[int]:
        """Returns indices of prior transactions sharing customer, merchant, or device strictly < t_i."""
        c_id = self.customer_ids[txn_idx]
        m_id = self.merchant_ids[txn_idx]
        d_id = self.device_ids[txn_idx]
        a_id = self.agent_ids[txn_idx]

        neighbors: set[int] = set()
        
        # Prior customer txns
        for i in reversed(self.cust_to_txns.get(c_id, [])):
            if i < txn_idx:
                neighbors.add(i)
                if len(neighbors) >= max_neighbors:
                    break

        # Prior merchant txns
        for i in reversed(self.merch_to_txns.get(m_id, [])):
            if i < txn_idx:
                neighbors.add(i)
                if len(neighbors) >= max_neighbors * 2:
                    break

        # Prior device txns
        for i in reversed(self.dev_to_txns.get(d_id, [])):
            if i < txn_idx:
                neighbors.add(i)
                if len(neighbors) >= max_neighbors * 3:
                    break

        # Prior agent txns
        if a_id:
            for i in reversed(self.agent_to_txns.get(a_id, [])):
                if i < txn_idx:
                    neighbors.add(i)
                    if len(neighbors) >= max_neighbors * 4:
                        break

        sorted_neighbors = sorted(neighbors)
        return sorted_neighbors[-max_neighbors:] if len(sorted_neighbors) > max_neighbors else sorted_neighbors

    def get_causal_neighborhood_representation(self, txn_idx: int) -> np.ndarray:
        """Computes mean aggregated representation of causally connected prior transactions.
        
        Returns 28-dim mean vector (or 0 if no prior neighbors).
        """
        nbrs = self.get_relational_neighbors(txn_idx, max_neighbors=10)
        if not nbrs:
            return np.zeros(self.x_txn.shape[1], dtype=np.float64)
        return np.mean(self.x_txn[nbrs], axis=0)

    def summary(self) -> dict[str, Any]:
        """Returns node, edge, and memory safety summary."""
        n_cust = len(self.cust_to_txns)
        n_merch = len(self.merch_to_txns)
        n_dev = len(self.dev_to_txns)
        n_agent = len(self.agent_to_txns)
        n_edges = (
            self.n_txns  # cust -> txn
            + self.n_txns  # txn -> merch
            + self.n_txns  # txn -> dev
            + sum(1 for a in self.agent_ids if a)  # agent -> txn
        )
        mem_mb = (self.x_txn.nbytes + self.timestamps.nbytes + self.is_fraud.nbytes) / (1024 * 1024)

        return {
            "node_counts": {
                "transaction": self.n_txns,
                "customer": n_cust,
                "merchant": n_merch,
                "device": n_dev,
                "agent": n_agent,
                "total_nodes": self.n_txns + n_cust + n_merch + n_dev + n_agent,
            },
            "edge_counts": {
                "customer_initiates_txn": self.n_txns,
                "txn_to_merchant": self.n_txns,
                "txn_from_device": self.n_txns,
                "agent_facilitates_txn": sum(1 for a in self.agent_ids if a),
                "total_edges": n_edges,
            },
            "feature_dims": {
                "transaction": len(self.feature_names),
                "customer_aggregates": 2,
                "merchant_aggregates": 2,
                "device_aggregates": 2,
                "agent_aggregates": 1,
                "total_entity_aggregates": 7,
            },
            "tensor_memory_mb": round(mem_mb, 4),
            "memory_safe": mem_mb < 500.0,
        }
