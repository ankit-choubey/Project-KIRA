"""ADV-001 Adversarial Attack Population Generator.

Generates a deterministic, reproducible population of 10,000 constrained attack plans
across canonical Red attack families and query budgets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import numpy as np

from mcdl.red.evaluator import CANONICAL_FAMILIES
from mcdl.schemas import AttackFamily, Customer, Mandate, Merchant, Transaction


@dataclass
class AttackPlan:
    """Specification for an individual attack evaluation attempt."""

    attack_id: str
    family: AttackFamily
    strategy_name: str
    seed: int
    parent_attack_id: str | None
    query_budget: int
    source_txn: Transaction
    customer: Customer


def generate_population_plans(
    candidate_transactions: list[Transaction],
    customers: dict[str, Customer],
    target_count: int = 10000,
    base_seed: int = 20260831,
    budgets: list[int] | None = None,
    families: list[AttackFamily] | None = None,
) -> list[AttackPlan]:
    """Generates a deterministic plan for target_count attack attempts.

    Args:
        candidate_transactions: Blocked/suspicious source transactions to attack from.
        customers: Dictionary of customer profiles.
        target_count: Total target population size (default: 10,000).
        base_seed: Master deterministic RNG seed.
        budgets: Evaluated query budgets (default: [1, 5, 20, 100]).
        families: Evaluated attack families (default: 5 canonical families).

    Returns:
        list of AttackPlan items.
    """
    if budgets is None:
        budgets = [1, 5, 20, 100]
    if families is None:
        families = CANONICAL_FAMILIES

    if not candidate_transactions:
        raise ValueError("Cannot generate attack population from empty candidate transactions list")

    plans: list[AttackPlan] = []
    n_txns = len(candidate_transactions)
    n_fams = len(families)
    n_budgets = len(budgets)

    strategy_names = {
        AttackFamily.BURST_DRAIN: "mutate_burst_drain",
        AttackFamily.SLOW_SIPHON: "mutate_slow_siphon",
        AttackFamily.GEO_HOP: "mutate_geo_hop",
        AttackFamily.AGENT_SUBVERSION: "mutate_agent_subversion",
        AttackFamily.CROSS_MERCHANT_FANOUT: "mutate_cross_merchant_fanout",
    }

    # Deterministic sequence generation
    for idx in range(target_count):
        # Round-robin distribution across transactions, families, and budgets
        txn_idx = idx % n_txns
        fam_idx = (idx // n_txns) % n_fams
        budget_idx = (idx // (n_txns * n_fams)) % n_budgets

        source_txn = candidate_transactions[txn_idx]
        family = families[fam_idx]
        budget = budgets[budget_idx]
        strategy = strategy_names.get(family, "mutate_burst_drain")

        # Deterministic attempt-specific seed derived from base_seed and index
        attempt_seed = int((base_seed + idx * 7919 + fam_idx * 31 + budget * 101) % (2**31 - 1))

        customer = customers.get(source_txn.customer_id)
        if customer is None:
            # Create synthetic fallback customer if missing from map
            customer = Customer(
                customer_id=source_txn.customer_id,
                archetype="standard",
                home_lat=source_txn.lat,
                home_lon=source_txn.lon,
                account_opened=source_txn.timestamp,
                credit_limit=max(5000.0, source_txn.amount * 2.0),
                mean_log_amount=float(np.log(max(10.0, source_txn.amount))),
                std_log_amount=0.8,
                daily_txn_rate=2.0,
            )

        attack_id = f"atk_adv001_{idx + 1:06d}"

        plans.append(
            AttackPlan(
                attack_id=attack_id,
                family=family,
                strategy_name=strategy,
                seed=attempt_seed,
                parent_attack_id=None,
                query_budget=budget,
                source_txn=source_txn,
                customer=customer,
            )
        )

    return plans
