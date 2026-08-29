"""Unit tests for synthetic world generation and Layer 1 physical validity."""

from datetime import datetime
import pytest

from mcdl.config import load_config
from mcdl.evaluation.validity import check_transactions, check_world
from mcdl.schemas import Archetype, HardNegative, Transaction
from mcdl.world.entities import generate_entities
from mcdl.world.generator import generate_world
from mcdl.world.ledger import WorldLedger


def test_entities_generation():
    cfg = load_config(scale="tiny")
    customers, merchants, devices, mandates = generate_entities(
        n_customers=50,
        n_merchants=20,
        start_date=datetime(2026, 1, 1),
        archetype_shares=cfg["world"]["archetypes"],
        agent_share=0.10,
    )
    assert len(customers) == 50
    assert len(merchants) == 20
    assert len(devices) >= 30
    assert len(mandates) >= 0

    # Ensure all customer fields are populated
    for cust in customers.values():
        assert cust.credit_limit > 0
        assert cust.daily_txn_rate > 0
        assert isinstance(cust.archetype, Archetype)


def test_ledger_invariants():
    cfg = load_config(scale="tiny")
    customers, merchants, devices, mandates = generate_entities(
        n_customers=5,
        n_merchants=5,
        start_date=datetime(2026, 1, 1),
        archetype_shares=cfg["world"]["archetypes"],
    )
    ledger = WorldLedger(customers=customers, devices=devices, mandates=mandates)

    c_id = list(customers.keys())[0]
    dev_id = list(devices.keys())[0]

    # Test excessive amount rejection
    bad_txn = {
        "txn_id": "tx_bad_01",
        "customer_id": c_id,
        "amount": 99999999.0,
        "timestamp": datetime(2026, 1, 2),
        "device_id": dev_id,
        "lat": 40.0,
        "lon": -74.0,
    }
    is_valid, reason, _, _ = ledger.validate_and_apply(bad_txn)
    assert not is_valid
    assert "EXCEEDS_CREDIT_LIMIT" in reason


def test_world_generation_and_validity():
    cfg = load_config(scale="tiny")
    world = generate_world(cfg)

    assert len(world.transactions) > 0
    assert len(world.customers) > 0
    assert len(world.merchants) > 0

    # Evaluate physical validity
    report = check_world(world)
    assert report.passed, f"Violations found: {report.violation_samples}"
    assert report.total_violations == 0
    assert report.negative_balance_violations == 0
    assert report.timestamp_order_violations == 0
    assert report.foreign_key_violations == 0


def test_hard_negatives_and_fraud_present():
    cfg = load_config(scale="tiny")
    world = generate_world(cfg)

    hard_negs = set(t.hard_negative for t in world.transactions if t.hard_negative != HardNegative.NONE)
    assert len(hard_negs) >= 2, f"Expected multiple hard negative types, got {hard_negs}"

    fraud_txns = [t for t in world.transactions if t.is_fraud]
    assert len(fraud_txns) > 0, "Expected baseline fraud transactions in generated world"
