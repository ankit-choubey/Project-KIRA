"""ADV-002 Stateful Adversarial Attacker Agents.

Implements specialized deterministic stateful agents with isolated histories
and distinct attack-family biases.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from mcdl.red.evaluator import CANONICAL_FAMILIES
from mcdl.schemas import AttackFamily


class AgentRole(str, Enum):
    VELOCITY_SPECIALIST = "velocity_specialist"
    GEO_SPECIALIST = "geo_specialist"
    MERCHANT_SPECIALIST = "merchant_specialist"
    AGENT_SUBVERSION_SPECIALIST = "agent_subversion_specialist"
    HYBRID_ADAPTIVE = "hybrid_adaptive"


@dataclass
class AgentState:
    """Serializable snapshot of an individual agent's private state."""

    agent_id: str
    role: str
    seed: int
    family_preference: list[str]
    cumulative_attacks: int
    cumulative_successes: int
    cumulative_failures: int
    cumulative_queries: int
    cumulative_reward: float
    recent_outcomes: list[str]
    recent_rewards: list[float]
    current_strategy_state: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SwarmAgent:
    """Stateful adversarial agent participating in a multi-agent attack campaign."""

    def __init__(
        self,
        agent_id: str,
        role: AgentRole | str,
        seed: int,
        family_preference: list[AttackFamily] | None = None,
        default_budget: int = 20,
    ) -> None:
        self.agent_id = agent_id
        self.role = AgentRole(role) if isinstance(role, str) else role
        self.seed = seed
        self.default_budget = default_budget

        if family_preference is not None:
            self.family_preference = family_preference
        else:
            self.family_preference = self._get_default_preferences(self.role)

        self.action_history: list[dict[str, Any]] = []
        self.reward_history: list[float] = []
        self.cumulative_attacks: int = 0
        self.cumulative_successes: int = 0
        self.cumulative_failures: int = 0
        self.cumulative_queries: int = 0
        self.cumulative_reward: float = 0.0
        self.current_strategy_state: dict[str, Any] = {
            "preferred_budget": default_budget,
            "last_evasion_distance": None,
            "adaptation_count": 0,
        }

    @staticmethod
    def _get_default_preferences(role: AgentRole) -> list[AttackFamily]:
        if role == AgentRole.VELOCITY_SPECIALIST:
            return [AttackFamily.BURST_DRAIN, AttackFamily.SLOW_SIPHON]
        elif role == AgentRole.GEO_SPECIALIST:
            return [AttackFamily.GEO_HOP]
        elif role == AgentRole.MERCHANT_SPECIALIST:
            return [AttackFamily.CROSS_MERCHANT_FANOUT]
        elif role == AgentRole.AGENT_SUBVERSION_SPECIALIST:
            return [AttackFamily.AGENT_SUBVERSION]
        elif role == AgentRole.HYBRID_ADAPTIVE:
            return list(CANONICAL_FAMILIES)
        return list(CANONICAL_FAMILIES)

    def record_attempt_result(
        self,
        round_number: int,
        target_txn_id: str,
        family: AttackFamily,
        budget: int,
        queries_used: int,
        evasion: bool,
        outcome: str,
        blue_score: float,
        blue_decision: str,
        perturbation_distance: float | None,
        reward: float,
        memory_refs: list[str],
    ) -> None:
        """Updates agent internal private state with outcome of an attack attempt."""
        self.cumulative_attacks += 1
        self.cumulative_queries += queries_used
        self.cumulative_reward += reward
        self.reward_history.append(reward)

        if evasion:
            self.cumulative_successes += 1
            if perturbation_distance is not None:
                self.current_strategy_state["last_evasion_distance"] = perturbation_distance
        else:
            self.cumulative_failures += 1

        action_record = {
            "round_number": round_number,
            "target_transaction_id": target_txn_id,
            "family": family.value,
            "query_budget": budget,
            "queries_used": queries_used,
            "evasion": evasion,
            "outcome": outcome,
            "blue_score": blue_score,
            "blue_decision": blue_decision,
            "perturbation_distance": perturbation_distance,
            "reward": reward,
            "memory_refs": memory_refs,
        }
        self.action_history.append(action_record)

    def get_state(self) -> AgentState:
        """Returns isolated immutable snapshot of the agent's current state."""
        return AgentState(
            agent_id=self.agent_id,
            role=self.role.value,
            seed=self.seed,
            family_preference=[f.value for f in self.family_preference],
            cumulative_attacks=self.cumulative_attacks,
            cumulative_successes=self.cumulative_successes,
            cumulative_failures=self.cumulative_failures,
            cumulative_queries=self.cumulative_queries,
            cumulative_reward=round(self.cumulative_reward, 4),
            recent_outcomes=[a["outcome"] for a in self.action_history[-10:]],
            recent_rewards=[round(r, 4) for r in self.reward_history[-10:]],
            current_strategy_state=dict(self.current_strategy_state),
        )


def create_canonical_agent_swarm(base_seed: int = 20260831) -> list[SwarmAgent]:
    """Instantiates the 5 canonical specialized swarm agents with distinct deterministic seeds."""
    configs = [
        (AgentRole.VELOCITY_SPECIALIST, "agent_velocity_01", 101),
        (AgentRole.GEO_SPECIALIST, "agent_geo_01", 202),
        (AgentRole.MERCHANT_SPECIALIST, "agent_merchant_01", 303),
        (AgentRole.AGENT_SUBVERSION_SPECIALIST, "agent_subversion_01", 404),
        (AgentRole.HYBRID_ADAPTIVE, "agent_hybrid_01", 505),
    ]

    agents: list[SwarmAgent] = []
    for role, agent_id, offset in configs:
        agent_seed = int((base_seed + offset * 7919) % (2**31 - 1))
        agents.append(
            SwarmAgent(
                agent_id=agent_id,
                role=role,
                seed=agent_seed,
            )
        )

    return agents
