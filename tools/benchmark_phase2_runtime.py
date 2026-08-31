"""Micro-benchmark for Phase 2 expensive operations across scales.

Measures:
1. Dataset generation
2. Polars DataFrame construction & feature computation
3. TemporalPaymentGraph construction
4. Arm A (Tabular Reference) training & calibration
5. Arm C (Causal Fusion) training & prediction
6. Arm D (Shuffled Topology) training & prediction
7. Paired bootstrap p-value computation (1,000 resamples)
8. S-03 zero-day evaluation
"""

from datetime import datetime
import json
import time
import numpy as np
import polars as pl

from mcdl.blue.calibration import IsotonicCalibrator
from mcdl.config import load_config
from mcdl.features.batch import compute_batch_features
from mcdl.research.phase2.experiments import (
    compute_paired_bootstrap_p_value,
    create_shuffled_topology_graph,
    evaluate_arm_metrics,
)
from mcdl.research.phase2.fusion import CausalGraphTabularFusion
from mcdl.research.phase2.graph_temporal import TemporalPaymentGraph
from mcdl.world.generator import generate_world
import lightgbm as lgb


def benchmark_scale(scale_name: str, target_events: int) -> dict[str, float]:
    print(f"\n--- Benchmarking Scale: {scale_name} ({target_events:,} events) ---")
    timings = {}

    # 1. Dataset Generation
    cfg = load_config(scale="tiny" if scale_name == "tiny" else "small")
    cfg["world"]["target_events"] = target_events
    if scale_name == "tiny":
        cfg["world"]["n_customers"] = 200
        cfg["world"]["n_merchants"] = 80
        cfg["world"]["n_days"] = 30
    elif scale_name == "small":
        cfg["world"]["n_customers"] = 1000
        cfg["world"]["n_merchants"] = 300
        cfg["world"]["n_days"] = 90
    elif scale_name == "medium":
        cfg["world"]["n_customers"] = 2500
        cfg["world"]["n_merchants"] = 500
        cfg["world"]["n_days"] = 180

    cfg["seed"] = 20260827
    
    t0 = time.perf_counter()
    world = generate_world(cfg)
    timings["dataset_generation_sec"] = round(time.perf_counter() - t0, 3)
    n_txns = len(world.transactions)
    timings["actual_events"] = n_txns

    # 2. Graph & Feature Construction
    t0 = time.perf_counter()
    graph = TemporalPaymentGraph(world.transactions)
    timings["graph_construction_sec"] = round(time.perf_counter() - t0, 3)

    train_idx = np.arange(int(0.70 * n_txns))
    val_idx = np.arange(int(0.70 * n_txns), int(0.85 * n_txns))
    test_idx = np.arange(int(0.85 * n_txns), n_txns)
    y_test = graph.is_fraud[test_idx]

    # 3. Arm A: Tabular Reference
    t0 = time.perf_counter()
    clf_a = lgb.LGBMClassifier(n_estimators=100, max_depth=4, num_leaves=15, learning_rate=0.05, random_state=20260827, verbose=-1)
    clf_a.fit(graph.x_txn[train_idx], graph.is_fraud[train_idx])
    val_probs_a = clf_a.predict_proba(graph.x_txn[val_idx])[:, 1]
    cal_a = IsotonicCalibrator()
    cal_a.fit(val_probs_a, graph.is_fraud[val_idx])
    probs_a = cal_a.transform(clf_a.predict_proba(graph.x_txn[test_idx])[:, 1])
    timings["arm_a_train_and_eval_sec"] = round(time.perf_counter() - t0, 3)

    # 4. Arm C: Causal Fusion
    t0 = time.perf_counter()
    model_c = CausalGraphTabularFusion(seed=20260827)
    model_c.fit(graph, train_idx, val_idx)
    probs_c = model_c.predict_proba(graph, test_idx)
    timings["arm_c_train_and_eval_sec"] = round(time.perf_counter() - t0, 3)

    # 5. Arm D: Shuffled Topology
    t0 = time.perf_counter()
    shuff_g = create_shuffled_topology_graph(graph, seed=20260827)
    model_d = CausalGraphTabularFusion(seed=20260827)
    model_d.fit(shuff_g, train_idx, val_idx)
    probs_d = model_d.predict_proba(shuff_g, test_idx)
    timings["arm_d_train_and_eval_sec"] = round(time.perf_counter() - t0, 3)

    # 6. Bootstrap p-value (1,000 resamples)
    t0 = time.perf_counter()
    p_val = compute_paired_bootstrap_p_value(y_test, probs_c, probs_a, n_resamples=1000, seed=20260827)
    timings["bootstrap_1000_sec"] = round(time.perf_counter() - t0, 3)
    timings["measured_p_value"] = p_val

    # 7. S-03 Zero-Day World C Inference
    t0 = time.perf_counter()
    world_c_fams = {"cross_merchant_fanout", "agent_subversion"}
    c_indices = np.array([i for i in test_idx if graph.attack_families[i] in world_c_fams], dtype=int)
    if len(c_indices) > 0:
        p_c_a = cal_a.transform(clf_a.predict_proba(graph.x_txn[c_indices])[:, 1])
        p_c_c = model_c.predict_proba(graph, c_indices)
    timings["s03_eval_sec"] = round(time.perf_counter() - t0, 3)
    timings["world_c_samples"] = len(c_indices)

    total_stage_sec = (
        timings["dataset_generation_sec"]
        + timings["graph_construction_sec"]
        + timings["arm_a_train_and_eval_sec"]
        + timings["arm_c_train_and_eval_sec"]
        + timings["arm_d_train_and_eval_sec"]
        + timings["bootstrap_1000_sec"]
        + timings["s03_eval_sec"]
    )
    timings["total_pipeline_single_seed_sec"] = round(total_stage_sec, 3)

    return timings


def main():
    results = {}
    # Run 10k (tiny), 25k (mid-tiny), 50k (small)
    for name, ev in [("tiny_10k", 10_000), ("mid_25k", 25_000), ("small_50k", 50_000)]:
        results[name] = benchmark_scale(name, ev)
        print(json.dumps(results[name], indent=2))

    with open("research_runs/KAGGLE_PHASE2_V7/micro_benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
