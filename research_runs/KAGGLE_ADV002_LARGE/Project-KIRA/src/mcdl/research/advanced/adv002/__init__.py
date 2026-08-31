"""ADV-002 Stateful Adversarial Swarm Research Module."""

from mcdl.research.advanced.adv002.agents import (
    AgentRole,
    AgentState,
    SwarmAgent,
    create_canonical_agent_swarm,
)
from mcdl.research.advanced.adv002.campaign import (
    CampaignManager,
    CampaignRound,
    CampaignState,
)
from mcdl.research.advanced.adv002.evaluator import (
    RewardBreakdown,
    SwarmAttemptResult,
    SwarmEvaluator,
    compute_adaptation_metrics,
    compute_reward,
    compute_swarm_metrics,
)
from mcdl.research.advanced.adv002.memory import (
    MemoryQuery,
    MemoryRecord,
    SharedAttackMemory,
)
from mcdl.research.advanced.adv002.policy import (
    DeterministicAdaptivePolicy,
    PolicyAction,
    PolicyConfig,
)
from mcdl.research.advanced.adv002.runner import (
    ADV002Runner,
    ADV002Scale,
    run_adv002,
)
from mcdl.research.advanced.adv002.scheduler import (
    SwarmConfig,
    SwarmScheduler,
)
from mcdl.research.advanced.adv002.storage import (
    ADV002Storage,
)

__all__ = [
    "AgentRole",
    "AgentState",
    "SwarmAgent",
    "create_canonical_agent_swarm",
    "CampaignManager",
    "CampaignRound",
    "CampaignState",
    "RewardBreakdown",
    "SwarmAttemptResult",
    "SwarmEvaluator",
    "compute_reward",
    "compute_swarm_metrics",
    "compute_adaptation_metrics",
    "MemoryQuery",
    "MemoryRecord",
    "SharedAttackMemory",
    "DeterministicAdaptivePolicy",
    "PolicyAction",
    "PolicyConfig",
    "SwarmScheduler",
    "SwarmConfig",
    "ADV002Runner",
    "ADV002Scale",
    "run_adv002",
    "ADV002Storage",
]
