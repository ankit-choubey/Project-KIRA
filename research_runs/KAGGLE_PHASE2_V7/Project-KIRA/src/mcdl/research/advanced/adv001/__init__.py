"""ADV-001: Large-Scale Adversarial Population Research Module."""

from mcdl.research.advanced.adv001.evaluator import (
    AttackAttemptResult,
    compute_bootstrap_ci,
    compute_population_statistics,
    evaluate_single_attempt,
)
from mcdl.research.advanced.adv001.population import AttackPlan, generate_population_plans
from mcdl.research.advanced.adv001.runner import run_adv001
from mcdl.research.advanced.adv001.storage import CheckpointManagerADV001

__all__ = [
    "run_adv001",
    "AttackPlan",
    "generate_population_plans",
    "evaluate_single_attempt",
    "AttackAttemptResult",
    "compute_population_statistics",
    "compute_bootstrap_ci",
    "CheckpointManagerADV001",
]
