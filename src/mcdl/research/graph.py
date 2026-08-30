"""Causal Payment Graph Topology Construction.

Builds relational payment graph topologies across:
- Customer
- Merchant
- Device
- Agent
- Transaction

Every edge is annotated with its exact event timestamp for causal snapshot generation.
"""

from __future__ import annotations

from typing import Any, Optional


class CausalGraphTopology:
    """Represents a time-indexed bipartite/heterogeneous payment graph."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {
            "customer": {},
            "merchant": {},
            "device": {},
            "agent": {},
            "transaction": {},
        }
        # Edges stored as: list of (source_type, source_id, target_type, target_id, timestamp, metadata)
        self.edges: list[dict[str, Any]] = []

    def add_transaction(self, txn: dict[str, Any]) -> None:
        """Inserts a transaction into the causal topology."""
        t_id = str(txn.get("txn_id", ""))
        c_id = str(txn.get("customer_id", ""))
        m_id = str(txn.get("merchant_id", ""))
        d_id = str(txn.get("device_id", ""))
        a_id = str(txn.get("agent_id", ""))
        ts_raw = txn.get("timestamp", 0.0)
        if isinstance(ts_raw, (int, float)):
            ts = float(ts_raw)
        else:
            try:
                from datetime import datetime
                ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00")).timestamp()
            except Exception:
                ts = 0.0

        # Node tracking
        if t_id:
            self.nodes["transaction"][t_id] = {"first_seen": ts, "is_fraud": txn.get("is_fraud", 0)}
        if c_id:
            self.nodes["customer"].setdefault(c_id, {"first_seen": ts})
        if m_id:
            self.nodes["merchant"].setdefault(m_id, {"first_seen": ts})
        if d_id:
            self.nodes["device"].setdefault(d_id, {"first_seen": ts})
        if a_id:
            self.nodes["agent"].setdefault(a_id, {"first_seen": ts})

        # Causal timestamped edges
        if c_id and m_id:
            self.edges.append({
                "src_type": "customer", "src_id": c_id,
                "dst_type": "merchant", "dst_id": m_id,
                "timestamp": ts, "amount": txn.get("amount", 0.0),
            })
        if c_id and d_id:
            self.edges.append({
                "src_type": "customer", "src_id": c_id,
                "dst_type": "device", "dst_id": d_id,
                "timestamp": ts,
            })
        if a_id and c_id:
            self.edges.append({
                "src_type": "agent", "src_id": a_id,
                "dst_type": "customer", "dst_id": c_id,
                "timestamp": ts,
            })

    def get_snapshot(self, cutoff_timestamp: float) -> "CausalGraphTopology":
        """Returns a graph snapshot containing only events at or before cutoff_timestamp."""
        snapshot = CausalGraphTopology()
        for edge in self.edges:
            if edge["timestamp"] <= cutoff_timestamp:
                snapshot.edges.append(edge)
                snapshot.nodes[edge["src_type"]][edge["src_id"]] = self.nodes[edge["src_type"]].get(edge["src_id"], {})
                snapshot.nodes[edge["dst_type"]][edge["dst_id"]] = self.nodes[edge["dst_type"]].get(edge["dst_id"], {})
        return snapshot

    def summary(self) -> dict[str, Any]:
        """Returns topological entity and edge counts."""
        return {
            "node_counts": {k: len(v) for k, v in self.nodes.items()},
            "edge_count": len(self.edges),
            "edge_types": {
                "customer_merchant": sum(1 for e in self.edges if e["src_type"] == "customer" and e["dst_type"] == "merchant"),
                "customer_device": sum(1 for e in self.edges if e["src_type"] == "customer" and e["dst_type"] == "device"),
                "agent_customer": sum(1 for e in self.edges if e["src_type"] == "agent" and e["dst_type"] == "customer"),
            },
        }


def build_causal_graph_from_transactions(transactions: list[dict[str, Any]]) -> CausalGraphTopology:
    """Factory helper to build a full causal graph from transaction stream."""
    graph = CausalGraphTopology()
    for txn in transactions:
        graph.add_transaction(txn)
    return graph
