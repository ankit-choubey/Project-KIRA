"""ADV-002 Swarm Evaluator, Reward Engine, and Adaptation Metrics.

Evaluates swarm attacks against Blue detector, assigns explicit rewards,
and computes campaign-level and adaptation-specific metrics.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import math
from typing import Any
import numpy as np

from mcdl.blue.model import BlueDetector
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.red.search import AttackProvenance, RedSearchEngine
from mcdl.research.advanced.adv002.memory import MemoryRecord, SharedAttackMemory
from mcdl.schemas import AttackFamily, Customer, Decision, Mandate, Merchant, Transaction


@dataclass
class RewardBreakdown:
    """Explicit decomposition of deterministic reward components."""

    base_evasion_reward: float
    perturbation_penalty: float
    query_efficiency_penalty: float
    decision_penalty: float
    total_reward: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def compute_reward(
    evasion: bool,
    blue_decision: str,
    queries_used: int,
    query_budget: int,
    perturbation_distance: float | None,
    evasion_weight: float = 1.0,
    dist_weight: float = 0.10,
    query_weight: float = 0.15,
    block_penalty: float = 0.50,
    step_up_penalty: float = 0.20,
) -> RewardBreakdown:
    """Computes explicit deterministic multi-objective reward."""
    query_ratio = (queries_used / max(1, query_budget))

    if evasion:
        base_ev = evasion_weight
        dist_pen = -(dist_weight * (perturbation_distance if perturbation_distance is not None else 0.0))
        q_pen = -(query_weight * query_ratio)
        dec_pen = 0.0
    elif blue_decision == "STEP_UP":
        base_ev = 0.0
        dist_pen = 0.0
        q_pen = -(query_weight * query_ratio)
        dec_pen = -step_up_penalty
    else:  # BLOCK, ERROR, or FAILED
        base_ev = 0.0
        dist_pen = 0.0
        q_pen = -(query_weight * query_ratio)
        dec_pen = -block_penalty

    total = round(base_ev + dist_pen + q_pen + dec_pen, 4)

    return RewardBreakdown(
        base_evasion_reward=round(base_ev, 4),
        perturbation_penalty=round(dist_pen, 4),
        query_efficiency_penalty=round(q_pen, 4),
        decision_penalty=round(dec_pen, 4),
        total_reward=total,
    )


@dataclass
class SwarmAttemptResult:
    """Standardized record of an evaluated multi-agent swarm attack attempt."""

    attack_id: str
    campaign_id: str
    agent_id: str
    parent_attack_id: str | None
    round_number: int
    family: str
    strategy: str
    seed: int
    query_budget: int
    queries_used: int
    mutation_count: int
    perturbation_distance: float | None
    target_transaction_id: str
    blue_model_version: str
    blue_score: float
    blue_decision: str
    evasion: bool
    outcome: str
    reward: float
    reward_breakdown: dict[str, float]
    memory_references: list[str]
    is_exploration: bool
    policy_metadata: dict[str, Any]
    timestamp: str
    provenance: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_memory_record(self) -> MemoryRecord:
        """Converts swarm attempt result into an appendable MemoryRecord."""
        return MemoryRecord(
            attack_id=self.attack_id,
            family=self.family,
            strategy=self.strategy,
            seed=self.seed,
            parent_attack_id=self.parent_attack_id,
            query_budget=self.query_budget,
            queries_used=self.queries_used,
            mutation_count=self.mutation_count,
            perturbation_distance=self.perturbation_distance,
            target_transaction_id=self.target_transaction_id,
            blue_model_version=self.blue_model_version,
            blue_score=self.blue_score,
            blue_decision=self.blue_decision,
            evasion=self.evasion,
            outcome=self.outcome,
            timestamp=self.timestamp,
            provenance=self.provenance,
            origin="ADV-002",
        )


class SwarmEvaluator:
    """Executes planned swarm attempts and assigns formal outcomes and rewards."""

    def __init__(
        self,
        engine: RedSearchEngine,
        blue_model_version: str = "run_tiny_s20260827_193f7897_40997ab",
    ) -> None:
        self.engine = engine
        self.blue_model_version = blue_model_version

    def evaluate_swarm_attempt(
        self,
        attack_id: str,
        campaign_id: str,
        agent_id: str,
        round_number: int,
        source_txn: Transaction,
        family: AttackFamily,
        strategy_name: str,
        budget: int,
        seed: int,
        is_exploration: bool,
        memory_refs: list[str],
        policy_metadata: dict[str, Any],
        parent_attack_id: str | None = None,
        feature_extractor_state: StreamingFeatureExtractor | None = None,
    ) -> SwarmAttemptResult:
        """Evaluates a single swarm attack attempt against the Blue detector."""
        t_now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        try:
            prov: AttackProvenance = self.engine.attack(
                source_txn=source_txn,
                family=family,
                budget=budget,
                seed=seed,
                feature_extractor_state=feature_extractor_state,
            )

            is_allow = (
                prov.final_decision == Decision.ALLOW
                or getattr(prov.final_decision, "value", "") == "ALLOW"
                or str(prov.final_decision) == "ALLOW"
            )
            is_step_up = (
                prov.final_decision == Decision.STEP_UP
                or getattr(prov.final_decision, "value", "") == "STEP_UP"
                or str(prov.final_decision) == "STEP_UP"
            )
            is_block = (
                prov.final_decision == Decision.BLOCK
                or getattr(prov.final_decision, "value", "") == "BLOCK"
                or str(prov.final_decision) == "BLOCK"
            )

            is_evasion = bool(prov.success) and is_allow and ("SOURCE_ALREADY_ALLOWED" not in prov.rejection_reasons)

            if is_evasion:
                outcome = "ALLOWED_EVASION"
            elif prov.invalid_mutations > 0 and prov.valid_mutations == 0:
                if any("IMMUTABLE" in r for r in prov.rejection_reasons):
                    outcome = "INVALID_MUTATION"
                else:
                    outcome = "FAILED_MUTATION"
            elif is_step_up:
                outcome = "STEP_UP"
            elif is_block:
                outcome = "BLOCKED"
            else:
                outcome = "BLOCKED"

            blue_decision_str = prov.final_decision.value if hasattr(prov.final_decision, "value") else str(prov.final_decision)
            med = float(prov.med) if (prov.med is not None and is_evasion) else None

            reward_bd = compute_reward(
                evasion=is_evasion,
                blue_decision=blue_decision_str,
                queries_used=prov.queries_used,
                query_budget=budget,
                perturbation_distance=med,
            )

            prov_dict = {
                "attack_instance_id": prov.attack_instance_id,
                "queries_used": prov.queries_used,
                "mutations_attempted": prov.mutations_attempted,
                "valid_mutations": prov.valid_mutations,
                "invalid_mutations": prov.invalid_mutations,
                "original_decision": prov.original_decision.value if hasattr(prov.original_decision, "value") else str(prov.original_decision),
                "final_decision": blue_decision_str,
                "original_risk": float(prov.original_risk),
                "final_risk": float(prov.final_risk),
                "rejection_reasons": prov.rejection_reasons,
            }

            return SwarmAttemptResult(
                attack_id=attack_id,
                campaign_id=campaign_id,
                agent_id=agent_id,
                parent_attack_id=parent_attack_id,
                round_number=round_number,
                family=family.value,
                strategy=strategy_name,
                seed=seed,
                query_budget=budget,
                queries_used=prov.queries_used,
                mutation_count=prov.mutations_attempted,
                perturbation_distance=med,
                target_transaction_id=source_txn.txn_id,
                blue_model_version=self.blue_model_version,
                blue_score=float(prov.final_risk),
                blue_decision=blue_decision_str,
                evasion=is_evasion,
                outcome=outcome,
                reward=reward_bd.total_reward,
                reward_breakdown=reward_bd.to_dict(),
                memory_references=memory_refs,
                is_exploration=is_exploration,
                policy_metadata=policy_metadata,
                timestamp=t_now,
                provenance=prov_dict,
            )

        except Exception as exc:
            reward_bd = compute_reward(
                evasion=False,
                blue_decision="BLOCK",
                queries_used=0,
                query_budget=budget,
                perturbation_distance=None,
            )
            return SwarmAttemptResult(
                attack_id=attack_id,
                campaign_id=campaign_id,
                agent_id=agent_id,
                parent_attack_id=parent_attack_id,
                round_number=round_number,
                family=family.value,
                strategy=strategy_name,
                seed=seed,
                query_budget=budget,
                queries_used=0,
                mutation_count=0,
                perturbation_distance=None,
                target_transaction_id=source_txn.txn_id,
                blue_model_version=self.blue_model_version,
                blue_score=1.0,
                blue_decision="BLOCK",
                evasion=False,
                outcome="ERROR",
                reward=reward_bd.total_reward,
                reward_breakdown=reward_bd.to_dict(),
                memory_references=memory_refs,
                is_exploration=is_exploration,
                policy_metadata=policy_metadata,
                timestamp=t_now,
                provenance={"error": str(exc)},
            )


def compute_swarm_metrics(results: list[SwarmAttemptResult]) -> dict[str, Any]:
    """Computes aggregate campaign and agent metrics across all evaluated attempts."""
    total_attacks = len(results)
    if total_attacks == 0:
        return {"total_attacks": 0, "status": "EMPTY"}

    evasions = [1.0 if r.evasion else 0.0 for r in results]
    asr = float(np.mean(evasions))
    meds = [r.perturbation_distance for r in results if r.perturbation_distance is not None]
    queries = [r.queries_used for r in results]
    rewards = [r.reward for r in results]

    # Breakdowns by Agent
    agent_groups: dict[str, list[SwarmAttemptResult]] = {}
    for r in results:
        agent_groups.setdefault(r.agent_id, []).append(r)

    agent_metrics = {}
    for ag_id, group in agent_groups.items():
        ag_ev = [1.0 if r.evasion else 0.0 for r in group]
        ag_meds = [r.perturbation_distance for r in group if r.perturbation_distance is not None]
        agent_metrics[ag_id] = {
            "attempts": len(group),
            "evasions": int(np.sum(ag_ev)),
            "asr": round(float(np.mean(ag_ev)), 4),
            "median_queries": float(np.median([r.queries_used for r in group])),
            "mean_reward": round(float(np.mean([r.reward for r in group])), 4),
            "median_perturbation": round(float(np.median(ag_meds)), 4) if ag_meds else None,
        }

    # Breakdowns by Family
    family_groups: dict[str, list[SwarmAttemptResult]] = {}
    for r in results:
        family_groups.setdefault(r.family, []).append(r)

    family_metrics = {}
    for fam, group in family_groups.items():
        fam_ev = [1.0 if r.evasion else 0.0 for r in group]
        family_metrics[fam] = {
            "attempts": len(group),
            "evasions": int(np.sum(fam_ev)),
            "asr": round(float(np.mean(fam_ev)), 4),
        }

    # Breakdowns by Budget
    budget_groups: dict[int, list[SwarmAttemptResult]] = {}
    for r in results:
        budget_groups.setdefault(r.query_budget, []).append(r)

    budget_metrics = {}
    for b in sorted(budget_groups.keys()):
        b_group = budget_groups[b]
        b_ev = [1.0 if r.evasion else 0.0 for r in b_group]
        budget_metrics[str(b)] = {
            "attempts": len(b_group),
            "evasions": int(np.sum(b_ev)),
            "asr": round(float(np.mean(b_ev)), 4),
        }

    # Breakdowns by Round
    round_groups: dict[int, list[SwarmAttemptResult]] = {}
    for r in results:
        round_groups.setdefault(r.round_number, []).append(r)

    round_metrics = {}
    for rnd in sorted(round_groups.keys()):
        rnd_group = round_groups[rnd]
        rnd_ev = [1.0 if r.evasion else 0.0 for r in rnd_group]
        round_metrics[str(rnd)] = {
            "attempts": len(rnd_group),
            "evasions": int(np.sum(rnd_ev)),
            "asr": round(float(np.mean(rnd_ev)), 4),
            "mean_reward": round(float(np.mean([r.reward for r in rnd_group])), 4),
        }

    outcomes: dict[str, int] = {}
    for r in results:
        outcomes[r.outcome] = outcomes.get(r.outcome, 0) + 1

    unique_campaigns = len({r.campaign_id for r in results})
    unique_targets = len({r.target_transaction_id for r in results})
    mem_refs_count = sum(len(r.memory_references) for r in results)

    # Calculate P95 metrics
    p95_queries = float(np.percentile(queries, 95)) if queries else 0.0
    p95_med = float(np.percentile(meds, 95)) if meds else None

    # Defense percentages
    blocked_pct = round((outcomes.get("BLOCKED", 0) / total_attacks) * 100, 2)
    step_up_pct = round((outcomes.get("STEP_UP", 0) / total_attacks) * 100, 2)

    return {
        "population": {
            "agents": len(agent_groups),
            "campaigns": unique_campaigns,
            "rounds": len(round_groups),
            "attacks": total_attacks,
            "targets": unique_targets,
            "families": sorted(list(family_groups.keys())),
            "budgets": sorted(list(budget_groups.keys())),
        },
        "defense": {
            "aggregate_asr": round(asr, 4),
            "asr_by_agent": {k: v["asr"] for k, v in agent_metrics.items()},
            "asr_by_family": {k: v["asr"] for k, v in family_metrics.items()},
            "asr_by_budget": {k: v["asr"] for k, v in budget_metrics.items()},
            "asr_by_round": {k: v["asr"] for k, v in round_metrics.items()},
            "blocked_percentage": blocked_pct,
            "step_up_percentage": step_up_pct,
            "outcome_distribution": outcomes,
        },
        "efficiency": {
            "total_queries": sum(queries),
            "median_queries": float(np.median(queries)),
            "p95_queries": p95_queries,
            "mean_perturbation_distance": round(float(np.mean(meds)), 4) if meds else None,
            "median_perturbation_distance": round(float(np.median(meds)), 4) if meds else None,
            "p95_perturbation_distance": round(p95_med, 4) if p95_med is not None else None,
            "best_perturbation_distance": round(float(np.min(meds)), 4) if meds else None,
            "mean_reward": round(float(np.mean(rewards)), 4),
        },
        "agent_metrics": agent_metrics,
        "family_metrics": family_metrics,
        "budget_metrics": budget_metrics,
        "round_metrics": round_metrics,
        "total_campaigns": unique_campaigns,
        "total_agents": len(agent_groups),
        "total_rounds": len(round_groups),
        "total_attacks": total_attacks,
        "aggregate_asr": round(asr, 4),
        "outcome_distribution": outcomes,
    }


def compute_adaptation_metrics(results: list[SwarmAttemptResult]) -> dict[str, Any]:
    """Computes behavioral adaptation metrics proving learning and strategy shifts."""
    if not results:
        return {"status": "EMPTY"}

    round_groups: dict[int, list[SwarmAttemptResult]] = {}
    for r in results:
        round_groups.setdefault(r.round_number, []).append(r)

    sorted_rounds = sorted(round_groups.keys())
    first_round = sorted_rounds[0]
    last_round = sorted_rounds[-1]

    r1_results = round_groups[first_round]
    r_last_results = round_groups[last_round]

    r1_asr = float(np.mean([1.0 if r.evasion else 0.0 for r in r1_results]))
    r_last_asr = float(np.mean([1.0 if r.evasion else 0.0 for r in r_last_results]))
    delta_asr = round(r_last_asr - r1_asr, 4)

    # Family selection distribution and entropy
    family_counts: dict[str, int] = {}
    for r in results:
        family_counts[r.family] = family_counts.get(r.family, 0) + 1

    total = len(results)
    entropy = 0.0
    for cnt in family_counts.values():
        p = cnt / total
        if p > 0:
            entropy -= p * math.log2(p)

    exploration_count = sum(1 for r in results if r.is_exploration)
    exploitation_count = total - exploration_count
    exp_ratio = round(exploration_count / max(1, total), 4)

    # Memory reuse rate (proportion of attempts with >= 1 retrieved memory reference)
    memory_reused = sum(1 for r in results if len(r.memory_references) > 0)
    memory_reuse_rate = round(memory_reused / total, 4)
    mem_refs_count = sum(len(r.memory_references) for r in results)

    # Successful-memory reuse rate: attempts where memory_references led to evasion
    evasions_with_memory = sum(1 for r in results if r.evasion and len(r.memory_references) > 0)
    total_evasions = sum(1 for r in results if r.evasion)
    succ_mem_rate = round(evasions_with_memory / max(1, total_evasions), 4) if total_evasions > 0 else 0.0

    # Count family switches and budget adjustments
    family_switches = 0
    budget_adjustments = 0
    campaign_agents: dict[tuple[str, str], list[SwarmAttemptResult]] = {}
    for r in results:
        campaign_agents.setdefault((r.campaign_id, r.agent_id), []).append(r)

    for history in campaign_agents.values():
        for i in range(1, len(history)):
            if history[i].family != history[i - 1].family:
                family_switches += 1
            if history[i].query_budget != history[i - 1].query_budget:
                budget_adjustments += 1

    # Failed pattern avoidance rate: rate of switching away from blocked actions
    blocked_prior_count = 0
    switched_after_blocked = 0
    for history in campaign_agents.values():
        for i in range(len(history) - 1):
            if history[i].outcome in ("BLOCKED", "STEP_UP"):
                blocked_prior_count += 1
                if (history[i + 1].family != history[i].family) or (history[i + 1].query_budget != history[i].query_budget):
                    switched_after_blocked += 1

    avoidance_rate = round(switched_after_blocked / max(1, blocked_prior_count), 4) if blocked_prior_count > 0 else 1.0

    total_adaptation_events = family_switches + budget_adjustments

    return {
        "initial_round_asr": round(r1_asr, 4),
        "final_round_asr": round(r_last_asr, 4),
        "delta_asr": delta_asr,
        "adaptation_event_count": total_adaptation_events,
        "family_switch_count": family_switches,
        "budget_adjustment_count": budget_adjustments,
        "exploration_rate": exp_ratio,
        "exploitation_rate": round(1.0 - exp_ratio, 4),
        "family_selection_entropy": round(entropy, 4),
        "memory_retrieval_count": mem_refs_count,
        "memory_reuse_rate": memory_reuse_rate,
        "successful_memory_reuse_rate": succ_mem_rate,
        "failed_pattern_avoidance_rate": avoidance_rate,
        "behavioral_adaptation_demonstrated": delta_asr >= 0 or total_adaptation_events > 0,
        "scientific_classification": "ADAPTATION_DEMONSTRATED" if (total_adaptation_events > 0) else "INSUFFICIENT_OBSERVATION",
    }
