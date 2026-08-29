"""Unit tests for synthetic world generation and Layer 1 physical validity."""

from datetime import datetime, timedelta
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


# --------------------------------------------------------------------------- #
# Targeted Layer-1 Validity Invariant Regression Tests
# --------------------------------------------------------------------------- #


@pytest.fixture
def base_world():
    cfg = load_config(scale="tiny")
    customers, merchants, devices, mandates = generate_entities(
        n_customers=5,
        n_merchants=5,
        start_date=datetime(2026, 1, 1),
        archetype_shares=cfg["world"]["archetypes"],
        agent_share=0.5,
    )
    return customers, merchants, devices, mandates


def _make_sample_txn(
    c_id: str,
    m_id: str,
    dev_id: str,
    ts: datetime,
    amount: float = 50.0,
    mcc: str = "5411",
    balance_before: float = 100.0,
    available_credit: float = 4900.0,
    lat: float = 40.0,
    lon: float = -74.0,
    mandate_id: str | None = None,
) -> Transaction:
    return Transaction(
        txn_id="tx_test_01",
        customer_id=c_id,
        merchant_id=m_id,
        device_id=dev_id,
        timestamp=ts,
        amount=amount,
        mcc=mcc,
        channel="card_present",
        lat=lat,
        lon=lon,
        ip_prefix="192.168",
        is_new_device=False,
        auth_failed_count=0,
        balance_before=balance_before,
        available_credit=available_credit,
        mandate_id=mandate_id,
    )


def test_regression_inconsistent_balance_transitions(base_world):
    customers, merchants, devices, mandates = base_world
    c_id = list(customers.keys())[0]
    cust = customers[c_id]
    m_id = list(merchants.keys())[0]
    dev_id = list(devices.keys())[0]

    # balance_before + available_credit does not match cust.credit_limit
    bad_txn = _make_sample_txn(
        c_id, m_id, dev_id, datetime(2026, 1, 2),
        balance_before=100.0, available_credit=cust.credit_limit,  # sum = limit + 100
    )
    report = check_transactions([bad_txn], customers, merchants, devices, mandates)
    assert report.negative_balance_violations > 0
    assert not report.passed


def test_regression_invalid_transaction_amount(base_world):
    customers, merchants, devices, mandates = base_world
    c_id = list(customers.keys())[0]
    m_id = list(merchants.keys())[0]
    dev_id = list(devices.keys())[0]

    with pytest.raises(ValueError):
        _make_sample_txn(c_id, m_id, dev_id, datetime(2026, 1, 2), amount=-10.0)


def test_regression_credit_limit_boundary(base_world):
    customers, merchants, devices, mandates = base_world
    c_id = list(customers.keys())[0]
    cust = customers[c_id]
    m_id = list(merchants.keys())[0]
    dev_id = list(devices.keys())[0]

    # balance_before strictly exceeds credit limit
    bad_txn = _make_sample_txn(
        c_id, m_id, dev_id, datetime(2026, 1, 2),
        balance_before=cust.credit_limit + 50.0,
        available_credit=0.0,
    )
    report = check_transactions([bad_txn], customers, merchants, devices, mandates)
    assert report.negative_balance_violations > 0
    assert not report.passed


def test_regression_timestamp_ordering(base_world):
    customers, merchants, devices, mandates = base_world
    c_id = list(customers.keys())[0]
    cust = customers[c_id]
    m_id = list(merchants.keys())[0]
    dev_id = list(devices.keys())[0]

    t1 = _make_sample_txn(c_id, m_id, dev_id, datetime(2026, 1, 2, 12, 0), balance_before=10.0, available_credit=cust.credit_limit - 10.0)
    t2 = _make_sample_txn(c_id, m_id, dev_id, datetime(2026, 1, 2, 11, 0), balance_before=20.0, available_credit=cust.credit_limit - 20.0)
    report = check_transactions([t1, t2], customers, merchants, devices, mandates)
    assert report.timestamp_order_violations > 0
    assert not report.passed


def test_regression_device_registration_ordering(base_world):
    customers, merchants, devices, mandates = base_world
    c_id = list(customers.keys())[0]
    cust = customers[c_id]
    m_id = list(merchants.keys())[0]
    dev_id = list(devices.keys())[0]
    dev = devices[dev_id]

    # Transaction timestamp earlier than device first_seen
    bad_txn = _make_sample_txn(
        c_id, m_id, dev_id,
        ts=dev.first_seen - timedelta(days=1),
        balance_before=10.0,
        available_credit=cust.credit_limit - 10.0,
    )
    report = check_transactions([bad_txn], customers, merchants, devices, mandates)
    assert report.device_registration_violations > 0
    assert not report.passed


def test_regression_invalid_mcc(base_world):
    customers, merchants, devices, mandates = base_world
    c_id = list(customers.keys())[0]
    m_id = list(merchants.keys())[0]
    dev_id = list(devices.keys())[0]

    with pytest.raises(ValueError):
        _make_sample_txn(c_id, m_id, dev_id, datetime(2026, 1, 2), mcc="INVALID_MCC")


def test_regression_impossible_travel(base_world):
    customers, merchants, devices, mandates = base_world
    c_id = list(customers.keys())[0]
    cust = customers[c_id]
    m_id = list(merchants.keys())[0]
    dev_id = list(devices.keys())[0]

    # NYC (40.71, -74.00) to London (51.50, -0.12) ~ 5500 km in 5 minutes
    t1 = _make_sample_txn(c_id, m_id, dev_id, datetime(2026, 1, 2, 10, 0), lat=40.71, lon=-74.00, balance_before=10.0, available_credit=cust.credit_limit - 10.0)
    t2 = _make_sample_txn(c_id, m_id, dev_id, datetime(2026, 1, 2, 10, 5), lat=51.50, lon=-0.12, balance_before=20.0, available_credit=cust.credit_limit - 20.0)
    report = check_transactions([t1, t2], customers, merchants, devices, mandates)
    assert report.geo_speed_violations > 0
    assert not report.passed


def test_regression_invalid_foreign_keys(base_world):
    customers, merchants, devices, mandates = base_world
    c_id = list(customers.keys())[0]
    m_id = list(merchants.keys())[0]
    dev_id = list(devices.keys())[0]

    bad_cust_txn = _make_sample_txn("unknown_cust_999", m_id, dev_id, datetime(2026, 1, 2))
    report1 = check_transactions([bad_cust_txn], customers, merchants, devices, mandates)
    assert report1.foreign_key_violations > 0

    bad_merch_txn = _make_sample_txn(c_id, "unknown_merch_999", dev_id, datetime(2026, 1, 2))
    report2 = check_transactions([bad_merch_txn], customers, merchants, devices, mandates)
    assert report2.foreign_key_violations > 0

    bad_dev_txn = _make_sample_txn(c_id, m_id, "unknown_dev_999", datetime(2026, 1, 2))
    report3 = check_transactions([bad_dev_txn], customers, merchants, devices, mandates)
    assert report3.foreign_key_violations > 0


def test_regression_invalid_mandate_amount(base_world):
    customers, merchants, devices, mandates = base_world
    if not mandates:
        # Create a mandate
        c_id = list(customers.keys())[0]
        mandates[f"mnd_{c_id}"] = Mandate(
            mandate_id=f"mnd_{c_id}",
            customer_id=c_id,
            agent_id=f"agent_{c_id}",
            max_amount=100.0,
            max_txn_count=10,
            allowed_mcc=["5411"],
            valid_from=datetime(2026, 1, 1),
            valid_until=datetime(2026, 12, 31),
        )

    mnd_id = list(mandates.keys())[0]
    mandate = mandates[mnd_id]
    c_id = mandate.customer_id
    cust = customers[c_id]
    m_id = list(merchants.keys())[0]
    dev_id = list(devices.keys())[0]

    # Exceeds max mandate amount of 100.0
    bad_txn = _make_sample_txn(
        c_id, m_id, dev_id, datetime(2026, 1, 2),
        amount=mandate.max_amount + 50.0,
        mandate_id=mnd_id,
        balance_before=10.0,
        available_credit=cust.credit_limit - 10.0,
    )
    report = check_transactions([bad_txn], customers, merchants, devices, mandates)
    assert report.mandate_violations > 0
    assert not report.passed

