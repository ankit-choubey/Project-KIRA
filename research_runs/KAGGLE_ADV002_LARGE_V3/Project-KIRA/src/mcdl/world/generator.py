"""Master synthetic payment world generator.

Simulates stateful customer behavior, entity interactions, hard negatives,
and valid physical ledger transitions across the configured timeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

from mcdl.config import Config
from mcdl.schemas import Customer, Device, HardNegative, Mandate, Merchant, Transaction
from mcdl.world.entities import generate_entities
from mcdl.world.hard_negatives import sample_transaction_attributes
from mcdl.world.ledger import WorldLedger


@dataclass
class WorldResult:
    customers: dict[str, Customer]
    merchants: dict[str, Merchant]
    devices: dict[str, Device]
    mandates: dict[str, Mandate]
    transactions: list[Transaction]
    rejection_count: int
    rejected_log: list[tuple[str, str]]


def generate_world(
    cfg: Config | dict,
    start_date: datetime | None = None,
    seed: int | None = None,
) -> WorldResult:
    """Generates a complete synthetic payment world matching configuration parameters."""
    if isinstance(cfg, dict):
        # Allow passing dict directly
        cfg_dict = cfg
    else:
        cfg_dict = cfg._raw if hasattr(cfg, "_raw") else dict(cfg)

    effective_seed = seed if seed is not None else cfg_dict.get("seed", 20260827)
    rng = np.random.default_rng(effective_seed)

    scale_name = cfg_dict.get("scale", "tiny")
    presets = cfg_dict.get("scale_presets", {})
    scale_cfg = presets.get(scale_name, {})

    n_customers = int(scale_cfg.get("n_customers", 200))
    n_merchants = int(scale_cfg.get("n_merchants", 80))
    n_days = int(scale_cfg.get("n_days", 30))
    target_events = int(scale_cfg.get("target_events", 10000))

    world_cfg = cfg_dict.get("world", {})
    archetype_shares = world_cfg.get("archetypes", {
        "salaried_urban": 0.45,
        "student": 0.25,
        "small_business": 0.20,
        "high_net_worth": 0.10,
    })
    base_fraud_rate = float(world_cfg.get("base_fraud_rate", 0.006))
    agent_share = float(world_cfg.get("agent_share", 0.08))
    hard_neg_cfg = world_cfg.get("hard_negatives", {
        "traveller": 0.03,
        "flash_sale": 0.04,
        "shared_family_device": 0.03,
    })

    if start_date is None:
        start_date = datetime(2026, 1, 1, 0, 0, 0)

    # 1. Initialize entities
    customers, merchants, devices, mandates = generate_entities(
        n_customers=n_customers,
        n_merchants=n_merchants,
        start_date=start_date,
        archetype_shares=archetype_shares,
        agent_share=agent_share,
        rng=rng,
    )

    # Ensure dynamic devices (travel/fraud) have a registered first_seen before use
    travel_dev_start = start_date - timedelta(days=50)
    for c_id in customers.keys():
        t_dev = f"dev_{c_id}_travel"
        devices[t_dev] = Device(device_id=t_dev, first_seen=travel_dev_start, shared=False)

    for f_idx in range(100, 1000):
        f_dev = f"dev_fraud_{f_idx}"
        devices[f_dev] = Device(device_id=f_dev, first_seen=travel_dev_start, shared=False)

    # 2. Initialize ledger
    ledger = WorldLedger(
        customers=customers,
        devices=devices,
        mandates=mandates,
        allow_overdraft=False,
    )

    # 3. Schedule customer events across simulation timeline
    # Generate event times per customer using Poisson inter-arrival intervals
    all_raw_events: list[tuple[datetime, str]] = []  # (ts, customer_id)
    total_seconds = n_days * 86400

    for c_id, cust in customers.items():
        # Lambda in events per second
        rate_per_sec = cust.daily_txn_rate / 86400.0
        curr_t = float(rng.uniform(0, 3600))  # initial offset
        while curr_t < total_seconds:
            dt = float(rng.exponential(1.0 / rate_per_sec))
            curr_t += max(60.0, dt)  # at least 1 minute apart
            if curr_t < total_seconds:
                event_ts = start_date + timedelta(seconds=curr_t)
                all_raw_events.append((event_ts, c_id))

    # Sort strictly chronologically
    all_raw_events.sort(key=lambda x: x[0])

    # Cap to target_events if specified and exceeded
    if len(all_raw_events) > target_events * 1.2:
        step = len(all_raw_events) / target_events
        indices = [int(i * step) for i in range(target_events)]
        all_raw_events = [all_raw_events[i] for i in indices]

    # 4. Generate transaction attributes and validate against ledger
    transactions: list[Transaction] = []
    txn_counter = 0

    traveller_prob = float(hard_neg_cfg.get("traveller", 0.03))
    flash_prob = float(hard_neg_cfg.get("flash_sale", 0.04))
    shared_prob = float(hard_neg_cfg.get("shared_family_device", 0.03))

    for event_ts, c_id in all_raw_events:
        cust = customers[c_id]
        txn_id = f"tx_{txn_counter:08d}"

        # Determine if hard negative or fraud
        p_type = rng.random()
        hard_neg = HardNegative.NONE
        is_fraud = False

        if p_type < base_fraud_rate:
            is_fraud = True
        elif p_type < base_fraud_rate + traveller_prob:
            hard_neg = HardNegative.TRAVELLER
        elif p_type < base_fraud_rate + traveller_prob + flash_prob:
            hard_neg = HardNegative.FLASH_SALE
        elif p_type < base_fraud_rate + traveller_prob + flash_prob + shared_prob:
            hard_neg = HardNegative.SHARED_FAMILY_DEVICE

        candidate_attrs = sample_transaction_attributes(
            customer=cust,
            merchants=merchants,
            ts=event_ts,
            hard_neg_type=hard_neg,
            is_fraud=is_fraud,
            mandates=mandates,
            rng=rng,
        )

        candidate_payload = {
            "txn_id": txn_id,
            "customer_id": c_id,
            "timestamp": event_ts,
            **candidate_attrs,
        }

        # Apply stateful validation in ledger
        is_valid, reason, bal_before, avail_before = ledger.validate_and_apply(candidate_payload)
        if not is_valid:
            continue

        txn = Transaction(
            txn_id=txn_id,
            customer_id=c_id,
            merchant_id=candidate_attrs["merchant_id"],
            device_id=candidate_attrs["device_id"],
            timestamp=event_ts,
            amount=candidate_attrs["amount"],
            mcc=candidate_attrs["mcc"],
            channel=candidate_attrs["channel"],
            lat=candidate_attrs["lat"],
            lon=candidate_attrs["lon"],
            ip_prefix=candidate_attrs["ip_prefix"],
            is_new_device=candidate_attrs["is_new_device"],
            auth_failed_count=candidate_attrs["auth_failed_count"],
            agent_id=candidate_attrs["agent_id"],
            mandate_id=candidate_attrs["mandate_id"],
            balance_before=bal_before,
            available_credit=avail_before,
            is_fraud=candidate_attrs["is_fraud"],
            attack_family=candidate_attrs["attack_family"],
            attack_instance_id=f"inst_{txn_id}" if candidate_attrs["is_fraud"] else None,
            attack_variant=0 if candidate_attrs["is_fraud"] else None,
            hard_negative=candidate_attrs["hard_negative"],
        )
        transactions.append(txn)
        txn_counter += 1

    return WorldResult(
        customers=customers,
        merchants=merchants,
        devices=devices,
        mandates=mandates,
        transactions=transactions,
        rejection_count=len(ledger.rejected_txns),
        rejected_log=ledger.rejected_txns[:20],
    )
