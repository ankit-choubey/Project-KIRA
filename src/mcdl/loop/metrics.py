"""Generalisation & Coevolution Metrics.

Calculates ASR, ΔASR, Generalisation Retention (GR), and policy trade-off distributions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import numpy as np

from mcdl.red.search import AttackProvenance
from mcdl.schemas import AttackFamily, BlueMetrics, Decision, RedMetrics


@dataclass
class FamilyGeneralisation:
    family: AttackFamily
    seen_asr: float
    heldout_asr: float
    delta_seen_asr: float
    delta_heldout_asr: float
    mean_med: float


@dataclass
class GeneralisationReport:
    seen_asr: float
    heldout_asr: float
    delta_seen_asr: float
    delta_heldout_asr: float
    generalisation_retention: float
    families: dict[str, FamilyGeneralisation]
    policy_distribution: dict[str, float]
    blue_metrics: BlueMetrics
    red_metrics: RedMetrics


def compute_generalisation_metrics(
    baseline_seen: list[AttackProvenance],
    baseline_heldout: list[AttackProvenance],
    challenger_seen: list[AttackProvenance],
    challenger_heldout: list[AttackProvenance],
    challenger_blue_metrics: BlueMetrics,
    decision_counts: dict[str, int],
) -> GeneralisationReport:
    """Computes comprehensive generalization and coevolution metrics."""

    def _asr(attacks: list[AttackProvenance]) -> float:
        if not attacks:
            return 0.0
        successes = len([a for a in attacks if a.success])
        return float(round(successes / len(attacks), 4))

    base_seen_asr = _asr(baseline_seen)
    base_heldout_asr = _asr(baseline_heldout)
    chal_seen_asr = _asr(challenger_seen)
    chal_heldout_asr = _asr(challenger_heldout)

    delta_seen = float(round(base_seen_asr - chal_seen_asr, 4))
    delta_heldout = float(round(base_heldout_asr - chal_heldout_asr, 4))

    # Compute Generalisation Retention (GR)
    if abs(delta_seen) < 1e-6:
        gr = 1.0 if abs(delta_heldout) < 1e-6 else 0.0
    else:
        gr = float(round(delta_heldout / delta_seen, 4))

    # Family-level breakdowns
    all_families = [
        AttackFamily.BURST_DRAIN,
        AttackFamily.SLOW_SIPHON,
        AttackFamily.GEO_HOP,
        AttackFamily.AGENT_SUBVERSION,
        AttackFamily.CROSS_MERCHANT_FANOUT,
    ]
    family_stats: dict[str, FamilyGeneralisation] = {}

    for fam in all_families:
        b_s = [a for a in baseline_seen if a.attack_family == fam]
        b_h = [a for a in baseline_heldout if a.attack_family == fam]
        c_s = [a for a in challenger_seen if a.attack_family == fam]
        c_h = [a for a in challenger_heldout if a.attack_family == fam]

        fam_base_seen = _asr(b_s)
        fam_base_held = _asr(b_h)
        fam_chal_seen = _asr(c_s)
        fam_chal_held = _asr(c_h)

        meds = [a.med for a in c_s + c_h if a.success and a.med is not None]
        avg_med = float(round(np.mean(meds), 4)) if meds else 0.0

        family_stats[fam.value] = FamilyGeneralisation(
            family=fam,
            seen_asr=fam_chal_seen,
            heldout_asr=fam_chal_held,
            delta_seen_asr=float(round(fam_base_seen - fam_chal_seen, 4)),
            delta_heldout_asr=float(round(fam_base_held - fam_chal_held, 4)),
            mean_med=avg_med,
        )

    # Compute policy distribution percentages
    total_decisions = max(1, sum(decision_counts.values()))
    policy_dist = {
        k: float(round(v / total_decisions, 4)) for k, v in decision_counts.items()
    }

    # Extract all successful challenger MEDs
    all_meds = [a.med for a in challenger_seen + challenger_heldout if a.success and a.med is not None]
    overall_mean_med = float(round(np.mean(all_meds), 4)) if all_meds else 0.0

    # Build ASR by budget for RedMetrics
    budgets = ["1", "5", "20", "100"]
    asr_by_budget = {}
    for b in budgets:
        b_atks = [a for a in challenger_seen + challenger_heldout if str(a.query_budget) == b]
        asr_by_budget[b] = _asr(b_atks)

    red_metrics = RedMetrics(
        asr_by_budget=asr_by_budget,
        asr_seen_variants=chal_seen_asr,
        asr_heldout_variants=chal_heldout_asr,
        mean_evasion_distance=overall_mean_med,
        mask_violations=0,
        invalid_attacks=0,
    )

    return GeneralisationReport(
        seen_asr=chal_seen_asr,
        heldout_asr=chal_heldout_asr,
        delta_seen_asr=delta_seen,
        delta_heldout_asr=delta_heldout,
        generalisation_retention=gr,
        families=family_stats,
        policy_distribution=policy_dist,
        blue_metrics=challenger_blue_metrics,
        red_metrics=red_metrics,
    )
