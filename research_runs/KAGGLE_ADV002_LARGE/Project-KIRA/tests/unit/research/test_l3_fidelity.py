"""Unit tests for L3 behavioral fidelity calculations (P1–P4)."""

import numpy as np
from mcdl.research.l3_fidelity import (
    compute_p1_interarrival,
    compute_p2_burstiness,
    compute_p3_graph_motifs,
    compute_p4_velocity_triggers,
    evaluate_l3_behavioral_fidelity,
)


def test_p1_interarrival():
    ts = np.array([10.0, 20.0, 30.0, 40.0])
    res = compute_p1_interarrival(ts)
    assert res["mean_dt"] == 10.0
    assert res["count"] == 3


def test_p2_burstiness():
    # Regular intervals have low burstiness
    ts_regular = np.array([0.0, 10.0, 20.0, 30.0])
    res_reg = compute_p2_burstiness(ts_regular)
    assert res_reg["sigma"] == 0.0
    assert res_reg["burstiness_coeff"] == -1.0


def test_p3_motifs():
    txns = [
        {"customer_id": "c1", "device_id": "d1", "merchant_id": "m1"},
        {"customer_id": "c2", "device_id": "d1", "merchant_id": "m2"},  # shared device d1
    ]
    res = compute_p3_graph_motifs(txns)
    assert res["shared_device_count"] == 1
    assert res["shared_device_ratio"] == 1.0


def test_p4_velocity():
    amounts = np.array([100.0, 1500.0, 200.0, 3000.0])
    ts = np.array([1.0, 2.0, 3.0, 4.0])
    res = compute_p4_velocity_triggers(amounts, ts, amount_threshold=1000.0)
    assert res["trigger_count"] == 2
    assert res["trigger_rate"] == 0.5


def test_evaluate_l3_fidelity_synthetic_only():
    txns = [
        {"timestamp": 10.0, "amount": 50.0, "customer_id": "c1", "device_id": "d1", "merchant_id": "m1"},
        {"timestamp": 25.0, "amount": 150.0, "customer_id": "c1", "device_id": "d1", "merchant_id": "m2"},
    ]
    res = evaluate_l3_behavioral_fidelity(txns, real_txns=None)
    assert res["status"] == "MEASURED_SYNTHETIC_ONLY"
    assert res["sample_count_synthetic"] == 2
    assert "comparability_note" in res
