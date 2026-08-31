"""Unit tests for Adaptive Red Team Search Engine."""

from __future__ import annotations

from datetime import datetime
import numpy as np
import pytest

from mcdl.blue.model import BlueDetector
from mcdl.red.adaptive import AdaptiveRedEngine
from mcdl.schemas import (
    Archetype,
    AttackFamily,
    Channel,
    Customer,
    Decision,
    FailureCategory,
    Merchant,
    Transaction,
    WeaknessProfile,
)


@pytest.fixture
def mock_entities():
    customer = Customer(
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
    merchant = Merchant(
        merchant_id="merch_001",
        mcc="5411",
        category="grocery",
        lat=40.7130,
        lon=-74.0055,
        risk_tier="low",
    )
    txn = Transaction(
        txn_id="txn_001",
        customer_id="cust_001",
        merchant_id="merch_001",
        device_id="dev_001",
        timestamp=datetime(2026, 8, 1, 12, 0, 0),
        amount=500.0,
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
    return {"customer": customer, "merchant": merchant, "txn": txn}


def test_adaptive_red_mutation_bias(mock_entities):
    cust = mock_entities["customer"]
    merch = mock_entities["merchant"]
    txn = mock_entities["txn"]

    # Mock detector
    detector = BlueDetector(n_estimators=10, max_depth=2, random_state=42)

    profile = WeaknessProfile(
        round_index=0,
        total_failures=5,
        dominant_categories=[(FailureCategory.W5_LOW_AND_SLOW.value, 0.60)],
        category_distribution={FailureCategory.W5_LOW_AND_SLOW.value: 0.60},
        frequent_mutations={"median_amount": 14.99, "top_channels": ["recurring"]},
        near_boundary_count=3,
        high_value_attack_surfaces=[AttackFamily.SLOW_SIPHON.value],
        rare_successful_patterns=[],
        reseeding_weights={AttackFamily.SLOW_SIPHON.value: 0.50},
    )

    engine = AdaptiveRedEngine(
        detector=detector,
        customers={cust.customer_id: cust},
        merchants={merch.merchant_id: merch},
        mandates={},
        weakness_profile=profile,
    )

    rng = np.random.default_rng(2026)
    cand = engine.generate_candidate(AttackFamily.SLOW_SIPHON, txn, cust, rng, query_idx=0)

    # Mutation should reflect low and slow biased amount (~14.99)
    assert cand.amount < 50.0
    assert cand.channel in (Channel.RECURRING, Channel.MOBILE_WALLET, Channel.ECOMMERCE)


def test_adaptive_red_query_budget_enforcement(mock_entities):
    from mcdl.features.batch import compute_batch_features
    from mcdl.blue.split import temporal_split

    cust = mock_entities["customer"]
    merch = mock_entities["merchant"]
    txn = mock_entities["txn"]

    # Fit detector with feature DataFrame
    feat_df = compute_batch_features([txn, txn.model_copy(update={"txn_id": "txn_002", "is_fraud": False})], customers={cust.customer_id: cust})
    detector = BlueDetector(n_estimators=10, max_depth=2, random_state=42)
    detector.fit(feat_df, feat_df)

    engine = AdaptiveRedEngine(
        detector=detector,
        customers={cust.customer_id: cust},
        merchants={merch.merchant_id: merch},
        mandates={},
    )

    # Test budget = 5
    prov = engine.attack(source_txn=txn, family=AttackFamily.BURST_DRAIN, budget=5, seed=2026)
    assert prov.queries_used <= 5
    assert prov.query_budget == 5

    # Test budget = 1
    prov1 = engine.attack(source_txn=txn, family=AttackFamily.BURST_DRAIN, budget=1, seed=2026)
    assert prov1.queries_used <= 1
    assert prov1.query_budget == 1
