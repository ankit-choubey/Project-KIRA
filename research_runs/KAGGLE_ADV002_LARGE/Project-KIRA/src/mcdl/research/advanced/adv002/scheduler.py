"""ADV-002 Swarm Scheduler and Coordination Engine.

Coordinates multi-agent execution across campaigns and sequential rounds,
orchestrating memory queries, policy evaluations, and shared learning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from mcdl.research.advanced.adv002.agents import SwarmAgent
from mcdl.research.advanced.adv002.campaign import CampaignManager, CampaignRound, CampaignState
from mcdl.research.advanced.adv002.evaluator import SwarmAttemptResult, SwarmEvaluator
from mcdl.research.advanced.adv002.memory import SharedAttackMemory
from mcdl.research.advanced.adv002.policy import DeterministicAdaptivePolicy
from mcdl.schemas import Customer, Mandate, Merchant, Transaction


@dataclass
class SwarmConfig:
    """Configuration for a multi-agent swarm evaluation run."""

    n_campaigns: int = 1
    rounds_per_campaign: int = 5
    base_seed: int = 20260831
    checkpoint_every_round: bool = True


class SwarmScheduler:
    """Deterministic scheduler coordinating stateful adversarial agents."""

    def __init__(
        self,
        agents: list[SwarmAgent],
        memory: SharedAttackMemory,
        policy: DeterministicAdaptivePolicy,
        evaluator: SwarmEvaluator,
        customers: dict[str, Customer],
        merchants: dict[str, Merchant],
        mandates: dict[str, Mandate],
        config: SwarmConfig | None = None,
    ) -> None:
        self.agents = agents
        self.memory = memory
        self.policy = policy
        self.evaluator = evaluator
        self.customers = customers
        self.merchants = merchants
        self.mandates = mandates
        self.config = config or SwarmConfig()
        self.campaign_manager = CampaignManager(max_rounds_per_campaign=self.config.rounds_per_campaign)

    def execute_campaign_round(
        self,
        campaign: CampaignState,
        agent: SwarmAgent,
        source_txn: Transaction,
        round_number: int,
        attempt_index: int,
    ) -> SwarmAttemptResult:
        """Executes a single coordinated round for an agent within a campaign."""
        # 1. Deterministic attempt seed
        attempt_seed = int((agent.seed + round_number * 7919 + attempt_index * 31) % (2**31 - 1))

        # 2. Select policy action using shared memory and agent private history
        action = self.policy.select_action(
            agent_role=agent.role.value,
            family_preference=agent.family_preference,
            target_id=source_txn.txn_id,
            round_number=round_number,
            agent_action_history=agent.action_history,
            memory=self.memory,
            seed=attempt_seed,
        )

        attack_id = f"atk_adv002_{campaign.campaign_id}_{agent.agent_id}_r{round_number:02d}_{attempt_index:04d}"

        # 3. Evaluate attack attempt against Blue detector
        result = self.evaluator.evaluate_swarm_attempt(
            attack_id=attack_id,
            campaign_id=campaign.campaign_id,
            agent_id=agent.agent_id,
            round_number=round_number,
            source_txn=source_txn,
            family=action.family,
            strategy_name=action.strategy_name,
            budget=action.query_budget,
            seed=attempt_seed,
            is_exploration=action.is_exploration,
            memory_refs=action.memory_references,
            policy_metadata=action.to_dict(),
        )

        # 4. Update Agent private state (isolated)
        agent.record_attempt_result(
            round_number=round_number,
            target_txn_id=source_txn.txn_id,
            family=action.family,
            budget=action.query_budget,
            queries_used=result.queries_used,
            evasion=result.evasion,
            outcome=result.outcome,
            blue_score=result.blue_score,
            blue_decision=result.blue_decision,
            perturbation_distance=result.perturbation_distance,
            reward=result.reward,
            memory_refs=action.memory_references,
        )

        # 5. Record round in campaign state
        c_round = CampaignRound(
            campaign_id=campaign.campaign_id,
            round_number=round_number,
            agent_id=agent.agent_id,
            target_txn_id=source_txn.txn_id,
            family=result.family,
            query_budget=result.query_budget,
            queries_used=result.queries_used,
            evasion=result.evasion,
            outcome=result.outcome,
            blue_score=result.blue_score,
            blue_decision=result.blue_decision,
            perturbation_distance=result.perturbation_distance,
            reward=result.reward,
            is_exploration=action.is_exploration,
            memory_references=action.memory_references,
            timestamp=result.timestamp,
        )
        campaign.record_round(c_round, agent)

        # 6. Append to Shared Attack Memory (enabling immediate cross-agent adaptation)
        self.memory.append_adv002_record(result.to_memory_record())

        return result

    def run_campaign(
        self,
        target_txn: Transaction,
        campaign_index: int,
        round_callback: Callable[[CampaignState, SwarmAttemptResult], None] | None = None,
    ) -> list[SwarmAttemptResult]:
        """Runs all sequential rounds for all swarm agents on a target transaction."""
        campaign = self.campaign_manager.create_campaign(target_txn, campaign_index=campaign_index)
        campaign_results: list[SwarmAttemptResult] = []
        attempt_counter = 0

        for r in range(1, self.config.rounds_per_campaign + 1):
            if campaign.is_completed:
                break

            for agent in self.agents:
                attempt_counter += 1
                result = self.execute_campaign_round(
                    campaign=campaign,
                    agent=agent,
                    source_txn=target_txn,
                    round_number=r,
                    attempt_index=attempt_counter,
                )
                campaign_results.append(result)

                if round_callback is not None:
                    round_callback(campaign, result)

        return campaign_results
