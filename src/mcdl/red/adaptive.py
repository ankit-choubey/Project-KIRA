"""Adaptive Red Team Search Engine.

Implements genuine adversarial adaptation driven by Blue WeaknessProfiles.
Dynamically re-seeds mutation distributions, biases parameter exploration towards
observed defensive blind spots, generates novel non-memorized variants, and
enforces strict query budgets and mutability masks.
"""

from __future__ import annotations

import copy
from typing import Any
import numpy as np

from mcdl.blue.model import BlueDetector
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.red.distance import compute_evasion_distance
from mcdl.red.mask import FAMILY_MUTABLE_FIELDS, check_mask_violations
from mcdl.red.search import AttackProvenance, validate_physical_candidate
from mcdl.red.strategies import (
    mutate_agent_subversion,
    mutate_burst_drain,
    mutate_cross_merchant_fanout,
    mutate_geo_hop,
    mutate_slow_siphon,
)
from mcdl.schemas import (
    AttackFamily,
    Channel,
    Customer,
    Decision,
    FailureCategory,
    Mandate,
    Merchant,
    Transaction,
    WeaknessProfile,
)


def adaptive_mutate_slow_siphon(
    txn: Transaction,
    customer: Customer,
    profile: WeaknessProfile | None,
    rng: np.random.Generator,
    query_idx: int,
) -> Transaction:
    """Adaptive Low-and-Slow mutation biased by observed Blue vulnerability patterns."""
    if profile and profile.frequent_mutations and profile.frequent_mutations.get("median_amount", 0) > 0:
        # Bias amounts around the observed evasive median amount with noise
        med_amt = profile.frequent_mutations["median_amount"]
        scale = float(rng.uniform(0.60, 1.25))
        new_amt = max(1.0, min(round(med_amt * scale, 2), txn.available_credit))
    else:
        # Standard progression
        targets = [25.0, 14.99, 9.99, 4.99, round(np.exp(customer.mean_log_amount * 0.5), 2)]
        new_amt = max(1.0, min(float(targets[query_idx % len(targets)]), txn.available_credit))

    # Test channels based on top observed channels if available
    if profile and profile.frequent_mutations and profile.frequent_mutations.get("top_channels"):
        top_chan = profile.frequent_mutations["top_channels"][0]
        try:
            new_channel = Channel(top_chan) if query_idx % 2 == 0 else Channel.RECURRING
        except ValueError:
            new_channel = Channel.RECURRING
    else:
        channels = [Channel.RECURRING, Channel.ECOMMERCE, Channel.MOBILE_WALLET]
        new_channel = channels[query_idx % len(channels)]

    return txn.model_copy(update={
        "amount": float(new_amt),
        "channel": new_channel,
        "auth_failed_count": 0,
    })


def adaptive_mutate_burst_drain(
    txn: Transaction,
    customer: Customer,
    profile: WeaknessProfile | None,
    rng: np.random.Generator,
    query_idx: int,
) -> Transaction:
    """Adaptive Burst Drain mutation testing tighter threshold boundaries."""
    # Scale down aggressively if Blue is catching large amounts
    if profile and FailureCategory.W1_VELOCITY_BLINDNESS.value in profile.category_distribution:
        # Fine-grained boundary probing near threshold
        scales = [0.45, 0.35, 0.28, 0.20, 0.12]
    else:
        scales = [0.85, 0.70, 0.55, 0.40, 0.25, 0.15]

    scale = scales[query_idx % len(scales)]
    noise = float(rng.uniform(0.95, 1.05))
    new_amt = max(1.0, min(round(txn.amount * scale * noise, 2), txn.available_credit))

    channels = [Channel.MOBILE_WALLET, Channel.ECOMMERCE, Channel.CARD_PRESENT]
    new_channel = channels[query_idx % len(channels)]

    return txn.model_copy(update={
        "amount": float(new_amt),
        "channel": new_channel,
        "auth_failed_count": 0,
    })


def adaptive_mutate_geo_hop(
    txn: Transaction,
    customer: Customer,
    merchants: dict[str, Merchant],
    profile: WeaknessProfile | None,
    rng: np.random.Generator,
    query_idx: int,
) -> Transaction:
    """Adaptive Geo Hop mutation testing realistic localized merchant clusters."""
    merch_list = list(merchants.values())

    # If geographic camouflage is high, use tighter realistic radii (< 30km)
    if profile and FailureCategory.W3_GEOGRAPHIC_CAMOUFLAGE.value in profile.category_distribution:
        radii_deg = [0.015, 0.03, 0.06, 0.12]
    else:
        radii_deg = [0.02, 0.05, 0.10, 0.20, 0.35]

    radius = radii_deg[query_idx % len(radii_deg)]
    angle = float(rng.uniform(0, 2 * np.pi))
    new_lat = float(customer.home_lat + radius * np.cos(angle))
    new_lon = float(customer.home_lon + radius * np.sin(angle))

    m = merch_list[int(rng.integers(0, len(merch_list)))]

    return txn.model_copy(update={
        "lat": new_lat,
        "lon": new_lon,
        "merchant_id": m.merchant_id,
        "mcc": m.mcc,
        "channel": Channel.CARD_PRESENT if query_idx % 2 == 0 else Channel.MOBILE_WALLET,
    })


def adaptive_mutate_agent_subversion(
    txn: Transaction,
    customer: Customer,
    mandates: dict[str, Mandate],
    profile: WeaknessProfile | None,
    rng: np.random.Generator,
    query_idx: int,
) -> Transaction:
    """Adaptive Agent Subversion conforming tightly to mandate bounds."""
    agent_id = f"agent_{customer.customer_id}"
    mandate_id = f"mnd_{customer.customer_id}"

    if mandate_id in mandates:
        m = mandates[mandate_id]
        scales = [0.95, 0.85, 0.65, 0.40] if profile else [0.90, 0.75, 0.50, 0.30]
        scale = scales[query_idx % len(scales)]
        new_amt = max(1.0, min(round(m.max_amount * scale, 2), txn.available_credit))
        allowed_mcc = m.allowed_mcc[0] if m.allowed_mcc else "5411"
    else:
        new_amt = max(1.0, min(round(np.exp(customer.mean_log_amount), 2), txn.available_credit))
        allowed_mcc = "5411"

    return txn.model_copy(update={
        "channel": Channel.AGENT,
        "agent_id": agent_id,
        "mandate_id": mandate_id,
        "amount": float(new_amt),
        "mcc": allowed_mcc,
        "auth_failed_count": 0,
    })


def adaptive_mutate_cross_merchant(
    txn: Transaction,
    customer: Customer,
    merchants: dict[str, Merchant],
    profile: WeaknessProfile | None,
    rng: np.random.Generator,
    query_idx: int,
) -> Transaction:
    """Adaptive Cross-Merchant Fanout testing lower-risk merchant categories."""
    low_risk_mccs = ["5411", "5912", "4900", "5311", "5814"]
    target_mcc = low_risk_mccs[query_idx % len(low_risk_mccs)]

    matching = [m for m in merchants.values() if m.mcc == target_mcc]
    if matching:
        m = matching[int(rng.integers(0, len(matching)))]
    else:
        m = list(merchants.values())[int(rng.integers(0, len(merchants)))]

    scale = [0.85, 0.70, 0.50, 0.30][query_idx % 4]
    new_amt = max(1.0, min(round(float(np.exp(customer.mean_log_amount * scale)), 2), txn.available_credit))

    return txn.model_copy(update={
        "merchant_id": m.merchant_id,
        "mcc": m.mcc,
        "amount": float(new_amt),
        "channel": Channel.CARD_PRESENT if query_idx % 2 == 0 else Channel.ECOMMERCE,
    })


class AdaptiveRedEngine:
    """Adaptive Red Team Search Engine driven by Blue Weakness Profiles."""

    def __init__(
        self,
        detector: BlueDetector,
        customers: dict[str, Customer],
        merchants: dict[str, Merchant],
        mandates: dict[str, Mandate],
        weakness_profile: WeaknessProfile | None = None,
    ) -> None:
        self.detector = detector
        self.customers = customers
        self.merchants = merchants
        self.mandates = mandates
        self.profile = weakness_profile

    def update_profile(self, profile: WeaknessProfile) -> None:
        """Updates weakness profile from previous round's failures."""
        self.profile = profile

    def generate_candidate(
        self,
        family: AttackFamily,
        source_txn: Transaction,
        customer: Customer,
        rng: np.random.Generator,
        query_idx: int,
    ) -> Transaction:
        """Generates candidate mutation using adaptive strategy."""
        if family == AttackFamily.BURST_DRAIN or family == AttackFamily.R2_VELOCITY_BURST:
            return adaptive_mutate_burst_drain(source_txn, customer, self.profile, rng, query_idx)
        elif family == AttackFamily.SLOW_SIPHON or family == AttackFamily.R3_LOW_AND_SLOW:
            return adaptive_mutate_slow_siphon(source_txn, customer, self.profile, rng, query_idx)
        elif family == AttackFamily.GEO_HOP:
            return adaptive_mutate_geo_hop(source_txn, customer, self.merchants, self.profile, rng, query_idx)
        elif family == AttackFamily.AGENT_SUBVERSION or family == AttackFamily.R8_INTENT_DRIFT:
            return adaptive_mutate_agent_subversion(source_txn, customer, self.mandates, self.profile, rng, query_idx)
        elif family == AttackFamily.CROSS_MERCHANT_FANOUT or family == AttackFamily.R4_MULE_RING:
            return adaptive_mutate_cross_merchant(source_txn, customer, self.merchants, self.profile, rng, query_idx)
        else:
            return adaptive_mutate_burst_drain(source_txn, customer, self.profile, rng, query_idx)

    def attack(
        self,
        source_txn: Transaction,
        family: AttackFamily,
        budget: int = 20,
        seed: int = 20260827,
        feature_extractor_state: StreamingFeatureExtractor | None = None,
        round_idx: int = 0,
    ) -> AttackProvenance:
        """Executes budgeted, constrained adaptive adversarial search."""
        rng = np.random.default_rng(seed)
        customer = self.customers.get(source_txn.customer_id)
        if customer is None:
            raise ValueError(f"Customer {source_txn.customer_id} not found")

        # 1. Baseline scoring under exact historical context
        if feature_extractor_state is not None:
            base_ext = feature_extractor_state.clone()
        else:
            base_ext = StreamingFeatureExtractor(customers=self.customers)

        base_feats = base_ext.extract(source_txn)
        base_decision = self.detector.score_transaction(source_txn, base_feats, mandates=self.mandates)

        orig_decision = base_decision.decision
        orig_risk = base_decision.calibrated_score

        atk_id = f"atk_r{round_idx}_{source_txn.txn_id}_{family.value}_b{budget}_s{seed}"

        if orig_decision == Decision.ALLOW:
            return AttackProvenance(
                attack_instance_id=atk_id,
                attack_family=family,
                source_txn_id=source_txn.txn_id,
                seed=seed,
                query_budget=budget,
                queries_used=0,
                mutations_attempted=0,
                valid_mutations=0,
                invalid_mutations=0,
                original_decision=orig_decision,
                final_decision=orig_decision,
                original_risk=orig_risk,
                final_risk=orig_risk,
                med=None,
                success=False,
                rejection_reasons=["SOURCE_ALREADY_ALLOWED"],
                best_candidate=source_txn,
            )

        allowed_mutable = FAMILY_MUTABLE_FIELDS.get(family, ["amount", "channel"])

        queries_used = 0
        mutations_attempted = 0
        valid_mutations = 0
        invalid_mutations = 0
        rejection_reasons: list[str] = []

        best_candidate: Transaction | None = None
        best_decision = orig_decision
        best_risk = orig_risk
        success = False

        # 2. Budgeted adaptive candidate search loop
        for q in range(budget):
            mutations_attempted += 1

            candidate = self.generate_candidate(
                family=family,
                source_txn=source_txn,
                customer=customer,
                rng=rng,
                query_idx=q,
            )

            # Check mutability mask violations
            mask_violations = check_mask_violations(source_txn, candidate, allowed_mutable)
            if mask_violations:
                invalid_mutations += 1
                rejection_reasons.extend(mask_violations)
                continue

            # Check physical validity
            physics_violations = validate_physical_candidate(
                candidate, customer, self.merchants, self.mandates
            )
            if physics_violations:
                invalid_mutations += 1
                rejection_reasons.extend(physics_violations)
                continue

            valid_mutations += 1
            queries_used += 1

            # Strict query budget contract
            if queries_used > budget:
                invalid_mutations += 1
                rejection_reasons.append("EXCEEDED_QUERY_BUDGET")
                break

            # Score candidate with Blue detector under exact historical context
            if feature_extractor_state is not None:
                cand_ext = feature_extractor_state.clone()
            else:
                cand_ext = StreamingFeatureExtractor(customers=self.customers)

            cand_feats = cand_ext.extract(candidate)
            cand_decision = self.detector.score_transaction(candidate, cand_feats, mandates=self.mandates)

            cand_score = cand_decision.calibrated_score
            cand_action = cand_decision.decision

            if cand_score < best_risk:
                best_risk = cand_score
                best_decision = cand_action
                best_candidate = candidate

            # Early stopping on successful evasion (ALLOW)
            if cand_action == Decision.ALLOW:
                # Check for non-zero mutation distance
                dist = compute_evasion_distance(source_txn, candidate)
                if dist > 1e-6:
                    success = True
                    best_candidate = candidate
                    best_decision = cand_action
                    best_risk = cand_score
                    break

        final_cand = best_candidate if success else None
        med = compute_evasion_distance(source_txn, final_cand) if (success and final_cand is not None) else None

        return AttackProvenance(
            attack_instance_id=atk_id,
            attack_family=family,
            source_txn_id=source_txn.txn_id,
            seed=seed,
            query_budget=budget,
            queries_used=queries_used,
            mutations_attempted=mutations_attempted,
            valid_mutations=valid_mutations,
            invalid_mutations=invalid_mutations,
            original_decision=orig_decision,
            final_decision=best_decision,
            original_risk=orig_risk,
            final_risk=best_risk,
            med=med,
            success=success,
            rejection_reasons=list(set(rejection_reasons)),
            best_candidate=best_candidate,
        )
