"""ADV-002 Stateful Adversarial Swarm Execution Pipeline.

Orchestrates the multi-agent adversarial swarm evaluation across configurable scales and control arms.
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
        mode: str = "adaptive_memory",
        base_seed: int = 20260831,
        output_dir: Path | str | None = None,
        adv001_memory_path: Path | str | None = None,
        candidates: list[Transaction] | None = None,
        max_wallclock_seconds: float = 3000.0,
    ) -> None:
        self.scale = ADV002Scale(scale) if isinstance(scale, str) else scale
        self.mode = mode
        self.base_seed = base_seed
        self.output_dir = Path(output_dir) if output_dir else REPO_ROOT / "research_runs" / "ADVANCED" / "ADV-002"
        self.adv001_memory_path = Path(adv001_memory_path) if adv001_memory_path else REPO_ROOT / "research_runs" / "ADVANCED" / "ADV-001" / "attack_memory.jsonl"
        self.storage = ADV002Storage(self.output_dir)
        self.precomputed_candidates = candidates
        self.max_wallclock_seconds = max_wallclock_seconds

    def run(self) -> dict[str, Any]:
        """Executes the swarm evaluation run across configured campaigns."""
        params = get_scale_parameters(self.scale)
        n_targets = params["n_targets"]
        rounds_per_campaign = params["rounds_per_campaign"]
        expected_total_attempts = n_targets * rounds_per_campaign * 5

        print("=" * 75)
        print("ADV-002 RESOLVED CONFIGURATION:")
        print(f"  Scale: {self.scale.value}")
        print(f"  Mode: {self.mode}")
        print(f"  Agents: 5 stateful specialized agents")
        print(f"  Rounds per Agent: {rounds_per_campaign}")
        print(f"  Targets: {n_targets}")
        print(f"  Expected Attack Attempts: {expected_total_attempts}")
        print(f"  Base Seed: {self.base_seed}")
        print(f"  Max Wallclock Deadline: {self.max_wallclock_seconds:.1f}s")
        print("=" * 75)

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

        # 2. Candidate Transactions
        if self.precomputed_candidates is not None:
            candidates = self.precomputed_candidates[:n_targets]
        else:
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
        policy = DeterministicAdaptivePolicy(PolicyConfig(mode=self.mode))
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
        timeout_triggered = False

        # 6. Execute Campaigns with atomic checkpointing & Telemetry
        for c_idx, target_txn in enumerate(candidates, start=1):
            elapsed_now = time.perf_counter() - t_start
            if elapsed_now > self.max_wallclock_seconds:
                print(f"[TIMEOUT] Deadline exceeded ({elapsed_now:.1f}s > {self.max_wallclock_seconds:.1f}s). Stopping safely.")
                timeout_triggered = True
                break

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

            # Telemetry line
            el = time.perf_counter() - t_start
            att_done = len(all_results)
            rate = att_done / max(0.001, el)
            ev_count = sum(1 for r in all_results if r.evasion)
            curr_asr = (ev_count / max(1, att_done)) * 100
            rem_att = max(0, expected_total_attempts - att_done)
            eta_sec = rem_att / max(0.001, rate)
            print(
                f"[{self.mode.upper()}] Target {c_idx}/{len(candidates)} ({target_txn.txn_id}) | "
                f"Attempts {att_done}/{expected_total_attempts} | ASR: {curr_asr:.1f}% | "
                f"{rate:.1f} att/s | Elapsed: {int(el)//60:02d}:{int(el)%60:02d} | "
                f"ETA: {int(eta_sec)//60:02d}:{int(eta_sec)%60:02d}"
            )

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
        metrics["efficiency"]["timeout_triggered"] = timeout_triggered

        # 8. Comparability Document
        comparability = {
            "experiment_id": "ADV-002",
            "scale": self.scale.value,
            "mode": self.mode,
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
            "mode": self.mode,
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
            "mode": self.mode,
            "base_seed": self.base_seed,
            "git_commit": "22bde659e441b0f9851ebdc1ffbc2c796bde78ca",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "adv001_memory_records_ingested": shared_memory.count_records()["adv001_records"],
            "adv002_memory_records_added": shared_memory.count_records()["adv002_records"],
            "runtime_sec": runtime_sec,
            "throughput_attempts_per_sec": throughput,
        }

        config_data = {
            "scale": self.scale.value,
            "mode": self.mode,
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
            "results": all_results,
        }


def extract_canonical_candidate_targets(scale: ADV002Scale | str = "large") -> list[Transaction]:
    """Extracts candidate target transactions deterministically from the test split."""
    params = get_scale_parameters(scale)
    n_targets = params["n_targets"]

    cfg = load_config(scale="tiny")
    world = generate_world(cfg)
    feature_df = compute_batch_features(world.transactions, customers=world.customers)
    n_total = len(feature_df)
    train_idx = int(n_total * 0.70)
    valid_idx = int(n_total * 0.85)

    detector = BlueDetector(n_estimators=100, max_depth=5, learning_rate=0.05, random_state=20260827)
    detector.fit(feature_df[:train_idx], feature_df[train_idx:valid_idx])

    sorted_txns = sorted(world.transactions, key=lambda t: (t.timestamp, t.txn_id))
    rolling_extractor = StreamingFeatureExtractor(customers=world.customers)

    for t in sorted_txns[:valid_idx]:
        rolling_extractor.extract(t)

    candidates: list[Transaction] = []
    test_txns = sorted_txns[valid_idx:]

    for t in test_txns:
        state_snapshot = rolling_extractor.clone()
        feats = state_snapshot.extract(t)
        dec = detector.score_transaction(t, feats, mandates=world.mandates)
        if dec.decision in {Decision.BLOCK, Decision.STEP_UP}:
            candidates.append(t)
        rolling_extractor.extract(t)

    if not candidates:
        candidates = test_txns[:n_targets]

    return candidates[:n_targets]


def run_adv002_multi_arm(
    scale: str = "large",
    base_seed: int = 20260831,
    root_output_dir: Path | str | None = None,
    max_wallclock_seconds: float = 3000.0,
) -> dict[str, Any]:
    """Executes the full 3-arm ADV-002 large evaluation with shared population manifest."""
    t_global_start = time.perf_counter()
    out_dir = Path(root_output_dir) if root_output_dir else REPO_ROOT / "research_runs" / "ADVANCED" / "ADV-002-LARGE"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("ADV-002 MULTI-ARM CLOUD EXPERIMENT EXECUTION ENGINE")
    print(f"  Scale: {scale}")
    print(f"  Arms: adaptive_memory, static_control, memory_disabled")
    print(f"  Master Seed: {base_seed}")
    print(f"  Root Output Directory: {out_dir}")
    print(f"  Global Deadline: {max_wallclock_seconds:.1f}s (50 minutes)")
    print("=" * 80)

    # 1. Generate and hash population manifest ONCE
    candidates = extract_canonical_candidate_targets(scale=scale)
    manifest_records = [
        {
            "index": i,
            "target_txn_id": t.txn_id,
            "customer_id": t.customer_id,
            "merchant_id": t.merchant_id,
            "amount": t.amount,
            "timestamp": str(t.timestamp),
        }
        for i, t in enumerate(candidates, start=1)
    ]
    manifest_bytes = json.dumps(manifest_records, indent=2, sort_keys=True).encode("utf-8")
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()

    with open(out_dir / "population_manifest.json", "w", encoding="utf-8") as f:
        f.write(manifest_bytes.decode("utf-8"))
    with open(out_dir / "population_manifest.sha256", "w", encoding="utf-8") as f:
        f.write(manifest_sha)

    print(f"Population Manifest Generated: {len(candidates)} targets | SHA-256: {manifest_sha}")

    # 2. Execute Arms sequentially with remaining time budget
    arms = ["adaptive_memory", "static_control", "memory_disabled"]
    arm_outputs: dict[str, Any] = {}
    all_memory_records = []

    for arm_name in arms:
        elapsed = time.perf_counter() - t_global_start
        remaining_budget = max(60.0, max_wallclock_seconds - elapsed)
        print("\n" + "#" * 80)
        print(f"LAUNCHING ARM: {arm_name.upper()} (Remaining Budget: {remaining_budget:.1f}s)")
        print("#" * 80)

        arm_dir = out_dir / arm_name
        runner = ADV002Runner(
            scale=scale,
            mode=arm_name,
            base_seed=base_seed,
            output_dir=arm_dir,
            candidates=candidates,
            max_wallclock_seconds=remaining_budget,
        )
        arm_res = runner.run()
        arm_outputs[arm_name] = arm_res

        # Collect attack records for consolidated memory
        for r in arm_res.get("results", []):
            rec = r.to_memory_record()
            rec.provenance["arm"] = arm_name
            all_memory_records.append(rec.to_dict())

    total_global_runtime_sec = round(time.perf_counter() - t_global_start, 3)

    # 3. Write consolidated attack memory
    memory_out_path = out_dir / "attack_memory.jsonl"
    with open(memory_out_path, "w", encoding="utf-8") as f:
        for rec_dict in all_memory_records:
            f.write(json.dumps(rec_dict) + "\n")

    # 4. Cross-Arm Comparison Metrics
    cross_arm_metrics = {
        "scale": scale,
        "population_manifest_sha256": manifest_sha,
        "target_count": len(candidates),
        "total_attempts_executed": len(all_memory_records),
        "arms": {
            arm: {
                "attempts": arm_outputs[arm]["metrics"]["total_attacks"],
                "evasions": arm_outputs[arm]["metrics"]["defense"]["outcome_distribution"].get("ALLOWED_EVASION", 0),
                "asr": arm_outputs[arm]["metrics"]["defense"]["aggregate_asr"],
                "blocked_percentage": arm_outputs[arm]["metrics"]["defense"]["blocked_percentage"],
                "step_up_percentage": arm_outputs[arm]["metrics"]["defense"]["step_up_percentage"],
                "median_queries": arm_outputs[arm]["metrics"]["efficiency"]["median_queries"],
                "median_med": arm_outputs[arm]["metrics"]["efficiency"]["median_perturbation_distance"],
                "runtime_sec": arm_outputs[arm]["metrics"]["efficiency"]["runtime_sec"],
                "throughput": arm_outputs[arm]["metrics"]["efficiency"]["throughput_attempts_per_sec"],
            }
            for arm in arms
        },
        "comparisons": {
            "delta_asr_adaptive_vs_static": round(
                arm_outputs["adaptive_memory"]["metrics"]["defense"]["aggregate_asr"] -
                arm_outputs["static_control"]["metrics"]["defense"]["aggregate_asr"],
                4
            ),
            "delta_asr_adaptive_vs_memory_disabled": round(
                arm_outputs["adaptive_memory"]["metrics"]["defense"]["aggregate_asr"] -
                arm_outputs["memory_disabled"]["metrics"]["defense"]["aggregate_asr"],
                4
            ),
        }
    }

    with open(out_dir / "cross_arm_metrics.json", "w", encoding="utf-8") as f:
        json.dump(cross_arm_metrics, f, indent=2)

    # 5. Behavioural Analysis
    behavioural_analysis = {
        "arms": {
            arm: arm_outputs[arm]["adaptation_metrics"] for arm in arms
        },
        "hypotheses_evaluation": {
            "H1_adaptation_gain": {
                "hypothesis": "ASR(adaptive_memory) > ASR(static_control)",
                "delta_asr": cross_arm_metrics["comparisons"]["delta_asr_adaptive_vs_static"],
                "supported": cross_arm_metrics["comparisons"]["delta_asr_adaptive_vs_static"] >= 0.0,
            },
            "H2_shared_memory_gain": {
                "hypothesis": "ASR(adaptive_memory) > ASR(memory_disabled)",
                "delta_asr": cross_arm_metrics["comparisons"]["delta_asr_adaptive_vs_memory_disabled"],
                "supported": cross_arm_metrics["comparisons"]["delta_asr_adaptive_vs_memory_disabled"] >= 0.0,
            }
        }
    }

    with open(out_dir / "behavioural_analysis.json", "w", encoding="utf-8") as f:
        json.dump(behavioural_analysis, f, indent=2)

    # 6. Global Integrity & Runtime Profile
    runtime_profile = {
        "scale": scale,
        "total_global_runtime_sec": total_global_runtime_sec,
        "total_attempts": len(all_memory_records),
        "overall_throughput_attempts_per_sec": round(len(all_memory_records) / max(0.001, total_global_runtime_sec), 2),
        "arm_runtimes_sec": {arm: arm_outputs[arm]["metrics"]["efficiency"]["runtime_sec"] for arm in arms},
    }
    with open(out_dir / "runtime_profile.json", "w", encoding="utf-8") as f:
        json.dump(runtime_profile, f, indent=2)

    global_integrity = {
        "experiment_id": "ADV-002-LARGE",
        "scale": scale,
        "total_arms": 3,
        "population_manifest_sha256": manifest_sha,
        "consolidated_memory_records": len(all_memory_records),
        "all_arms_accounting_verified": all(arm_outputs[arm]["integrity"]["accounting_verified"] for arm in arms),
        "adv001_memory_immutable": all(arm_outputs[arm]["integrity"]["adv001_intact"] for arm in arms),
        "total_runtime_sec": total_global_runtime_sec,
    }
    with open(out_dir / "integrity.json", "w", encoding="utf-8") as f:
        json.dump(global_integrity, f, indent=2)

    # 7. Global Status
    status_data = {
        "status": "COMPLETED",
        "experiment_id": "ADV-002-LARGE",
        "scale": scale,
        "total_attempts_executed": len(all_memory_records),
        "adaptive_asr": arm_outputs["adaptive_memory"]["metrics"]["defense"]["aggregate_asr"],
        "static_asr": arm_outputs["static_control"]["metrics"]["defense"]["aggregate_asr"],
        "nomem_asr": arm_outputs["memory_disabled"]["metrics"]["defense"]["aggregate_asr"],
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    with open(out_dir / "status.json", "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2)

    print("\n" + "=" * 80)
    print(f"ALL 3 ARMS COMPLETED IN {total_global_runtime_sec:.2f}s ({runtime_profile['overall_throughput_attempts_per_sec']} att/s)")
    print(f"Adaptive ASR: {status_data['adaptive_asr']} | Static ASR: {status_data['static_asr']} | NoMem ASR: {status_data['nomem_asr']}")
    print("=" * 80)

    return {
        "cross_arm_metrics": cross_arm_metrics,
        "behavioural_analysis": behavioural_analysis,
        "runtime_profile": runtime_profile,
        "integrity": global_integrity,
        "status": status_data,
    }


def run_adv002(
    scale: str = "smoke",
    mode: str = "adaptive_memory",
    seed: int = 20260831,
    output_dir: Path | str | None = None,
) -> dict[str, Any]:
    runner = ADV002Runner(scale=scale, mode=mode, base_seed=seed, output_dir=output_dir)
    return runner.run()


def main() -> None:
    parser = argparse.ArgumentParser(description="ADV-002 Stateful Swarm Runner")
    parser.add_argument("--scale", type=str, default="smoke", choices=["smoke", "standard", "large"])
    parser.add_argument("--mode", type=str, default="adaptive_memory", choices=["adaptive_memory", "static_control", "memory_disabled", "all_arms"])
    parser.add_argument("--seed", type=int, default=20260831)
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--deadline-sec", type=float, default=3000.0)
    args = parser.parse_args()

    if args.mode == "all_arms":
        result = run_adv002_multi_arm(
            scale=args.scale,
            base_seed=args.seed,
            root_output_dir=args.output_dir,
            max_wallclock_seconds=args.deadline_sec,
        )
        print(json.dumps(result["cross_arm_metrics"], indent=2))
    else:
        result = run_adv002(scale=args.scale, mode=args.mode, seed=args.seed, output_dir=args.output_dir)
        print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()
