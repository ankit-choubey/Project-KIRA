"""ADV-003: Adaptive Defense Curve & Anti-Forgetting Evaluation.

Closed-loop adversarial defense experiment evaluating whether Blue challengers
learn from validated attack failures across successive rounds without modifying
production baseline models.
"""

from mcdl.research.advanced.adv003.attacker import DeterministicAdaptiveRedAttacker
from mcdl.research.advanced.adv003.challenger import ChallengerDetector, PromotionGate
from mcdl.research.advanced.adv003.evaluator import ADV003Evaluator
from mcdl.research.advanced.adv003.knowledge import DefensiveKnowledgeStore
from mcdl.research.advanced.adv003.runner import ADV003Runner, run_adv003
from mcdl.research.advanced.adv003.schemas import (
    AntiForgettingStatus,
    DefensiveKnowledgeRecord,
    PromotionDecision,
    PromotionGateConfig,
)
from mcdl.research.advanced.adv003.storage import ADV003Storage

__all__ = [
    "ADV003Evaluator",
    "ADV003Runner",
    "ADV003Storage",
    "AntiForgettingStatus",
    "ChallengerDetector",
    "DefensiveKnowledgeRecord",
    "DefensiveKnowledgeStore",
    "DeterministicAdaptiveRedAttacker",
    "PromotionDecision",
    "PromotionGate",
    "PromotionGateConfig",
    "run_adv003",
]
