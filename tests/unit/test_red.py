"""Comprehensive Unit Tests for Red Team Adversarial Search Engine."""

from datetime import datetime, timedelta
import numpy as np
import pytest

from mcdl.blue.model import BlueDetector
from mcdl.config import load_config
from mcdl.features.batch import compute_batch_features
from mcdl.red.distance import compute_evasion_distance
from mcdl.red.evaluator import CANONICAL_FAMILIES, evaluate_red_attacks
from mcdl.red.mask import (
    FAMILY_MUTABLE_FIELDS,
    IMMUTABLE_FIELDS,
    check_mask_violations,
    get_mutability_mask,
)
from mcdl.red.search import AttackProvenance, RedSearchEngine, validate_physical_candidate
from mcdl.schemas import AttackFamily, Channel, Customer, Decision, Mandate, Merchant, Transaction
from mcdl.world.generator import generate_world


@pytest.fixture
def sample_world_data():
    """Generates a small baseline world with trained BlueDetector for testing."""
    cfg = load_config(scale="tiny")
    world = generate_world(cfg)
    feature_df = compute_batch_features(world.transactions, customers=world.customers)
    train_df = feature_df[:5000]
    valid_df = feature_df[5000:6500]

    detector = BlueDetector(n_estimators=30, max_depth=3, learning_rate=0.05)
    detector.fit(train_df, valid_df)

    return world, detector


def test_immutable_field_policy_enforcement():
    """Verifies that attempting to alter immutable fields is strictly caught and rejected."""
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    base_txn = Transaction(
        txn_id="tx_orig",
        customer_id="c_orig",
        merchant_id="m_orig",
        device_id="dev_orig",
        timestamp=t0,
        amount=100.0,
        mcc="5411",
        channel=Channel.CARD_PRESENT,
        lat=40.0,
        lon=-74.0,
        ip_prefix="10.0",
        is_new_device=False,
        auth_failed_count=0,
        balance_before=1000.0,
        available_credit=4000.0,
        is_fraud=False,
    )

    # 1. Legal mutation on amount (allowed in burst_drain)
    legal_mutated = base_txn.model_copy(update={"amount": 50.0})
    violations = check_mask_violations(base_txn, legal_mutated, allowed_mutable=["amount", "channel"])
    assert len(violations) == 0

    # 2. Illegal mutation on customer_id
    illegal_cust = base_txn.model_copy(update={"customer_id": "c_hacked"})
    v_cust = check_mask_violations(base_txn, illegal_cust, allowed_mutable=["amount", "channel"])
    assert any("customer_id" in v for v in v_cust)

    # 3. Illegal mutation on timestamp
    illegal_ts = base_txn.model_copy(update={"timestamp": t0 + timedelta(days=1)})
    v_ts = check_mask_violations(base_txn, illegal_ts, allowed_mutable=["amount", "channel"])
    assert any("timestamp" in v for v in v_ts)

    # 4. Illegal mutation on balance_before
    illegal_bal = base_txn.model_copy(update={"balance_before": 0.0})
    v_bal = check_mask_violations(base_txn, illegal_bal, allowed_mutable=["amount", "channel"])
    assert any("balance_before" in v for v in v_bal)


def test_physical_validity_candidate_validator():
    """Verifies that invalid physics (exceeding credit limit, invalid balance equation) is caught."""
    cust = Customer(
        customer_id="c1",
        archetype="salaried_urban",
        home_lat=40.0,
        home_lon=-74.0,
        account_opened=datetime(2025, 1, 1),
        credit_limit=5000.0,
        mean_log_amount=3.5,
        std_log_amount=0.8,
        daily_txn_rate=2.0,
    )
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    valid_txn = Transaction(
        txn_id="tx_1",
        customer_id="c1",
        merchant_id="m1",
        device_id="dev1",
        timestamp=t0,
        amount=100.0,
        mcc="5411",
        channel=Channel.CARD_PRESENT,
        lat=40.0,
        lon=-74.0,
        ip_prefix="10.0",
        is_new_device=False,
        auth_failed_count=0,
        balance_before=1000.0,
        available_credit=4000.0,
        is_fraud=False,
    )

    merchants = {}
    mandates = {}

    # Valid txn passes
    assert len(validate_physical_candidate(valid_txn, cust, merchants, mandates)) == 0

    # Exceeding credit limit
    over_limit_txn = valid_txn.model_copy(update={"amount": 6000.0})
    v_over = validate_physical_candidate(over_limit_txn, cust, merchants, mandates)
    assert "EXCEEDS_CREDIT_LIMIT" in v_over

    # Negative amount
    neg_txn = valid_txn.model_copy(update={"amount": -50.0})
    v_neg = validate_physical_candidate(neg_txn, cust, merchants, mandates)
    assert "NON_POSITIVE_AMOUNT" in v_neg

    # Invalid coordinates
    bad_geo = valid_txn.model_copy(update={"lat": 120.0})
    v_geo = validate_physical_candidate(bad_geo, cust, merchants, mandates)
    assert "INVALID_COORDINATES" in v_geo


def test_evasion_distance_metric():
    """Asserts that Minimum Evasion Distance (MED) is non-negative and properly normalized."""
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    t1 = Transaction(
        txn_id="tx_1",
        customer_id="c1",
        merchant_id="m1",
        device_id="dev1",
        timestamp=t0,
        amount=100.0,
        mcc="5411",
        channel=Channel.CARD_PRESENT,
        lat=40.0,
        lon=-74.0,
        ip_prefix="10.0",
        is_new_device=False,
        auth_failed_count=0,
        balance_before=1000.0,
        available_credit=4000.0,
        is_fraud=False,
    )

    # Identical transaction -> distance = 0.0
    assert compute_evasion_distance(t1, t1) == 0.0

    # Perturbed amount ($100 -> $50)
    t_amt = t1.model_copy(update={"amount": 50.0})
    d_amt = compute_evasion_distance(t1, t_amt)
    assert d_amt > 0.0
    assert abs(d_amt - abs(np.log(51.0) - np.log(101.0))) <= 1e-5

    # Perturbed coordinates (~111 km north)
    t_geo = t1.model_copy(update={"lat": 41.0})
    d_geo = compute_evasion_distance(t1, t_geo)
    assert d_geo > 0.0
    assert 1.0 <= d_geo <= 1.3  # approx 111 km / 100 km ~ 1.11


def test_all_five_attack_families_execute(sample_world_data):
    """Executes all 5 canonical attack families against Blue detector and verifies provenance."""
    world, detector = sample_world_data

    # Select a transaction flagged as risky
    risky_txns = [t for t in world.transactions if t.is_fraud or t.amount > 300.0]
    sample_txn = risky_txns[0] if risky_txns else world.transactions[0]

    engine = RedSearchEngine(
        detector=detector,
        customers=world.customers,
        merchants=world.merchants,
        mandates=world.mandates,
    )

    for family in CANONICAL_FAMILIES:
        prov = engine.attack(source_txn=sample_txn, family=family, budget=5, seed=42)

        assert isinstance(prov, AttackProvenance)
        assert prov.attack_family == family
        assert prov.source_txn_id == sample_txn.txn_id
        assert 1 <= prov.queries_used <= 5
        assert prov.med >= 0.0
        assert prov.final_decision in {Decision.ALLOW, Decision.STEP_UP, Decision.BLOCK}


def test_deterministic_attack_replay(sample_world_data):
    """Asserts that running Red attack with the exact same seed produces bit-for-bit identical results."""
    world, detector = sample_world_data
    sample_txn = world.transactions[10]

    engine = RedSearchEngine(
        detector=detector,
        customers=world.customers,
        merchants=world.merchants,
        mandates=world.mandates,
    )

    run1 = engine.attack(source_txn=sample_txn, family=AttackFamily.BURST_DRAIN, budget=20, seed=12345)
    run2 = engine.attack(source_txn=sample_txn, family=AttackFamily.BURST_DRAIN, budget=20, seed=12345)

    assert run1.queries_used == run2.queries_used
    assert run1.final_decision == run2.final_decision
    assert run1.final_risk == run2.final_risk
    assert run1.med == run2.med
    assert run1.success == run2.success


def test_red_evaluator_asr_at_budget(sample_world_data):
    """Verifies ASR@budget computation across budgets [1, 5, 20, 100]."""
    world, detector = sample_world_data
    sample_txns = world.transactions[:10]

    red_metrics, prov_log = evaluate_red_attacks(
        transactions=sample_txns,
        detector=detector,
        customers=world.customers,
        merchants=world.merchants,
        mandates=world.mandates,
        budgets=[1, 5, 20, 100],
        families=[AttackFamily.BURST_DRAIN, AttackFamily.SLOW_SIPHON],
    )

    assert "1" in red_metrics.asr_by_budget
    assert "5" in red_metrics.asr_by_budget
    assert "20" in red_metrics.asr_by_budget
    assert "100" in red_metrics.asr_by_budget

    # ASR at larger budgets must be >= ASR at budget 1
    assert red_metrics.asr_by_budget["100"] >= red_metrics.asr_by_budget["1"]
    assert red_metrics.mask_violations == 0
