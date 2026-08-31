"""Unit tests for real-world Sparkov evaluation pipelines."""

import csv
import json
from pathlib import Path
import numpy as np

from mcdl.research.real_world import (
    find_sparkov_dataset_path,
    load_sparkov_transactions,
    run_real_world_c2st_evaluation,
    run_real_world_l3_evaluation,
    run_real_world_tstr_evaluation,
)


def test_load_sparkov_transactions(tmp_path):
    csv_file = tmp_path / "fraudTest.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["trans_date_trans_time", "cc_num", "merchant", "category", "amt", "trans_num", "unix_time", "is_fraud"])
        writer.writerow(["2020-06-21 12:14:25", "123456", "fraud_test_merch", "misc_net", "55.20", "t1", "1592741665", "0"])
        writer.writerow(["2020-06-21 12:20:10", "123456", "fraud_test_merch", "misc_net", "1200.00", "t2", "1592742010", "1"])

    txns, manifest = load_sparkov_transactions(csv_file)
    assert len(txns) == 2
    assert manifest["namespace"] == "REAL_WORLD"
    assert manifest["positive_count"] == 1
    assert manifest["sample_count"] == 2
    assert txns[0]["amount"] == 55.20
    assert txns[1]["is_fraud"] == 1


def test_run_real_world_l3_evaluation():
    syn = [
        {"timestamp": 100.0, "amount": 50.0, "customer_id": "c1", "merchant_id": "m1"},
        {"timestamp": 200.0, "amount": 1500.0, "customer_id": "c1", "merchant_id": "m1"},
    ]
    real = [
        {"timestamp": 105.0, "amount": 60.0, "customer_id": "r1", "merchant_id": "m1"},
        {"timestamp": 210.0, "amount": 2000.0, "customer_id": "r2", "merchant_id": "m1"},
    ]
    res = run_real_world_l3_evaluation(syn, real)
    assert res["status"] == "MEASURED_REAL_COMPARISON"
    assert "p1_interarrival" in res
    assert "p2_burstiness" in res
    assert "p3_shared_entity_motifs" in res
    assert "NOT_COMPARABLE" in res["p3_shared_entity_motifs"]["shared_device"]
    assert "p4_velocity_triggers" in res


def test_run_real_world_c2st_evaluation():
    syn = [{"timestamp": i * 100.0, "amount": float(i * 10), "is_agent_initiated": False} for i in range(50)]
    real = [{"timestamp": i * 120.0, "amount": float(i * 15 + 5), "is_agent_initiated": False} for i in range(50)]
    
    res = run_real_world_c2st_evaluation(syn, real, n_bootstrap=10)
    assert res["status"] == "COMPLETE"
    assert "c2st_auc" in res
    assert res["c2st_auc"] is not None


def test_run_real_world_tstr_evaluation():
    syn = [{"timestamp": float(i), "amount": float(i * 20), "is_fraud": 1 if i % 5 == 0 else 0} for i in range(100)]
    real_test = [{"timestamp": float(i), "amount": float(i * 25), "is_fraud": 1 if i % 5 == 0 else 0} for i in range(50)]
    real_train = [{"timestamp": float(i), "amount": float(i * 22), "is_fraud": 1 if i % 5 == 0 else 0} for i in range(50)]

    res = run_real_world_tstr_evaluation(syn, real_test, real_train)
    assert res["status"] == "COMPLETE"
    assert "tstr" in res
    assert "trtr" in res
    assert res["tstr"]["pr_auc"] is not None
    assert res["trtr"]["pr_auc"] is not None
