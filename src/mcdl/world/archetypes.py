"""Archetype behavioural profiles for synthetic world generation.

Calibrated to match realistic payment patterns and reference distributions.
"""

from __future__ import annotations

from dataclasses import dataclass
from mcdl.schemas import Archetype


@dataclass(frozen=True)
class ArchetypeProfile:
    archetype: Archetype
    share: float
    credit_limit_min: float
    credit_limit_max: float
    mean_log_amount_mu: float
    mean_log_amount_sigma: float
    std_log_amount_val: float
    daily_rate_min: float
    daily_rate_max: float
    ecom_prob: float
    mobile_prob: float
    card_present_prob: float
    agent_prob: float
    common_mccs: list[str]


# 4 archetypes with distinct behavioural parameters and realistic MCC sets
ARCHETYPE_PROFILES: dict[Archetype, ArchetypeProfile] = {
    Archetype.SALARIED_URBAN: ArchetypeProfile(
        archetype=Archetype.SALARIED_URBAN,
        share=0.45,
        credit_limit_min=3000.0,
        credit_limit_max=15000.0,
        mean_log_amount_mu=3.8,  # exp(3.8) ~ $45
        mean_log_amount_sigma=0.3,
        std_log_amount_val=0.8,
        daily_rate_min=1.2,
        daily_rate_max=3.5,
        ecom_prob=0.35,
        mobile_prob=0.35,
        card_present_prob=0.30,
        agent_prob=0.10,
        common_mccs=["5411", "5812", "5814", "5541", "5912", "4121", "5311"],  # Grocery, Dining, Fast food, Gas, Pharmacy, Ride, Dept
    ),
    Archetype.STUDENT: ArchetypeProfile(
        archetype=Archetype.STUDENT,
        share=0.25,
        credit_limit_min=500.0,
        credit_limit_max=2500.0,
        mean_log_amount_mu=2.8,  # exp(2.8) ~ $16
        mean_log_amount_sigma=0.25,
        std_log_amount_val=0.6,
        daily_rate_min=0.8,
        daily_rate_max=2.5,
        ecom_prob=0.55,
        mobile_prob=0.35,
        card_present_prob=0.10,
        agent_prob=0.04,
        common_mccs=["5814", "5499", "5942", "4899", "7832", "5812", "5399"],  # Fast food, Convenience, Books, Cable/Streaming, Cinema, Dining, General
    ),
    Archetype.SMALL_BUSINESS: ArchetypeProfile(
        archetype=Archetype.SMALL_BUSINESS,
        share=0.20,
        credit_limit_min=10000.0,
        credit_limit_max=50000.0,
        mean_log_amount_mu=5.2,  # exp(5.2) ~ $180
        mean_log_amount_sigma=0.5,
        std_log_amount_val=1.1,
        daily_rate_min=3.0,
        daily_rate_max=8.0,
        ecom_prob=0.40,
        mobile_prob=0.20,
        card_present_prob=0.40,
        agent_prob=0.15,
        common_mccs=["5045", "5085", "5111", "5943", "7399", "5411", "5541"],  # Computers, Industrial supplies, Stationery, Office, Business services, Grocery, Gas
    ),
    Archetype.HIGH_NET_WORTH: ArchetypeProfile(
        archetype=Archetype.HIGH_NET_WORTH,
        share=0.10,
        credit_limit_min=30000.0,
        credit_limit_max=150000.0,
        mean_log_amount_mu=5.8,  # exp(5.8) ~ $330
        mean_log_amount_sigma=0.6,
        std_log_amount_val=1.3,
        daily_rate_min=2.0,
        daily_rate_max=6.0,
        ecom_prob=0.30,
        mobile_prob=0.30,
        card_present_prob=0.40,
        agent_prob=0.20,
        common_mccs=["3000", "7011", "5812", "5651", "5944", "4511", "5311"],  # Airlines, Hotels, Fine Dining, Apparel, Jewelry, Airlines, Luxury Dept
    ),
}
