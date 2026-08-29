"""Hard negative behaviors and base fraud generation.

Hard negatives are legitimate transactions designed to stress-test the detector:
without them, the model learns 'unusual == fraud' and generates false alarms.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import numpy as np

from mcdl.schemas import AttackFamily, Channel, Customer, HardNegative, Merchant


def sample_transaction_attributes(
    customer: Customer,
    merchants: dict[str, Merchant],
    ts: datetime,
    hard_neg_type: HardNegative = HardNegative.NONE,
    is_fraud: bool = False,
    mandates: dict[str, Mandate] | None = None,
    rng: np.random.Generator | None = None,
) -> dict:
    """Generates realistic transaction attributes for a customer event at time ts."""
    if rng is None:
        rng = np.random.default_rng(20260827)

    merch_list = list(merchants.values())

    # Default amount from customer log-normal distribution
    raw_amount = float(np.exp(rng.normal(customer.mean_log_amount, customer.std_log_amount)))
    amount = max(1.0, min(raw_amount, customer.credit_limit * 0.4))
    amount = round(amount, 2)

    # Default location is close to customer home (within ~20 km)
    # 1 deg lat ~ 111 km
    lat = float(customer.home_lat + rng.normal(0, 0.05))
    lon = float(customer.home_lon + rng.normal(0, 0.05))

    channel = Channel.CARD_PRESENT
    channel_p = rng.random()
    if channel_p < 0.35:
        channel = Channel.ECOMMERCE
    elif channel_p < 0.65:
        channel = Channel.MOBILE_WALLET
    elif channel_p < 0.70 and customer.has_agent:
        channel = Channel.AGENT

    m = rng.choice(merch_list)
    mcc = m.mcc
    merchant_id = m.merchant_id

    ip_prefix = f"{int(rng.integers(24, 210))}.{int(rng.integers(1, 255))}"
    device_id = f"dev_{customer.customer_id}_pri"
    is_new_device = False
    auth_failed_count = 0
    agent_id = None
    mandate_id = None

    # Handle Hard Negatives (human edge cases)
    if hard_neg_type == HardNegative.TRAVELLER:
        travel_mccs = ["3000", "7011", "5812", "4511"]
        mcc = str(rng.choice(travel_mccs))
        amount = round(amount * float(rng.uniform(1.5, 3.5)), 2)
        lat = float(lat + rng.uniform(4.0, 10.0) * rng.choice([-1, 1]))
        lon = float(lon + rng.uniform(4.0, 12.0) * rng.choice([-1, 1]))
        channel = Channel.CARD_PRESENT
        if rng.random() < 0.6:
            device_id = f"dev_{customer.customer_id}_travel"
            is_new_device = True

    elif hard_neg_type == HardNegative.FLASH_SALE:
        flash_mccs = ["5045", "5311", "5942"]
        mcc = str(rng.choice(flash_mccs))
        amount = round(amount * float(rng.uniform(2.0, 5.0)), 2)
        channel = Channel.ECOMMERCE

    elif hard_neg_type == HardNegative.SHARED_FAMILY_DEVICE:
        device_id = f"dev_shared_{int(rng.integers(0, 5)):03d}"

    # Handle Base Fraud
    attack_family = None
    if is_fraud:
        channel = Channel.ECOMMERCE
        amount = round(float(np.exp(customer.mean_log_amount + 2.0 * customer.std_log_amount)), 2)
        mcc = str(rng.choice(["5944", "5045", "5732", "5311"]))
        ip_prefix = f"198.51.{int(rng.integers(1, 255))}"
        device_id = f"dev_fraud_{int(rng.integers(100, 999))}"
        is_new_device = True
        auth_failed_count = int(rng.choice([1, 2, 3]))
        attack_family = AttackFamily.R1_ATO

    # If channel is AGENT (and not overridden by fraud/hard-negatives)
    if channel == Channel.AGENT and customer.has_agent and not is_fraud and hard_neg_type == HardNegative.NONE:
        agent_id = f"agent_{customer.customer_id}"
        mandate_id = f"mnd_{customer.customer_id}"
        if mandates and mandate_id in mandates:
            mandate = mandates[mandate_id]
            amount = min(amount, round(mandate.max_amount * 0.9, 2))
        else:
            max_agent_limit = float(min(customer.credit_limit * 0.4, np.exp(customer.mean_log_amount + 1.0 * customer.std_log_amount)))
            amount = min(amount, round(max_agent_limit, 2))

    return {
        "amount": amount,
        "mcc": mcc,
        "channel": channel,
        "lat": lat,
        "lon": lon,
        "merchant_id": merchant_id,
        "device_id": device_id,
        "ip_prefix": ip_prefix,
        "is_new_device": is_new_device,
        "auth_failed_count": auth_failed_count,
        "agent_id": agent_id,
        "mandate_id": mandate_id,
        "is_fraud": is_fraud,
        "attack_family": attack_family,
        "hard_negative": hard_neg_type,
    }
