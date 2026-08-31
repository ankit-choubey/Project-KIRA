"""ADV-002 Deterministic Adaptive Attacker Policy.

Implements inspectable, non-RL adaptive decision making balancing historical
memory exploitation and bounded exploration across attack families and query budgets.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import math
from typing import Any
import numpy as np

from mcdl.red.evaluator import CANONICAL_FAMILIES
from mcdl.research.advanced.adv002.memory import MemoryQuery, SharedAttackMemory
from mcdl.schemas import AttackFamily


@dataclass
class PolicyConfig:
    """Hyperparameters governing deterministic adaptive selection."""

    base_exploration_rate: float = 0.25
    min_exploration_rate: float = 0.05
    exploration_decay: float = 0.90
    family_weight_power: float = 2.0
    failure_penalty_weight: float = 0.40
    budget_options: list[int] = field(default_factory=lambda: [1, 5, 20, 100])
    default_budget: int = 20


@dataclass
class PolicyAction:
    """Structured decision output produced by the adaptive policy."""

    family: AttackFamily
    strategy_name: str
    query_budget: int
    is_exploration: bool
    selection_probabilities: dict[str, float]
    memory_references: list[str]
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "family": self.family.value,
            "strategy_name": self.strategy_name,
            "query_budget": self.query_budget,
            "is_exploration": self.is_exploration,
            "selection_probabilities": self.selection_probabilities,
            "memory_references": self.memory_references,
            "rationale": self.rationale,
        }


class DeterministicAdaptivePolicy:
    """Non-RL deterministic adaptive policy with inspectable reasoning."""

    STRATEGY_MAP = {
        AttackFamily.BURST_DRAIN: "mutate_burst_drain",
        AttackFamily.SLOW_SIPHON: "mutate_slow_siphon",
        AttackFamily.GEO_HOP: "mutate_geo_hop",
        AttackFamily.AGENT_SUBVERSION: "mutate_agent_subversion",
        AttackFamily.CROSS_MERCHANT_FANOUT: "mutate_cross_merchant_fanout",
    }

    def __init__(self, config: PolicyConfig | None = None) -> None:
        self.config = config or PolicyConfig()

    def get_exploration_rate(self, round_number: int) -> float:
        """Calculates decayed exploration rate for a given campaign round."""
        decayed = self.config.base_exploration_rate * (self.config.exploration_decay ** max(0, round_number - 1))
        return max(self.config.min_exploration_rate, min(1.0, decayed))

    def select_action(
        self,
        agent_role: str,
        family_preference: list[AttackFamily],
        target_id: str,
        round_number: int,
        agent_action_history: list[dict[str, Any]],
        memory: SharedAttackMemory,
        seed: int,
    ) -> PolicyAction:
        """Selects attack family and query budget deterministically based on memory and state."""
        rng = np.random.default_rng(seed)
        eps = self.get_exploration_rate(round_number)
        roll = rng.random()
        is_exploration = (roll < eps)

        all_families = list(CANONICAL_FAMILIES)
        failed_configs = memory.get_failed_configurations(target_id)
        failed_fams = {f["family"] for f in failed_configs}

        # 1. Compute empirical family scores from memory and agent preference
        family_scores: dict[str, float] = {}
        memory_refs: list[str] = []

        for fam in all_families:
            fam_str = fam.value
            global_asr = memory.get_family_success_rate(fam_str)
            target_asr = memory.get_family_success_rate(fam_str, target_id=target_id)

            # Combined score with higher weight on target-specific performance
            combined_asr = (target_asr * 0.7) + (global_asr * 0.3)
            pref_boost = 1.5 if fam in family_preference else 1.0
            fail_penalty = (1.0 - self.config.failure_penalty_weight) if fam_str in failed_fams else 1.0

            # Base score with floor to prevent complete starvation
            score = (combined_asr ** self.config.family_weight_power) * pref_boost * fail_penalty + 0.05
            family_scores[fam_str] = round(score, 6)

        # Normalize probabilities
        total_score = sum(family_scores.values())
        probs = {f: round(s / total_score, 6) for f, s in family_scores.items()}

        # 2. Select Family
        if is_exploration:
            # Deterministic exploration across eligible families
            fam_keys = sorted(family_scores.keys())
            chosen_fam_str = rng.choice(fam_keys)
            rationale = f"Exploration round (eps={eps:.3f}, roll={roll:.3f}): selected underrepresented family {chosen_fam_str}"
        else:
            # Exploitation: select highest probability with deterministic tie-breaking
            sorted_fams = sorted(family_scores.items(), key=lambda item: (-item[1], item[0]))
            chosen_fam_str = sorted_fams[0][0]
            rationale = f"Exploitation round: selected top-scoring family {chosen_fam_str} (score={family_scores[chosen_fam_str]:.4f})"

        chosen_family = next(f for f in all_families if f.value == chosen_fam_str)

        # 3. Retrieve Memory References
        best_records = memory.get_best_perturbations(chosen_fam_str, limit=3)
        memory_refs = [r.attack_id for r in best_records]

        # 4. Adaptive Budget Selection
        # If previous attempts on this family were blocked near threshold (e.g. Blue score 0.4-0.6), increase budget
        chosen_budget = self.config.default_budget
        recent_family_attempts = [
            a for a in agent_action_history
            if a.get("family") == chosen_fam_str and a.get("target_transaction_id") == target_id
        ]

        if recent_family_attempts:
            last_attempt = recent_family_attempts[-1]
            last_score = last_attempt.get("blue_score", 1.0)
            last_budget = last_attempt.get("query_budget", self.config.default_budget)

            if last_attempt.get("evasion", False):
                # If already evaded, attempt lower budget for efficiency
                chosen_budget = max(1, last_budget // 4)
                rationale += f"; downscaling budget to {chosen_budget} to minimize query cost on known evasion"
            elif last_score < 0.60 and last_budget < 100:
                # Borderline block/step-up: escalate budget
                chosen_budget = min(100, last_budget * 4 if last_budget > 1 else 5)
                rationale += f"; escalating budget to {chosen_budget} (borderline score={last_score:.3f})"
            elif last_score >= 0.90 and len(recent_family_attempts) >= 2:
                # Severe block with multiple tries: switch to minimal probe
                chosen_budget = 5
                rationale += f"; setting probe budget {chosen_budget} due to high resistance"

        strategy_name = self.STRATEGY_MAP.get(chosen_family, "mutate_burst_drain")

        return PolicyAction(
            family=chosen_family,
            strategy_name=strategy_name,
            query_budget=chosen_budget,
            is_exploration=is_exploration,
            selection_probabilities=probs,
            memory_references=memory_refs,
            rationale=rationale,
        )
