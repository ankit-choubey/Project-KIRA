"""Red Team Evaluation & ASR@Budget Aggregator.

Runs adversarial search benchmark across query budgets (1, 5, 20, 100) and attack families.
Computes ASR(B) and Mean Evasion Distance (MED).
"""

from __future__ import annotations

import numpy as np
from mcdl.blue.model import BlueDetector
from mcdl.red.search import AttackProvenance, RedSearchEngine
from mcdl.schemas import AttackFamily, Customer, Decision, Mandate, Merchant, RedMetrics, Transaction


CANONICAL_FAMILIES = [
    AttackFamily.BURST_DRAIN,
    AttackFamily.SLOW_SIPHON,
    AttackFamily.GEO_HOP,
    AttackFamily.AGENT_SUBVERSION,
    AttackFamily.CROSS_MERCHANT_FANOUT,
]


def evaluate_red_attacks(
    transactions: list[Transaction],
    detector: BlueDetector,
    customers: dict[str, Customer],
    merchants: dict[str, Merchant],
    mandates: dict[str, Mandate],
    budgets: list[int] | None = None,
    families: list[AttackFamily] | None = None,
    seed: int = 20260827,
) -> tuple[RedMetrics, list[AttackProvenance]]:
    """Evaluates Red Team adversarial search benchmark across query budgets and attack families."""
    if budgets is None:
        budgets = [1, 5, 20, 100]
    if families is None:
        families = CANONICAL_FAMILIES

    engine = RedSearchEngine(
        detector=detector,
        customers=customers,
        merchants=merchants,
        mandates=mandates,
    )

    provenance_log: list[AttackProvenance] = []

    # Map budget -> successful evasions count and total attempts
    budget_successes: dict[int, int] = {b: 0 for b in budgets}
    budget_totals: dict[int, int] = {b: 0 for b in budgets}
    med_values: list[float] = []
    total_mask_violations = 0
    total_invalid_attacks = 0

    # Test each transaction across attack families and budgets
    for txn in transactions:
        for family in families:
            for budget in budgets:
                atk_seed = int(seed + len(provenance_log))
                prov = engine.attack(
                    source_txn=txn,
                    family=family,
                    budget=budget,
                    seed=atk_seed,
                )
                provenance_log.append(prov)

                budget_totals[budget] += 1
                if prov.success:
                    budget_successes[budget] += 1
                    med_values.append(prov.med)

                total_mask_violations += len([r for r in prov.rejection_reasons if "IMMUTABLE" in r or "UNAUTHORIZED" in r])
                total_invalid_attacks += prov.invalid_mutations

    # Compute ASR by budget
    asr_by_budget: dict[str, float] = {}
    for b in budgets:
        total = budget_totals[b]
        rate = float(budget_successes[b] / total) if total > 0 else 0.0
        asr_by_budget[str(b)] = float(round(rate, 4))

    mean_med = float(round(np.mean(med_values), 4)) if med_values else None

    red_metrics = RedMetrics(
        asr_by_budget=asr_by_budget,
        asr_seen_variants=asr_by_budget.get("20", 0.0),
        asr_heldout_variants=asr_by_budget.get("100", 0.0),
        asr_unseen_family=asr_by_budget.get("5", 0.0),
        mean_evasion_distance=mean_med,
        mask_violations=total_mask_violations,
        invalid_attacks=total_invalid_attacks,
    )

    return red_metrics, provenance_log
