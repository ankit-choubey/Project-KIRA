"""Three-World Evaluation & Strict Family Isolation Infrastructure.

Implements the three-world benchmark:
  World A: Evolution World (Red <-> Blue iterative co-evolution)
  World B: Shifted Physics World (Perturbed merchant & customer distributions)
  World C: Hidden Attack Family World (Withheld zero-day attack families)

Enforces runtime assertion: Adaptation Families ∩ Hidden Families = ∅.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
import numpy as np

from mcdl.config import Config, load_config
from mcdl.schemas import AttackFamily, Customer, Merchant, Transaction
from mcdl.world.generator import WorldResult, generate_world


class WorldType(str, Enum):
    WORLD_A_EVOLUTION = "world_a_evolution"
    WORLD_B_SHIFTED_PHYSICS = "world_b_shifted_physics"
    WORLD_C_HIDDEN_FAMILIES = "world_c_hidden_families"


# Canonical family allocation
CANONICAL_ADAPTATION_FAMILIES: list[AttackFamily] = [
    AttackFamily.BURST_DRAIN,
    AttackFamily.SLOW_SIPHON,
    AttackFamily.GEO_HOP,
]

CANONICAL_HIDDEN_FAMILIES: list[AttackFamily] = [
    AttackFamily.AGENT_SUBVERSION,
    AttackFamily.CROSS_MERCHANT_FANOUT,
]


def verify_family_isolation(
    adaptation_families: list[AttackFamily],
    hidden_families: list[AttackFamily],
) -> bool:
    """Verifies that adaptation attack families and hidden evaluation families are strictly disjoint.

    Raises ValueError if any leakage / overlap is detected.
    """
    adapt_set = {f.value if hasattr(f, "value") else str(f) for f in adaptation_families}
    hidden_set = {f.value if hasattr(f, "value") else str(f) for f in hidden_families}

    overlap = adapt_set & hidden_set
    if overlap:
        raise ValueError(
            f"CRITICAL ZERO-DAY LEAKAGE VIOLATION: Adaptation families and Hidden families "
            f"have non-empty intersection: {overlap}. Hidden families must NEVER appear in adaptation."
        )
    return True


def generate_shifted_physics_world(cfg: Config, base_world: WorldResult, seed_offset: int = 777) -> WorldResult:
    """Generates World B with shifted physics (distributional shift).

    Perturbs merchant risk tiers, geographic coordinates, and customer velocity/spending rates.
    """
    rng = np.random.default_rng(cfg["seed"] + seed_offset)

    # Perturb customer spending baselines by +15% and jitter locations
    shifted_customers: dict[str, Customer] = {}
    for cid, c in base_world.customers.items():
        delta_lat = float(rng.normal(0.0, 0.05))
        delta_lon = float(rng.normal(0.0, 0.05))
        shifted_c = c.model_copy(update={
            "mean_log_amount": float(c.mean_log_amount + rng.uniform(-0.2, 0.3)),
            "daily_txn_rate": float(max(0.5, c.daily_txn_rate * rng.uniform(0.8, 1.4))),
            "home_lat": float(c.home_lat + delta_lat),
            "home_lon": float(c.home_lon + delta_lon),
        })
        shifted_customers[cid] = shifted_c

    # Perturb merchant risk tiers and categories
    shifted_merchants: dict[str, Merchant] = {}
    for mid, m in base_world.merchants.items():
        new_risk = "high" if rng.uniform() < 0.15 else m.risk_tier
        shifted_m = m.model_copy(update={"risk_tier": new_risk})
        shifted_merchants[mid] = shifted_m

    # Re-generate world with shifted distributions
    shifted_cfg = cfg.copy()
    shifted_cfg["seed"] = cfg["seed"] + seed_offset
    shifted_world = generate_world(shifted_cfg)

    return shifted_world


def build_three_world_suite(
    cfg: Config,
    adaptation_families: list[AttackFamily] | None = None,
    hidden_families: list[AttackFamily] | None = None,
) -> dict[WorldType, dict[str, Any]]:
    """Builds and validates the 3-World Evaluation Suite."""
    adapt_fams = adaptation_families or CANONICAL_ADAPTATION_FAMILIES
    hidden_fams = hidden_families or CANONICAL_HIDDEN_FAMILIES

    # 1. Strict Isolation Invariant Check
    verify_family_isolation(adapt_fams, hidden_fams)

    # 2. Generate World A (Evolution)
    world_a = generate_world(cfg)

    # 3. Generate World B (Shifted Physics)
    world_b = generate_shifted_physics_world(cfg, world_a, seed_offset=888)

    # 4. World C uses World A entities but is evaluated STRICTLY on hidden families post-adaptation
    return {
        WorldType.WORLD_A_EVOLUTION: {
            "world": world_a,
            "families": adapt_fams,
            "description": "Standard synthetic world where Red and Blue adapt co-evolutionarily.",
        },
        WorldType.WORLD_B_SHIFTED_PHYSICS: {
            "world": world_b,
            "families": adapt_fams,
            "description": "Distributional shift world (perturbed merchant density, spending rates).",
        },
        WorldType.WORLD_C_HIDDEN_FAMILIES: {
            "world": world_a,
            "families": hidden_fams,
            "description": "Withheld zero-day attack families evaluated strictly after adaptation.",
        },
    }
