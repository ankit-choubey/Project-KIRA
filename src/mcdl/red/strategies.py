"""Domain-Specific Attack Mutation Strategies for the 5 Red Team Families.

Generates physically constrained candidate mutations without cheating or bypassing invariants.
"""

from __future__ import annotations

import numpy as np
from mcdl.schemas import AttackFamily, Channel, Customer, Mandate, Merchant, Transaction


def mutate_burst_drain(
    txn: Transaction,
    customer: Customer,
    rng: np.random.Generator,
    query_idx: int,
) -> Transaction:
    """Burst Drain: Rapid extraction attempting to stay just below burst thresholds."""
    # Scale amount down progressively across queries
    amount_scales = [0.85, 0.70, 0.55, 0.40, 0.25, 0.15]
    scale = amount_scales[query_idx % len(amount_scales)]
    noise = float(rng.uniform(0.92, 1.05))
    new_amount = max(1.0, round(txn.amount * scale * noise, 2))

    # Keep amount <= available credit
    new_amount = min(new_amount, txn.available_credit)

    # Test cleaner auth and mobile wallet / card channels
    channels = [Channel.MOBILE_WALLET, Channel.ECOMMERCE, Channel.CARD_PRESENT]
    new_channel = channels[query_idx % len(channels)]

    return txn.model_copy(update={
        "amount": float(new_amount),
        "channel": new_channel,
        "auth_failed_count": 0 if query_idx > 0 else txn.auth_failed_count,
    })


def mutate_slow_siphon(
    txn: Transaction,
    customer: Customer,
    rng: np.random.Generator,
    query_idx: int,
) -> Transaction:
    """Slow Siphon: Micro-transactions designed to stay far beneath amount and velocity radars."""
    # Micro amounts relative to customer baseline
    micro_targets = [
        round(np.exp(customer.mean_log_amount * 0.7), 2),
        round(np.exp(customer.mean_log_amount * 0.5), 2),
        25.0,
        14.99,
        9.99,
        4.99,
    ]
    target = micro_targets[query_idx % len(micro_targets)]
    new_amount = max(1.0, min(float(target), txn.available_credit))

    channels = [Channel.RECURRING, Channel.ECOMMERCE, Channel.MOBILE_WALLET]
    new_channel = channels[query_idx % len(channels)]

    return txn.model_copy(update={
        "amount": float(new_amount),
        "channel": new_channel,
        "auth_failed_count": 0,
    })


def mutate_geo_hop(
    txn: Transaction,
    customer: Customer,
    merchants: dict[str, Merchant],
    rng: np.random.Generator,
    query_idx: int,
) -> Transaction:
    """Geo Hop: Perturbs coordinates and merchant selection within realistic physical distance."""
    merch_list = list(merchants.values())

    # Shift location closer to customer home or within reasonable driving radius (< 50 km)
    radii_deg = [0.02, 0.05, 0.10, 0.20, 0.35]
    radius = radii_deg[query_idx % len(radii_deg)]

    angle = float(rng.uniform(0, 2 * np.pi))
    new_lat = float(customer.home_lat + radius * np.cos(angle))
    new_lon = float(customer.home_lon + radius * np.sin(angle))

    # Pick a realistic merchant in that area
    m = merch_list[int(rng.integers(0, len(merch_list)))]

    return txn.model_copy(update={
        "lat": new_lat,
        "lon": new_lon,
        "merchant_id": m.merchant_id,
        "mcc": m.mcc,
        "channel": Channel.CARD_PRESENT if query_idx % 2 == 0 else Channel.MOBILE_WALLET,
    })


def mutate_agent_subversion(
    txn: Transaction,
    customer: Customer,
    mandates: dict[str, Mandate],
    rng: np.random.Generator,
    query_idx: int,
) -> Transaction:
    """Agent Subversion: Exploits autonomous agent delegation channel by adhering to mandate rules."""
    agent_id = f"agent_{customer.customer_id}"
    mandate_id = f"mnd_{customer.customer_id}"

    # If customer has a registered mandate, conform to its bounds
    if mandate_id in mandates:
        m = mandates[mandate_id]
        scale = [0.90, 0.75, 0.50, 0.30][query_idx % 4]
        new_amount = max(1.0, min(round(m.max_amount * scale, 2), txn.available_credit))
        allowed_mcc = m.allowed_mcc[0] if m.allowed_mcc else "5411"
    else:
        new_amount = max(1.0, min(round(np.exp(customer.mean_log_amount), 2), txn.available_credit))
        allowed_mcc = "5411"

    return txn.model_copy(update={
        "channel": Channel.AGENT,
        "agent_id": agent_id,
        "mandate_id": mandate_id,
        "amount": float(new_amount),
        "mcc": allowed_mcc,
        "auth_failed_count": 0,
    })


def mutate_cross_merchant_fanout(
    txn: Transaction,
    customer: Customer,
    merchants: dict[str, Merchant],
    rng: np.random.Generator,
    query_idx: int,
) -> Transaction:
    """Cross Merchant Fanout: Distributes spend across low-risk merchant categories (grocery, pharmacy, utility)."""
    low_risk_mccs = ["5411", "5912", "4900", "5311", "5814"]
    target_mcc = low_risk_mccs[query_idx % len(low_risk_mccs)]

    # Find merchant matching this MCC or pick one and assign MCC
    matching = [m for m in merchants.values() if m.mcc == target_mcc]
    if matching:
        m = matching[int(rng.integers(0, len(matching)))]
    else:
        m = list(merchants.values())[int(rng.integers(0, len(merchants)))]

    # Moderate amount matching grocery/pharmacy baskets
    new_amount = max(1.0, min(round(float(np.exp(customer.mean_log_amount * 0.9)), 2), txn.available_credit))

    return txn.model_copy(update={
        "merchant_id": m.merchant_id,
        "mcc": m.mcc,
        "amount": float(new_amount),
        "channel": Channel.CARD_PRESENT if query_idx % 2 == 0 else Channel.ECOMMERCE,
    })


def generate_candidate_mutation(
    family: AttackFamily,
    source_txn: Transaction,
    customer: Customer,
    merchants: dict[str, Merchant],
    mandates: dict[str, Mandate],
    rng: np.random.Generator,
    query_idx: int,
) -> Transaction:
    """Dispatches to the appropriate attack family mutation generator."""
    if family == AttackFamily.BURST_DRAIN or family == AttackFamily.R2_VELOCITY_BURST:
        return mutate_burst_drain(source_txn, customer, rng, query_idx)
    elif family == AttackFamily.SLOW_SIPHON or family == AttackFamily.R3_LOW_AND_SLOW:
        return mutate_slow_siphon(source_txn, customer, rng, query_idx)
    elif family == AttackFamily.GEO_HOP:
        return mutate_geo_hop(source_txn, customer, merchants, rng, query_idx)
    elif family == AttackFamily.AGENT_SUBVERSION or family == AttackFamily.R8_INTENT_DRIFT:
        return mutate_agent_subversion(source_txn, customer, mandates, rng, query_idx)
    elif family == AttackFamily.CROSS_MERCHANT_FANOUT or family == AttackFamily.R4_MULE_RING:
        return mutate_cross_merchant_fanout(source_txn, customer, merchants, rng, query_idx)
    else:
        # Default fallback to burst drain
        return mutate_burst_drain(source_txn, customer, rng, query_idx)
