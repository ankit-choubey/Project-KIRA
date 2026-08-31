"""ADV-002 Stateful Adversarial Swarm Execution Pipeline.

Orchestrates the multi-agent adversarial swarm evaluation across configurable scales.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from pathlib import Path
import sys
import time
from typing import Any
import numpy as np

from mcdl.blue.model import BlueDetector
from mcdl.config import REPO_ROOT, load_config
from mcdl.features.batch import compute_batch_features
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.red.search import RedSearchEngine
from mcdl.research.advanced.adv002.agents import create_canonical_agent_swarm
from mcdl.research.advanced.adv002.evaluator import (
    SwarmEvaluator,
    compute_adaptation_metrics,
    compute_swarm_metrics,
)
from mcdl.research.advanced.adv002.memory import SharedAttackMemory
from mcdl.research.advanced.adv002.policy import DeterministicAdaptivePolicy, PolicyConfig
from mcdl.research.advanced.adv002.scheduler import SwarmConfig, SwarmScheduler
from mcdl.research.advanced.adv002.storage import ADV002Storage
from mcdl.schemas import Customer, Decision, Mandate, Merchant, Transaction
from mcdl.world.generator import generate_world


class ADV002Scale(str, Enum):
    SMOKE = "smoke"
    STANDARD = "standard"
    LARGE = "large"


def get_scale_parameters(scale: ADV002Scale | str) -> dict[str, int]:
    scale_enum = ADV002Scale(scale) if isinstance(scale, str) else scale
    if scale_enum == ADV002Scale.SMOKE:
        return {"n_targets": 1, "rounds_per_campaign": 5}
    elif scale_enum == ADV002Scale.STANDARD:
        return {"n_targets": 5, "rounds_per_campaign": 20}
    elif scale_enum == ADV002Scale.LARGE:
        return {"n_targets": 10, "rounds_per_campaign": 100}
    return {"n_targets": 1, "rounds_per_campaign": 5}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class ADV002Runner:
    """End-to-end runner for ADV-002 Multi-Agent Swarm Evaluation."""

    def __init__(
        self,
        scale: ADV002Scale | str = ADV002Scale.SMOKE,
        base_seed: int = 20260831,
        output_dir: Path | str | None = None,
        adv001_memory_path: Path | str | None = None,
    ) -> None:
        self.scale = ADV002Scale(scale) if isinstance(scale, str) else scale
        self.base_seed = base_seed
        self.output_dir = Path(output_dir) if output_dir else REPO_ROOT / "research_runs" / "ADVANCED" / "ADV-002"
        self.adv001_memory_path = Path(adv001_memory_path) if adv001_memory_path else REPO_ROOT / "research_runs" / "ADVANCED" / "ADV-001" / "attack_memory.jsonl"
        self.storage = ADV002Storage(self.output_dir)

    def run(self) -> dict[str, Any]:
        """Executes the swarm evaluation run across configured campaigns."""
        params = get_scale_parameters(self.scale)
        n_targets = params["n_targets"]
        rounds_per_campaign = params["rounds_per_campaign"]
        expected_total_attempts = n_targets * rounds_per_campaign * 5

        print("=" * 70)
        print("ADV-002 RESOLVED CONFIGURATION:")
        print(f"  Scale: {self.scale.value}")
        print(f"  Agents: 5 stateful specialized agents")
        print(f"  Rounds per Agent: {rounds_per_campaign}")
        print(f"  Targets: {n_targets}")
        print(f"  Expected Attack Attempts: {expected_total_attempts}")
        print(f"  Base Seed: {self.base_seed}")
        print("=" * 70)

        # Record ADV-001 Memory Integrity before execution
        adv001_sha_before = sha256_file(self.adv001_memory_path) if self.adv001_memory_path.exists() else "NONE"
        adv001_count_before = 0
        if self.adv001_memory_path.exists():
            with open(self.adv001_memory_path, "r", encoding="utf-8") as f:
                adv001_count_before = sum(1 for line in f if line.strip())

        t_start = time.perf_counter()

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

        red_engine = RedSearchEngine(
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
            candidate_test_cases = test_txns[:n_targets]

        candidates = candidate_test_cases[:n_targets]

        # 3. Ingest Historical ADV-001 Memory (Read-only)
        shared_memory = SharedAttackMemory(self.adv001_memory_path)

        # 4. Instantiate Swarm Agents, Policy, and Evaluator
        agents = create_canonical_agent_swarm(base_seed=self.base_seed)
        policy = DeterministicAdaptivePolicy(PolicyConfig())
        evaluator = SwarmEvaluator(engine=red_engine, blue_model_version="run_tiny_s20260827_193f7897_40997ab")

        # 5. Configure Scheduler
        swarm_config = SwarmConfig(
            n_campaigns=len(candidates),
            rounds_per_campaign=rounds_per_campaign,
            base_seed=self.base_seed,
        )
        scheduler = SwarmScheduler(
            agents=agents,
            memory=shared_memory,
            policy=policy,
            evaluator=evaluator,
            customers=world.customers,
            merchants=world.merchants,
            mandates=world.mandates,
            config=swarm_config,
        )

        completed_campaigns = self.storage.get_completed_campaign_ids()
        all_results = []

        # 6. Execute Campaigns with atomic checkpointing
        for c_idx, target_txn in enumerate(candidates, start=1):
            expected_cmp_id = f"cmp_adv002_{c_idx:04d}_{target_txn.txn_id}"
            if expected_cmp_id in completed_campaigns:
                print(f"Skipping already completed campaign: {expected_cmp_id}")
                continue

            def on_round(campaign, result):
                self.storage.save_round_result(result)
                self.storage.save_campaign_state(campaign)

            cmp_results = scheduler.run_campaign(
                target_txn=target_txn,
                campaign_index=c_idx,
                round_callback=on_round,
            )
            all_results.extend(cmp_results)

        runtime_sec = round(time.perf_counter() - t_start, 3)
        total_attacks = len(all_results)
        throughput = round(total_attacks / max(0.001, runtime_sec), 2)
        mean_scoring_latency_ms = round((runtime_sec / max(1, total_attacks)) * 1000, 2)

        # 7. Compute Metrics
        metrics = compute_swarm_metrics(all_results)
        adaptation_metrics = compute_adaptation_metrics(all_results)

        metrics["efficiency"]["runtime_sec"] = runtime_sec
        metrics["efficiency"]["throughput_attempts_per_sec"] = throughput
        metrics["efficiency"]["mean_scoring_latency_ms"] = mean_scoring_latency_ms

        # 8. Comparability Document
        comparability = {
            "experiment_id": "ADV-002",
            "comparison_target": "ADV-001",
            "shared_components": [
                "Blue detector model (run_tiny_s20260827_193f7897_40997ab)",
                "5 Canonical attack families (burst_drain, slow_siphon, geo_hop, agent_subversion, cross_merchant_fanout)",
                "Layer-1 physical constraints and mutability masks",
                "Distance computation metric (normalized Euclidean space)",
                "Underlying RedSearchEngine candidate generation",
            ],
            "structural_differences": [
                "ADV-001 used non-adaptive static round-robin grid search (10k independent attempts)",
                "ADV-002 implements stateful sequential campaigns with multi-agent coordination",
                "ADV-002 dynamically updates family selection and query budgets via shared memory",
                "ADV-002 measures multi-objective rewards (evasion + distance + query efficiency)",
            ],
            "comparability_verdict": "NOT_DIRECTLY_COMPARABLE_IN_AGGREGATE",
            "rationale": "ADV-002 introduces campaign-level adaptation and sequential statefulness, evaluating behavioral evolution rather than static population coverage."
        }

        # 9. Verify ADV-001 Memory Integrity after execution
        adv001_sha_after = sha256_file(self.adv001_memory_path) if self.adv001_memory_path.exists() else "NONE"
        adv001_count_after = 0
        if self.adv001_memory_path.exists():
            with open(self.adv001_memory_path, "r", encoding="utf-8") as f:
                adv001_count_after = sum(1 for line in f if line.strip())

        adv001_intact = (adv001_sha_before == adv001_sha_after) and (adv001_count_before == adv001_count_after)

        outcomes = metrics.get("outcome_distribution", {})
        total_outcomes = sum(outcomes.values())
        accounting_verified = (total_outcomes == total_attacks)

        integrity_data = {
            "experiment_id": "ADV-002",
            "scale": self.scale.value,
            "adv001_memory_sha256_before": adv001_sha_before,
            "adv001_memory_sha256_after": adv001_sha_after,
            "adv001_records_before": adv001_count_before,
            "adv001_records_after": adv001_count_after,
            "adv001_intact": adv001_intact,
            "total_adv002_attempts": total_attacks,
            "unique_adv002_attack_ids": len({r.attack_id for r in all_results}),
            "accounting_closure_sum": total_outcomes,
            "accounting_verified": accounting_verified,
            "runtime_sec": runtime_sec,
            "throughput_attempts_per_sec": throughput,
        }

        provenance = {
            "experiment_id": "ADV-002",
            "scale": self.scale.value,
            "base_seed": self.base_seed,
            "git_commit": "9a47f35419b7874319d720f255db048684b56f41",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "adv001_memory_records_ingested": shared_memory.count_records()["adv001_records"],
            "adv002_memory_records_added": shared_memory.count_records()["adv002_records"],
            "runtime_sec": runtime_sec,
            "throughput_attempts_per_sec": throughput,
        }

        config_data = {
            "scale": self.scale.value,
            "n_targets": n_targets,
            "rounds_per_campaign": rounds_per_campaign,
            "base_seed": self.base_seed,
            "agents_count": len(agents),
            "total_expected_attempts": expected_total_attempts,
        }

        self.storage.save_final_artifacts(
            config=config_data,
            metrics=metrics,
            adaptation_metrics=adaptation_metrics,
            comparability=comparability,
            provenance=provenance,
        )
        self.storage.save_integrity(integrity_data)

        return {
            "metrics": metrics,
            "adaptation_metrics": adaptation_metrics,
            "comparability": comparability,
            "provenance": provenance,
            "integrity": integrity_data,
        }


def run_adv002(scale: str = "smoke", seed: int = 20260831) -> dict[str, Any]:
    runner = ADV002Runner(scale=scale, base_seed=seed)
    return runner.run()


def main() -> None:
    parser = argparse.ArgumentParser(description="ADV-002 Stateful Swarm Runner")
    parser.add_argument("--scale", type=str, default="smoke", choices=["smoke", "standard", "large"])
    parser.add_argument("--seed", type=int, default=20260831)
    args = parser.parse_args()

    result = run_adv002(scale=args.scale, seed=args.seed)
    print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()
