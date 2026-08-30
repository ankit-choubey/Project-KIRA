"""Failure Analysis, Diagnosis & Weakness Profiling Engine.

Diagnoses successful Red evasions against Blue defense, maps failures to the W1..W12
taxonomy, computes boundary proximity, hardness, novelty, and priority scores,
and synthesizes actionable WeaknessProfiles to drive adaptive Red reseeding.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any
import numpy as np

from mcdl.red.search import AttackProvenance
from mcdl.schemas import (
    AttackFamily,
    BlueDecision,
    Customer,
    Decision,
    FailureCategory,
    FailureRecord,
    Transaction,
    WeaknessProfile,
)


class FailureAnalyzer:
    """Diagnoses evasion failures and synthesizes weakness profiles."""

    def __init__(
        self,
        w_hardness: float = 0.35,
        w_novelty: float = 0.25,
        w_boundary: float = 0.25,
        w_rarity: float = 0.15,
    ) -> None:
        self.w_hardness = w_hardness
        self.w_novelty = w_novelty
        self.w_boundary = w_boundary
        self.w_rarity = w_rarity

    def classify_categories(
        self,
        family: AttackFamily,
        source_txn: Transaction,
        candidate: Transaction,
        features: dict[str, float] | None = None,
        intent_drift_score: float | None = None,
    ) -> tuple[FailureCategory, list[FailureCategory]]:
        """Maps an evasion into primary and optional secondary failure categories."""
        secondary: list[FailureCategory] = []

        if family == AttackFamily.BURST_DRAIN or family == AttackFamily.R2_VELOCITY_BURST:
            primary = FailureCategory.W1_VELOCITY_BLINDNESS
            if candidate.channel.value in ("mobile_wallet", "ecommerce"):
                secondary.append(FailureCategory.W11_TEMPORAL_CAMOUFLAGE)

        elif family == AttackFamily.SLOW_SIPHON or family == AttackFamily.R3_LOW_AND_SLOW:
            primary = FailureCategory.W5_LOW_AND_SLOW
            secondary.append(FailureCategory.W11_TEMPORAL_CAMOUFLAGE)

        elif family == AttackFamily.GEO_HOP:
            primary = FailureCategory.W3_GEOGRAPHIC_CAMOUFLAGE
            if candidate.is_new_device:
                secondary.append(FailureCategory.W2_DEVICE_NOVELTY_BLINDNESS)

        elif family == AttackFamily.AGENT_SUBVERSION or family == AttackFamily.R8_INTENT_DRIFT:
            primary = FailureCategory.W7_INTENT_DRIFT
            secondary.append(FailureCategory.W10_AGENT_SWARM)

        elif family == AttackFamily.CROSS_MERCHANT_FANOUT or family == AttackFamily.R4_MULE_RING:
            primary = FailureCategory.W8_COORDINATED_MULTI_ACCOUNT
            secondary.append(FailureCategory.W4_MERCHANT_COLLUSION)

        else:
            primary = FailureCategory.W12_OPEN_SET_ANOMALY

        # Feature-driven secondary refinement
        if features:
            if features.get("is_new_device", 0.0) == 1.0 and FailureCategory.W2_DEVICE_NOVELTY_BLINDNESS not in secondary:
                secondary.append(FailureCategory.W2_DEVICE_NOVELTY_BLINDNESS)
            if features.get("cust_velocity_1h_count", 0.0) > 3.0 and FailureCategory.W1_VELOCITY_BLINDNESS not in secondary:
                secondary.append(FailureCategory.W1_VELOCITY_BLINDNESS)

        if intent_drift_score is not None and intent_drift_score > 0.25 and FailureCategory.W7_INTENT_DRIFT not in secondary and primary != FailureCategory.W7_INTENT_DRIFT:
            secondary.append(FailureCategory.W7_INTENT_DRIFT)

        return primary, secondary

    def diagnose_failure(
        self,
        prov: AttackProvenance,
        customer: Customer,
        features: dict[str, float],
        round_idx: int = 0,
        model_version: str = "0.1.0",
        known_failures: list[FailureRecord] | None = None,
    ) -> FailureRecord:
        """Diagnoses a single successful evasion and constructs a full FailureRecord."""
        candidate = prov.best_candidate
        if candidate is None:
            raise ValueError("Cannot diagnose failure without best_candidate transaction")

        primary_cat, secondary_cats = self.classify_categories(
            family=prov.attack_family,
            source_txn=candidate,
            candidate=candidate,
            features=features,
            intent_drift_score=features.get("intent_drift_score"),
        )

        # 1. Hardness: Evasions requiring few queries out of the budget are harder
        if prov.query_budget > 1:
            hardness = max(0.0, min(1.0, 1.0 - (prov.queries_used - 1) / max(1, prov.query_budget - 1)))
        else:
            hardness = 1.0

        # 2. Boundary Proximity: Calibrated scores close to 0.5 decision boundary
        # A calibrated score of 0.48 has proximity ~0.96; score 0.10 has proximity ~0.20
        boundary_proximity = max(0.0, min(1.0, 1.0 - abs(prov.final_risk - 0.5) * 2.0))

        # 3. Novelty: Feature distance relative to customer normal baseline
        # (normalized log amount delta and velocity delta)
        amt_delta = abs(np.log(max(1.0, candidate.amount)) - customer.mean_log_amount)
        novelty = float(min(1.0, amt_delta / max(1.0, customer.std_log_amount * 3.0)))

        # 4. Rarity: Inverse frequency among previously observed failures
        if known_failures:
            cat_counts = Counter(f.primary_failure_category.value for f in known_failures)
            freq = cat_counts.get(primary_cat.value, 0) / len(known_failures)
            rarity = float(max(0.0, 1.0 - freq))
        else:
            rarity = 1.0

        # Composite priority score
        priority = (
            self.w_hardness * hardness
            + self.w_novelty * novelty
            + self.w_boundary * boundary_proximity
            + self.w_rarity * rarity
        )

        mutable_fields = [
            f for f in ["amount", "channel", "merchant_id", "mcc", "lat", "lon", "auth_failed_count"]
            if hasattr(candidate, f)
        ]
        mutation_values = {
            f: getattr(candidate, f).value if hasattr(getattr(candidate, f), "value") else getattr(candidate, f)
            for f in mutable_fields
        }

        failure_id = f"fail_{prov.source_txn_id}_{prov.attack_family.value}_r{round_idx}_{prov.seed}"

        return FailureRecord(
            failure_id=failure_id,
            attack_id=prov.attack_instance_id,
            attack_family=prov.attack_family,
            world_id="world_a",
            base_transaction_id=prov.source_txn_id,
            model_version=model_version,
            feature_version="feat_v1_causal",
            policy_version="cost_router_v1",
            risk_score=float(prov.final_risk),
            calibrated_score=float(prov.final_risk),
            decision=prov.final_decision,
            detected=prov.final_decision != Decision.ALLOW,
            primary_failure_category=primary_cat,
            optional_secondary_categories=secondary_cats,
            mutable_fields=mutable_fields,
            mutation_values=mutation_values,
            mutation_distance=float(prov.med or 0.0),
            query_count=prov.queries_used,
            query_budget=prov.query_budget,
            attack_cost=float(round(prov.queries_used * 0.05 + (prov.med or 0.0) * 0.1, 4)),
            fidelity_score=1.0,
            novelty_score=float(round(novelty, 4)),
            hardness_score=float(round(hardness, 4)),
            boundary_proximity=float(round(boundary_proximity, 4)),
            rarity_score=float(round(rarity, 4)),
            priority_score=float(round(priority, 4)),
            intent_drift_score=features.get("intent_drift_score"),
            generator_version="0.7.0",
            timestamp=candidate.timestamp,
            seed=prov.seed,
            provenance={
                "source_txn_id": prov.source_txn_id,
                "mutations_attempted": prov.mutations_attempted,
                "valid_mutations": prov.valid_mutations,
                "invalid_mutations": prov.invalid_mutations,
                "original_risk": prov.original_risk,
                "original_decision": prov.original_decision.value,
                "rejection_reasons": prov.rejection_reasons,
            },
        )

    def synthesize_weakness_profile(
        self,
        failures: list[FailureRecord],
        round_idx: int = 0,
    ) -> WeaknessProfile:
        """Synthesizes high-level Blue WeaknessProfile to guide adaptive Red search."""
        if not failures:
            # Uniform fallback
            return WeaknessProfile(
                round_index=round_idx,
                total_failures=0,
                dominant_categories=[],
                category_distribution={},
                frequent_mutations={},
                near_boundary_count=0,
                high_value_attack_surfaces=[],
                rare_successful_patterns=[],
                reseeding_weights={
                    AttackFamily.BURST_DRAIN.value: 0.20,
                    AttackFamily.SLOW_SIPHON.value: 0.20,
                    AttackFamily.GEO_HOP.value: 0.20,
                    AttackFamily.AGENT_SUBVERSION.value: 0.20,
                    AttackFamily.CROSS_MERCHANT_FANOUT.value: 0.20,
                },
            )

        total = len(failures)
        cat_counts = Counter(f.primary_failure_category.value for f in failures)
        cat_dist = {k: round(v / total, 4) for k, v in cat_counts.items()}
        dominant = sorted(cat_dist.items(), key=lambda x: x[1], reverse=True)

        near_boundary = [f for f in failures if f.boundary_proximity >= 0.60]
        near_boundary_count = len(near_boundary)

        # High value surfaces: attack families with highest success / priority
        fam_priority: dict[str, list[float]] = {}
        for f in failures:
            fam_priority.setdefault(f.attack_family.value, []).append(f.priority_score)
        avg_fam_priority = {k: float(np.mean(v)) for k, v in fam_priority.items()}
        high_value_surfaces = sorted(avg_fam_priority.keys(), key=lambda k: avg_fam_priority[k], reverse=True)

        # Frequent mutation patterns
        amounts = [f.mutation_values.get("amount", 0.0) for f in failures if "amount" in f.mutation_values]
        channels = [f.mutation_values.get("channel", "") for f in failures if "channel" in f.mutation_values]
        frequent_mutations = {
            "mean_amount": float(round(np.mean(amounts), 2)) if amounts else 0.0,
            "median_amount": float(round(np.median(amounts), 2)) if amounts else 0.0,
            "top_channels": [c for c, _ in Counter(channels).most_common(3)],
        }

        # Rare patterns (priority > 0.70)
        rare_patterns = [
            {
                "failure_id": f.failure_id,
                "family": f.attack_family.value,
                "category": f.primary_failure_category.value,
                "priority": f.priority_score,
                "med": f.mutation_distance,
            }
            for f in sorted(failures, key=lambda x: x.priority_score, reverse=True)[:5]
        ]

        # Reseeding weights: Proportional to failure concentration + smoothing
        all_canonical_families = [
            AttackFamily.BURST_DRAIN.value,
            AttackFamily.SLOW_SIPHON.value,
            AttackFamily.GEO_HOP.value,
            AttackFamily.AGENT_SUBVERSION.value,
            AttackFamily.CROSS_MERCHANT_FANOUT.value,
        ]

        # Map failure categories to family weights
        family_scores: dict[str, float] = {fam: 0.10 for fam in all_canonical_families}  # 0.10 smoothing base
        for fam, prio in avg_fam_priority.items():
            if fam in family_scores:
                family_scores[fam] += prio * 2.0

        total_weight = sum(family_scores.values())
        reseeding_weights = {k: round(v / total_weight, 4) for k, v in family_scores.items()}

        return WeaknessProfile(
            round_index=round_idx,
            total_failures=total,
            dominant_categories=dominant,
            category_distribution=cat_dist,
            frequent_mutations=frequent_mutations,
            near_boundary_count=near_boundary_count,
            high_value_attack_surfaces=high_value_surfaces,
            rare_successful_patterns=rare_patterns,
            reseeding_weights=reseeding_weights,
        )
