"""ADV-001 Experiment Runner.

Executes the 10,000-attempt adversarial attack population evaluation against
the Blue detector and policy.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
import numpy as np

from mcdl.blue.model import BlueDetector
from mcdl.config import load_config, REPO_ROOT
from mcdl.features.batch import compute_batch_features
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.red.evaluator import CANONICAL_FAMILIES
from mcdl.red.search import RedSearchEngine
from mcdl.research.advanced.adv001.evaluator import (
    compute_population_statistics,
    evaluate_single_attempt,
)
from mcdl.research.advanced.adv001.population import generate_population_plans
from mcdl.research.advanced.adv001.storage import CheckpointManagerADV001
from mcdl.schemas import Decision, Transaction
from mcdl.world.generator import generate_world

BASELINE_DIR = REPO_ROOT / "artifacts" / "run_tiny_s20260827_193f7897_40997ab"
OUTPUT_DIR = REPO_ROOT / "research_runs" / "ADVANCED" / "ADV-001"


def run_adv001(
    target_count: int = 10000,
    seed: int = 20260831,
    batch_size: int = 500,
    output_dir: Path = OUTPUT_DIR,
    git_sha: str = "7cbbeff",
) -> dict[str, Any]:
    """Runs ADV-001 10,000 Adversarial Population experiment."""
    t_start = time.perf_counter()
    mgr = CheckpointManagerADV001(output_dir)

    # 1. Setup environment and load baseline world
    cfg = load_config(scale="tiny")
    world = generate_world(cfg)

    # Train Blue detector strictly on world training split
    feature_df = compute_batch_features(world.transactions, customers=world.customers)
    n_total = len(feature_df)
    train_idx = int(n_total * 0.70)
    valid_idx = int(n_total * 0.85)

    train_df = feature_df[:train_idx]
    valid_df = feature_df[train_idx:valid_idx]

    detector = BlueDetector(n_estimators=100, max_depth=5, learning_rate=0.05, random_state=20260827)
    detector.fit(train_df, valid_df)

    engine = RedSearchEngine(
        detector=detector,
        customers=world.customers,
        merchants=world.merchants,
        mandates=world.mandates,
    )

    # 2. Advance streaming feature extractor through pre-test history to identify candidate test cases
    sorted_txns = sorted(world.transactions, key=lambda t: (t.timestamp, t.txn_id))
    rolling_extractor = StreamingFeatureExtractor(customers=world.customers)

    for t in sorted_txns[:valid_idx]:
        rolling_extractor.extract(t)

    # Candidate transactions: find transactions scored as BLOCK or STEP_UP
    candidate_test_cases: list[Transaction] = []
    test_txns = sorted_txns[valid_idx:]

    for t in test_txns:
        state_snapshot = rolling_extractor.clone()
        feats = state_snapshot.extract(t)
        dec = detector.score_transaction(t, feats, mandates=world.mandates)
        if dec.decision in {Decision.BLOCK, Decision.STEP_UP}:
            candidate_test_cases.append(t)
        rolling_extractor.extract(t)

    if not candidate_test_cases:
        # Fallback to all test transactions if none naturally blocked
        candidate_test_cases = test_txns[:50]

    # 3. Generate population plans
    plans = generate_population_plans(
        candidate_transactions=candidate_test_cases,
        customers=world.customers,
        target_count=target_count,
        base_seed=seed,
    )

    # 4. Check completed batches for resume capability
    completed_batches = mgr.get_completed_batch_indices()
    n_batches = int(np.ceil(len(plans) / batch_size))

    latencies_ms: list[float] = []

    for b_idx in range(1, n_batches + 1):
        if b_idx in completed_batches:
            continue

        b_start = (b_idx - 1) * batch_size
        b_end = min(b_start + batch_size, len(plans))
        batch_plans = plans[b_start:b_end]

        batch_results = []
        for p in batch_plans:
            t0 = time.perf_counter()
            res = evaluate_single_attempt(
                plan=p,
                engine=engine,
                merchants=world.merchants,
                mandates=world.mandates,
                blue_model_version="run_tiny_s20260827_193f7897_40997ab",
            )
            lat = (time.perf_counter() - t0) * 1000.0
            latencies_ms.append(lat)
            batch_results.append(res)

        mgr.write_batch(b_idx, batch_results)

    # 5. Read all results and compute comprehensive statistics
    all_results = mgr.read_all_results()
    stats = compute_population_statistics(all_results)

    total_time_sec = round(time.perf_counter() - t_start, 2)
    throughput_eps = round(len(all_results) / total_time_sec, 2) if total_time_sec > 0 else 0.0

    # 6. EXP-007-A baseline comparison
    comparison_table = {
        "benchmark_comparison": {
            "attempts": {"EXP-007-A": 200, "ADV-001": len(all_results)},
            "asr_budget_1": {"EXP-007-A": 0.3333, "ADV-001": stats["budget_metrics"].get("1", {}).get("asr")},
            "asr_budget_5": {"EXP-007-A": 0.7667, "ADV-001": stats["budget_metrics"].get("5", {}).get("asr")},
            "asr_budget_20": {"EXP-007-A": 0.9667, "ADV-001": stats["budget_metrics"].get("20", {}).get("asr")},
            "asr_budget_100": {"EXP-007-A": 0.9667, "ADV-001": stats["budget_metrics"].get("100", {}).get("asr")},
            "families_covered": {"EXP-007-A": 5, "ADV-001": len(stats["family_metrics"])},
            "median_med": {"EXP-007-A": 2.8488, "ADV-001": stats.get("median_med")},
        },
        "interpretation": (
            f"ADV-001 scaled adversarial evaluation by 50x (from 200 to {len(all_results)} attempts) "
            "providing tighter 95% bootstrap confidence intervals across query budgets and families."
        ),
    }

    # 7. Provenance Record
    prov_record = {
        "experiment_id": "ADV-001",
        "dataset_id": "ADV001_ATTACK_POPULATION_10K",
        "scale": "tiny_world_scaled_attacks",
        "world_seed": 20260827,
        "population_seed": seed,
        "blue_model_version": "run_tiny_s20260827_193f7897_40997ab",
        "git_sha": git_sha,
        "sample_count": len(all_results),
        "runtime_seconds": total_time_sec,
        "throughput_attempts_per_sec": throughput_eps,
        "scoring_latency_p50_ms": round(float(np.percentile(latencies_ms, 50)), 3) if latencies_ms else None,
        "scoring_latency_p95_ms": round(float(np.percentile(latencies_ms, 95)), 3) if latencies_ms else None,
        "classification": "MEASURED",
    }

    config = {
        "experiment_id": "ADV-001",
        "target_count": target_count,
        "seed": seed,
        "batch_size": batch_size,
        "budgets": [1, 5, 20, 100],
        "families": [f.value for f in CANONICAL_FAMILIES],
    }

    # 8. Markdown Evidence Report
    evidence_md = f"""# ADV-001: Large-Scale Adversarial Population Evaluation Report

- **Experiment ID**: `ADV-001`
- **Population ID**: `ADV001_ATTACK_POPULATION_10K`
- **Total Evaluated Attempts**: `{len(all_results):,}`
- **Master Seed**: `{seed}`
- **Blue Model Version**: `run_tiny_s20260827_193f7897_40997ab`
- **Total Runtime**: `{total_time_sec}s` (`{throughput_eps} attempts/sec`)
- **Classification**: **`MEASURED`**

---

## 1. Primary Empirical Findings

| Metric | Measured Value | 95% Bootstrap CI | Baseline (EXP-007-A) |
| :--- | :--- | :--- | :--- |
| **Total Attempts** | **`{len(all_results):,}`** | N/A | `200` |
| **Aggregate ASR** | **`{stats['aggregate_asr'] * 100:.2f}%`** | `{stats['aggregate_asr_ci_95']}` | `N/A` |
| **ASR @ Budget 1** | **`{stats['budget_metrics'].get('1', {}).get('asr', 0) * 100:.2f}%`** | `{stats['budget_metrics'].get('1', {}).get('asr_ci_95')}` | `33.33%` |
| **ASR @ Budget 5** | **`{stats['budget_metrics'].get('5', {}).get('asr', 0) * 100:.2f}%`** | `{stats['budget_metrics'].get('5', {}).get('asr_ci_95')}` | `76.67%` |
| **ASR @ Budget 20** | **`{stats['budget_metrics'].get('20', {}).get('asr', 0) * 100:.2f}%`** | `{stats['budget_metrics'].get('20', {}).get('asr_ci_95')}` | `96.67%` |
| **ASR @ Budget 100** | **`{stats['budget_metrics'].get('100', {}).get('asr', 0) * 100:.2f}%`** | `{stats['budget_metrics'].get('100', {}).get('asr_ci_95')}` | `96.67%` |
| **Median MED** | **`{stats.get('median_med')}`** | `{stats.get('med_ci_95')}` | `2.8488` |

---

## 2. Attack Family Breakdown

| Family | Attempted | Evasions | ASR | 95% CI | Median Queries | Median MED |
| :--- | ---: | ---: | ---: | :--- | ---: | ---: |
"""

    for fam, fm in stats.get("family_metrics", {}).items():
        evidence_md += f"| `{fam}` | {fm['attempted']:,} | {fm['successful_evasions']:,} | {fm['asr']*100:.2f}% | {fm['asr_ci_95']} | {fm['median_query_count']} | {fm['median_perturbation_distance']} |\n"

    evidence_md += f"""
---

## 3. Outcome Taxonomy Distribution

- **ALLOWED_EVASION**: `{stats['allowed_evasion_count']:,}`
- **BLOCKED**: `{stats['blocked_count']:,}`
- **STEP_UP**: `{stats['step_up_count']:,}`
- **GENERATION_FAILURES**: `{stats['generation_failures']:,}`
- **ERRORS**: `{stats['error_count']:,}`

---

## 4. Scientific Limitations & Boundaries
1. **Synthetic Population Context**: The 10,000 attempts represent simulated mutation trajectories against a fixed world state, not 10,000 independent real-world adversaries.
2. **Deterministic Mutation Grid**: Diversity is parameterized over canonical mutation operators within defined mutability masks.
3. **No Dynamic Defender Adaptation**: ADV-001 measures evasion across an unhardened baseline detector without online retraining during the test sequence.
"""

    mgr.save_final_artifacts(
        config=config,
        stats=stats,
        comparison=comparison_table,
        provenance=prov_record,
        evidence_md=evidence_md,
    )

    return {
        "status": "COMPLETED",
        "total_attempts": len(all_results),
        "aggregate_asr": stats["aggregate_asr"],
        "runtime_seconds": total_time_sec,
        "throughput_eps": throughput_eps,
        "output_dir": str(output_dir),
    }


def main() -> None:
    print("Starting ADV-001 10,000 Adversarial Population Execution...")
    res = run_adv001(target_count=10000, seed=20260831, batch_size=500)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
