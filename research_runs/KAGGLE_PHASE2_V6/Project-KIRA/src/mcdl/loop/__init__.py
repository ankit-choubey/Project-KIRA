"""Adversarial Coevolution Loop & Generalisation Measurement."""

from mcdl.loop.challenger import ChallengerTrainer, evaluate_promotion
from mcdl.loop.coevolution import CoevolutionLoop, CoevolutionResult
from mcdl.loop.metrics import (
    FamilyGeneralisation,
    GeneralisationReport,
    compute_generalisation_metrics,
)
from mcdl.loop.replay import ReplayBuffer, ReplayRecord
from mcdl.loop.split import SeenHeldoutSplit, split_seen_heldout

__all__ = [
    "CoevolutionLoop",
    "CoevolutionResult",
    "ChallengerTrainer",
    "evaluate_promotion",
    "ReplayBuffer",
    "ReplayRecord",
    "SeenHeldoutSplit",
    "split_seen_heldout",
    "GeneralisationReport",
    "FamilyGeneralisation",
    "compute_generalisation_metrics",
]
