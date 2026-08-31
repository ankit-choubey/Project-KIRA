"""ADV-002 Swarm Campaign State and Multi-Round Orchestration.

Manages sequential multi-round adversarial attack campaigns across target transactions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from mcdl.research.advanced.adv002.agents import AgentState, SwarmAgent
from mcdl.schemas import Transaction


@dataclass
class CampaignRound:
    """Record of a single executed round within an adversarial campaign."""

    campaign_id: str
    round_number: int
    agent_id: str
    target_txn_id: str
    family: str
    query_budget: int
    queries_used: int
    evasion: bool
    outcome: str
    blue_score: float
    blue_decision: str
    perturbation_distance: float | None
    reward: float
    is_exploration: bool
    memory_references: list[str]
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CampaignState:
    """Stateful tracking container for an ongoing multi-agent attack campaign."""

    campaign_id: str
    target_txn_id: str
    max_rounds: int
    current_round: int = 0
    cumulative_attacks: int = 0
    cumulative_successes: int = 0
    cumulative_failures: int = 0
    cumulative_queries: int = 0
    best_perturbation_distance: float | None = None
    last_family: str | None = None
    last_budget: int | None = None
    last_outcome: str | None = None
    last_blue_decision: str | None = None
    last_blue_score: float | None = None
    agent_states: dict[str, dict[str, Any]] = field(default_factory=dict)
    round_history: list[dict[str, Any]] = field(default_factory=list)
    adaptation_events: list[dict[str, Any]] = field(default_factory=list)
    is_completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def record_round(self, round_data: CampaignRound, agent: SwarmAgent) -> None:
        """Appends an executed round and updates state transitions and adaptation events."""
        self.current_round = round_data.round_number
        self.cumulative_attacks += 1
        self.cumulative_queries += round_data.queries_used

        # Check for adaptation events
        if self.last_family is not None and self.last_family != round_data.family:
            self.adaptation_events.append({
                "round": round_data.round_number,
                "type": "FAMILY_SWITCH",
                "from_family": self.last_family,
                "to_family": round_data.family,
                "prior_outcome": self.last_outcome,
            })

        if self.last_budget is not None and self.last_budget != round_data.query_budget:
            self.adaptation_events.append({
                "round": round_data.round_number,
                "type": "BUDGET_ADJUSTMENT",
                "from_budget": self.last_budget,
                "to_budget": round_data.query_budget,
                "prior_outcome": self.last_outcome,
            })

        if round_data.evasion:
            self.cumulative_successes += 1
            if round_data.perturbation_distance is not None:
                if self.best_perturbation_distance is None or round_data.perturbation_distance < self.best_perturbation_distance:
                    self.best_perturbation_distance = round_data.perturbation_distance
        else:
            self.cumulative_failures += 1

        self.last_family = round_data.family
        self.last_budget = round_data.query_budget
        self.last_outcome = round_data.outcome
        self.last_blue_decision = round_data.blue_decision
        self.last_blue_score = round_data.blue_score

        self.round_history.append(round_data.to_dict())
        self.agent_states[agent.agent_id] = agent.get_state().to_dict()

        if self.current_round >= self.max_rounds:
            self.is_completed = True


class CampaignManager:
    """Manages active campaigns across target transactions."""

    def __init__(self, max_rounds_per_campaign: int = 5) -> None:
        self.max_rounds = max_rounds_per_campaign
        self.campaigns: dict[str, CampaignState] = {}

    def create_campaign(self, target_txn: Transaction, campaign_index: int = 1) -> CampaignState:
        """Initializes a new stateful campaign for a specific target transaction."""
        campaign_id = f"cmp_adv002_{campaign_index:04d}_{target_txn.txn_id}"
        state = CampaignState(
            campaign_id=campaign_id,
            target_txn_id=target_txn.txn_id,
            max_rounds=self.max_rounds,
        )
        self.campaigns[campaign_id] = state
        return state
