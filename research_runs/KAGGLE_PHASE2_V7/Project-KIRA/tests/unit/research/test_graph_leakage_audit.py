"""Unit tests for Graph causal construction and leakage audit."""

from mcdl.research.graph import build_causal_graph_from_transactions
from mcdl.research.graph_leakage_audit import audit_graph_causal_integrity


def test_graph_causal_leakage_audit_pass():
    txns = [
        {"txn_id": "t1", "customer_id": "c1", "merchant_id": "m1", "device_id": "d1", "timestamp": 100.0},
        {"txn_id": "t2", "customer_id": "c1", "merchant_id": "m2", "device_id": "d1", "timestamp": 200.0},
        {"txn_id": "t3", "customer_id": "c2", "merchant_id": "m1", "device_id": "d2", "timestamp": 300.0},
    ]
    graph = build_causal_graph_from_transactions(txns)
    
    audit = audit_graph_causal_integrity(
        full_graph=graph,
        train_cutoff_ts=150.0,
        valid_cutoff_ts=250.0,
        test_cutoff_ts=350.0,
    )
    assert audit["audit_passed"] is True
    assert audit["status"] == "PASS"
    assert audit["checks"]["temporal_edge_isolation"]["violations"] == 0
    assert audit["summary"]["train_edges"] == 2  # c1->m1, c1->d1 at ts=100.0


def test_graph_chronological_ordering_fail():
    txns = [{"txn_id": "t1", "customer_id": "c1", "merchant_id": "m1", "timestamp": 100.0}]
    graph = build_causal_graph_from_transactions(txns)
    
    audit = audit_graph_causal_integrity(
        full_graph=graph,
        train_cutoff_ts=300.0,
        valid_cutoff_ts=200.0,  # Invalid: valid before train
        test_cutoff_ts=400.0,
    )
    assert audit["audit_passed"] is False
    assert audit["status"] == "BLOCKED_LEAKAGE_AUDIT"
