"""Unit tests for Failure Analysis, Taxonomy, and Weakness Profiling."""

from __future__ import annotations

from datetime import datetime
import pytest

from mcdl.loop.failure import FailureAnalyzer
from mcdl.red.search import AttackProvenance
from mcdl.schemas import (
    Archetype,
    AttackFamily,
    Channel,
    Customer,
    Decision,
    FailureCategory,
    Transaction,
)


@pytest.fixture
def mock_customer() -> Customer:
    return Customer(
        customer_id="cust_001",
        archetype=Archetype.SALARIED_URBAN,
        home_lat=40.7128,
        home_lon=-74.0060,
        account_opened=datetime(2023, 1, 1),
        credit_limit=5000.0,
        mean_log_amount=4.0,
        std_log_amount=0.5,
        daily_txn_rate=2.0,
    )


@pytest.fixture
def mock_transaction() -> Transaction:
    return Transaction(
        txn_id="txn_001",
        customer_id="cust_001",
        merchant_id="merch_001",
        device_id="dev_001",
        timestamp=datetime(2026, 8, 1, 12, 0, 0),
        amount=100.0,
        mcc="5411",
        channel=Channel.ECOMMERCE,
        lat=40.7128,
        lon=-74.0060,
        ip_prefix="192.168.1",
        is_new_device=False,
        auth_failed_count=0,
        balance_before=1000.0,
        available_credit=4000.0,
        is_fraud=True,
    )


def test_classify_categories_mapping(mock_transaction):
    analyzer = FailureAnalyzer()

    # W1 Velocity Blindness
    cat1, sec1 = analyzer.classify_categories(AttackFamily.BURST_DRAIN, mock_transaction, mock_transaction)
    assert cat1 == FailureCategory.W1_VELOCITY_BLINDNESS

    # W5 Low and Slow
    cat5, sec5 = analyzer.classify_categories(AttackFamily.SLOW_SIPHON, mock_transaction, mock_transaction)
    assert cat5 == FailureCategory.W5_LOW_AND_SLOW
    assert FailureCategory.W11_TEMPORAL_CAMOUFLAGE in sec5

    # W3 Geo Camouflage
    cat3, _ = analyzer.classify_categories(AttackFamily.GEO_HOP, mock_transaction, mock_transaction)
    assert cat3 == FailureCategory.W3_GEOGRAPHIC_CAMOUFLAGE

    # W7 Intent Drift
    cat7, _ = analyzer.classify_categories(AttackFamily.AGENT_SUBVERSION, mock_transaction, mock_transaction)
    assert cat7 == FailureCategory.W7_INTENT_DRIFT

    # W8 Multi Account
    cat8, _ = analyzer.classify_categories(AttackFamily.CROSS_MERCHANT_FANOUT, mock_transaction, mock_transaction)
    assert cat8 == FailureCategory.W8_COORDINATED_MULTI_ACCOUNT


def test_diagnose_failure_scoring(mock_customer, mock_transaction):
    analyzer = FailureAnalyzer(w_hardness=0.35, w_novelty=0.25, w_boundary=0.25, w_rarity=0.15)

    prov = AttackProvenance(
        attack_instance_id="atk_test_001",
        attack_family=AttackFamily.SLOW_SIPHON,
        source_txn_id=mock_transaction.txn_id,
        seed=2026,
        query_budget=20,
        queries_used=2,  # Hard evasion (used only 2 probes)
        mutations_attempted=2,
        valid_mutations=2,
        invalid_mutations=0,
        original_decision=Decision.BLOCK,
        final_decision=Decision.ALLOW,
        original_risk=0.85,
        final_risk=0.48,  # Near boundary (boundary proximity ~ 0.96)
        med=1.25,
        success=True,
        best_candidate=mock_transaction,
    )

    rec = analyzer.diagnose_failure(
        prov=prov,
        customer=mock_customer,
        features={"intent_drift_score": 0.0},
        round_idx=1,
    )

    assert rec.primary_failure_category == FailureCategory.W5_LOW_AND_SLOW
    assert rec.hardness_score > 0.90  # queries_used = 2 out of 20
    assert rec.boundary_proximity > 0.90  # risk = 0.48
    assert rec.priority_score > 0.50
    assert rec.mutation_distance == 1.25


def test_synthesize_weakness_profile(mock_customer, mock_transaction):
    analyzer = FailureAnalyzer()

    prov = AttackProvenance(
        attack_instance_id="atk_test_001",
        attack_family=AttackFamily.SLOW_SIPHON,
        source_txn_id=mock_transaction.txn_id,
        seed=2026,
        query_budget=20,
        queries_used=3,
        mutations_attempted=3,
        valid_mutations=3,
        invalid_mutations=0,
        original_decision=Decision.BLOCK,
        final_decision=Decision.ALLOW,
        original_risk=0.80,
        final_risk=0.45,
        med=0.85,
        success=True,
        best_candidate=mock_transaction,
    )

    rec = analyzer.diagnose_failure(prov, mock_customer, {}, round_idx=0)
    profile = analyzer.synthesize_weakness_profile([rec], round_idx=0)

    assert profile.total_failures == 1
    assert profile.dominant_categories[0][0] == FailureCategory.W5_LOW_AND_SLOW.value
    assert profile.reseeding_weights[AttackFamily.SLOW_SIPHON.value] > profile.reseeding_weights[AttackFamily.GEO_HOP.value]
