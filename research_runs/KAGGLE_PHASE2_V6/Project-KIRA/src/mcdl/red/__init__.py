"""Red Team Adversarial Mutation & Search Engine."""

from mcdl.red.distance import compute_evasion_distance
from mcdl.red.evaluator import CANONICAL_FAMILIES, evaluate_red_attacks
from mcdl.red.mask import FAMILY_MUTABLE_FIELDS, IMMUTABLE_FIELDS, check_mask_violations, get_mutability_mask
from mcdl.red.search import AttackProvenance, RedSearchEngine, validate_physical_candidate
from mcdl.red.strategies import generate_candidate_mutation

__all__ = [
    "RedSearchEngine",
    "AttackProvenance",
    "evaluate_red_attacks",
    "compute_evasion_distance",
    "check_mask_violations",
    "get_mutability_mask",
    "validate_physical_candidate",
    "generate_candidate_mutation",
    "IMMUTABLE_FIELDS",
    "FAMILY_MUTABLE_FIELDS",
    "CANONICAL_FAMILIES",
]
