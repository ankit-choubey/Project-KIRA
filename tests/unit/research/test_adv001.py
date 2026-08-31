"""Unit Test Suite for ADV-001 Large-Scale Adversarial Population."""

import json
from pathlib import Path
import numpy as np
import pytest

from mcdl.config import REPO_ROOT
from mcdl.red.evaluator import CANONICAL_FAMILIES
from mcdl.red.mask import check_mask_violations
from mcdl.research.advanced.adv001.evaluator import (
    AttackAttemptResult,
    compute_bootstrap_ci,
    compute_population_statistics,
)
from mcdl.research.advanced.adv001.population import generate_population_plans
from mcdl.research.advanced.adv001.storage import CheckpointManagerADV001
from mcdl.schemas import AttackFamily, Channel, Customer, Decision, Transaction

BASELINE_DIR = REPO_ROOT / "artifacts" / "run_tiny_s20260827_193f7897_40997ab"


@pytest.fixture
def sample_candidates():
    cust = Customer(
        customer_id="c_test_01",
        archetype="salaried_urban",
        home_lat=40.7128,
        home_lon=-74.0060,
        account_opened="2025-01-01T00:00:00",
        credit_limit=5000.0,
        mean_log_amount=4.0,
        std_log_amount=0.5,
        daily_txn_rate=1.5,
    )
    txns = [
        Transaction(
            txn_id=f"tx_test_{i:03d}",
            customer_id="c_test_01",
            merchant_id="m_test_01",
            device_id="dev_test_01",
            timestamp="2026-08-27T12:00:00",
            amount=150.0 + i * 10.0,
            mcc="5411",
            channel=Channel.ECOMMERCE,
            lat=40.7128,
            lon=-74.0060,
            ip_prefix="192.168",
            is_new_device=False,
            auth_failed_count=0,
            balance_before=500.0,
            available_credit=4500.0,
            is_fraud=False,
        )
        for i in range(5)
    ]
    return txns, {"c_test_01": cust}


def test_adv001_deterministic_seeding(sample_candidates):
    txns, customers = sample_candidates
    plans1 = generate_population_plans(txns, customers, target_count=50, base_seed=20260831)
    plans2 = generate_population_plans(txns, customers, target_count=50, base_seed=20260831)

    assert len(plans1) == 50
    assert len(plans2) == 50
    for p1, p2 in zip(plans1, plans2):
        assert p1.attack_id == p2.attack_id
        assert p1.seed == p2.seed
        assert p1.family == p2.family
        assert p1.query_budget == p2.query_budget


def test_adv001_exact_population_and_unique_ids(sample_candidates):
    txns, customers = sample_candidates
    plans = generate_population_plans(txns, customers, target_count=200, base_seed=20260831)
    assert len(plans) == 200

    attack_ids = [p.attack_id for p in plans]
    assert len(set(attack_ids)) == 200
    assert attack_ids[0] == "atk_adv001_000001"
    assert attack_ids[-1] == "atk_adv001_000200"


def test_adv001_family_coverage_and_budgets(sample_candidates):
    txns, customers = sample_candidates
    plans = generate_population_plans(txns, customers, target_count=100, base_seed=20260831)

    families_present = {p.family for p in plans}
    assert families_present == set(CANONICAL_FAMILIES)

    budgets_present = {p.query_budget for p in plans}
    assert budgets_present == {1, 5, 20, 100}


def test_adv001_failed_generation_not_counted_as_evasion():
    # Construct mock failed / invalid attempt results
    results = [
        AttackAttemptResult(
            attack_id="atk_1",
            family="burst_drain",
            strategy="mutate_burst_drain",
            seed=1,
            parent_attack_id=None,
            query_budget=20,
            queries_used=0,
            mutation_count=1,
            perturbation_distance=None,
            target_transaction_id="tx_1",
            blue_model_version="test_v1",
            blue_score=1.0,
            blue_decision="BLOCK",
            evasion=False,
            outcome="FAILED_MUTATION",
            timestamp="2026-08-31T10:00:00Z",
            provenance={"rejection_reasons": ["NON_POSITIVE_AMOUNT"]},
        ),
        AttackAttemptResult(
            attack_id="atk_2",
            family="burst_drain",
            strategy="mutate_burst_drain",
            seed=2,
            parent_attack_id=None,
            query_budget=20,
            queries_used=5,
            mutation_count=5,
            perturbation_distance=1.25,
            target_transaction_id="tx_2",
            blue_model_version="test_v1",
            blue_score=0.1,
            blue_decision="ALLOW",
            evasion=True,
            outcome="ALLOWED_EVASION",
            timestamp="2026-08-31T10:00:01Z",
            provenance={},
        ),
    ]

    stats = compute_population_statistics(results)
    assert stats["total_attempts"] == 2
    assert stats["allowed_evasion_count"] == 1
    assert stats["generation_failures"] == 1
    assert stats["aggregate_asr"] == 0.5


def test_adv001_bootstrap_ci_bounds():
    values = [1.0] * 50 + [0.0] * 50
    ci = compute_bootstrap_ci(values, n_bootstraps=500, seed=20260831)
    assert ci is not None
    lower, upper = ci
    assert 0.35 <= lower <= 0.50
    assert 0.50 <= upper <= 0.65


def test_adv001_checkpoint_and_resume(tmp_path):
    mgr = CheckpointManagerADV001(tmp_path / "adv001_test")

    # Write batch 1
    res_b1 = [
        AttackAttemptResult(
            attack_id=f"atk_{i}",
            family="burst_drain",
            strategy="mutate_burst_drain",
            seed=i,
            parent_attack_id=None,
            query_budget=20,
            queries_used=1,
            mutation_count=1,
            perturbation_distance=2.5,
            target_transaction_id=f"tx_{i}",
            blue_model_version="test_v1",
            blue_score=0.0,
            blue_decision="ALLOW",
            evasion=True,
            outcome="ALLOWED_EVASION",
            timestamp="2026-08-31T10:00:00Z",
            provenance={},
        )
        for i in range(10)
    ]
    mgr.write_batch(1, res_b1)

    completed = mgr.get_completed_batch_indices()
    assert 1 in completed
    assert 2 not in completed

    # Read all results
    all_res = mgr.read_all_results()
    assert len(all_res) == 10
    assert all_res[0].attack_id == "atk_0"


def test_adv001_valid_mutation_constraints(sample_candidates):
    txns, customers = sample_candidates
    base_txn = txns[0]
    cust = customers["c_test_01"]

    # Mutate burst drain
    rng = np.random.default_rng(20260831)
    from mcdl.red.strategies import mutate_burst_drain
    cand = mutate_burst_drain(base_txn, cust, rng, query_idx=0)
    violations = check_mask_violations(base_txn, cand, allowed_mutable=["amount", "channel"])
    assert len(violations) == 0
    assert cand.customer_id == base_txn.customer_id
    assert cand.timestamp == base_txn.timestamp


def test_adv001_invalid_mutation_rejection(sample_candidates):
    txns, _ = sample_candidates
    base_txn = txns[0]

    # Illegal mutation: modify customer_id
    illegal_cand = base_txn.model_copy(update={"customer_id": "c_hacked"})
    violations = check_mask_violations(base_txn, illegal_cand, allowed_mutable=["amount", "channel"])
    assert len(violations) > 0
    assert any("customer_id" in v for v in violations)


def test_adv001_outcome_taxonomy():
    results = [
        AttackAttemptResult(
            attack_id="atk_1",
            family="burst_drain",
            strategy="mutate_burst_drain",
            seed=1,
            parent_attack_id=None,
            query_budget=20,
            queries_used=20,
            mutation_count=20,
            perturbation_distance=None,
            target_transaction_id="tx_1",
            blue_model_version="test_v1",
            blue_score=0.9,
            blue_decision="BLOCK",
            evasion=False,
            outcome="BLOCKED",
            timestamp="2026-08-31T10:00:00Z",
            provenance={},
        ),
        AttackAttemptResult(
            attack_id="atk_2",
            family="burst_drain",
            strategy="mutate_burst_drain",
            seed=2,
            parent_attack_id=None,
            query_budget=20,
            queries_used=20,
            mutation_count=20,
            perturbation_distance=None,
            target_transaction_id="tx_2",
            blue_model_version="test_v1",
            blue_score=0.6,
            blue_decision="STEP_UP",
            evasion=False,
            outcome="STEP_UP",
            timestamp="2026-08-31T10:00:01Z",
            provenance={},
        ),
        AttackAttemptResult(
            attack_id="atk_3",
            family="burst_drain",
            strategy="mutate_burst_drain",
            seed=3,
            parent_attack_id=None,
            query_budget=20,
            queries_used=3,
            mutation_count=3,
            perturbation_distance=1.45,
            target_transaction_id="tx_3",
            blue_model_version="test_v1",
            blue_score=0.1,
            blue_decision="ALLOW",
            evasion=True,
            outcome="ALLOWED_EVASION",
            timestamp="2026-08-31T10:00:02Z",
            provenance={},
        ),
    ]

    stats = compute_population_statistics(results)
    assert stats["total_attempts"] == 3
    assert stats["allowed_evasion_count"] == 1
    assert stats["blocked_count"] == 1
    assert stats["step_up_count"] == 1
    assert stats["outcome_distribution"]["ALLOWED_EVASION"] == 1
    assert stats["outcome_distribution"]["BLOCKED"] == 1
    assert stats["outcome_distribution"]["STEP_UP"] == 1


def test_adv001_provenance_metadata():
    res = AttackAttemptResult(
        attack_id="atk_prov_test",
        family="geo_hop",
        strategy="mutate_geo_hop",
        seed=20260831,
        parent_attack_id=None,
        query_budget=100,
        queries_used=12,
        mutation_count=12,
        perturbation_distance=2.12,
        target_transaction_id="tx_test_99",
        blue_model_version="run_tiny_s20260827_193f7897_40997ab",
        blue_score=0.05,
        blue_decision="ALLOW",
        evasion=True,
        outcome="ALLOWED_EVASION",
        timestamp="2026-08-31T10:00:00Z",
        provenance={"rejection_reasons": []},
    )
    d = res.to_dict()
    assert d["attack_id"] == "atk_prov_test"
    assert d["family"] == "geo_hop"
    assert d["blue_model_version"] == "run_tiny_s20260827_193f7897_40997ab"
    assert d["perturbation_distance"] == 2.12


def test_adv001_protected_baseline_integrity():
    # Baseline directory must contain exact 22/22 original artifacts untouched
    if BASELINE_DIR.exists():
        prov_path = BASELINE_DIR / "provenance.json"
        assert prov_path.exists()
        prov = json.loads(prov_path.read_text(encoding="utf-8"))
        artifacts = prov.get("artifacts", {})
        assert len(artifacts) == 22
        assert prov.get("artifact_count") == 22
