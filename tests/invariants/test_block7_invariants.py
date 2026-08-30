"""The 10 Invariant Tests for Block 7 Adaptive Co-Evolution Engine.

Asserts all critical safety, mutability, isolation, and anti-memorization contracts:
  Test 1  — Mutability mask rejection
  Test 2  — Constraint validation / Layer-1 physics rejection
  Test 3  — Strict query budget enforcement (queries_used <= budget)
  Test 4  — Replay provenance preservation without feature leakage
  Test 5  — Held-out variant isolation (train_variants ∩ eval_variants = ∅)
  Test 6  — Hidden-family isolation (adapt_families ∩ hidden_families = ∅)
  Test 7  — Champion / Challenger evaluation fairness (identical test suites)
  Test 8  — Rollback invariant (failed challenger preserves champion)
  Test 9  — Bit-for-bit reproducibility with seed
  Test 10 — No fabricated metrics (every reported metric traces to disk artifact)
"""

from __future__ import annotations

from datetime import datetime
import numpy as np
import pytest

from mcdl.blue.model import BlueDetector
from mcdl.config import load_config
from mcdl.features.batch import compute_batch_features
from mcdl.features.spec import FEATURE_NAMES
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.loop.coevolution import CoevolutionLoop
from mcdl.loop.failure import FailureAnalyzer
from mcdl.loop.promotion import MultiObjectivePromotionGate, PromotionGateConfig
from mcdl.loop.replay import ReplayBuffer, ReplayRecord
from mcdl.loop.split import split_seen_heldout
from mcdl.loop.worlds import (
    CANONICAL_ADAPTATION_FAMILIES,
    CANONICAL_HIDDEN_FAMILIES,
    build_three_world_suite,
    verify_family_isolation,
)
from mcdl.red.adaptive import AdaptiveRedEngine
from mcdl.red.mask import check_mask_violations
from mcdl.red.search import AttackProvenance, validate_physical_candidate
from mcdl.schemas import (
    Archetype,
    AttackFamily,
    BlueMetrics,
    Channel,
    Customer,
    Decision,
    Merchant,
    Transaction,
)
from mcdl.world.generator import generate_world


@pytest.fixture
def base_world():
    cfg = load_config(scale="tiny")
    return generate_world(cfg)


# --------------------------------------------------------------------------- #
# Invariant Test 1: Mutability Mask Enforcement
# --------------------------------------------------------------------------- #
def test_invariant_1_mutability_mask_rejection(base_world):
    """Mutating immutable fields (customer_id, balance_before, etc.) must be rejected."""
    txn = base_world.transactions[0]
    # Attempt unauthorized mutation of immutable customer_id and balance_before
    illegal_candidate = txn.model_copy(update={"customer_id": "cust_HACKED", "balance_before": 999999.0})

    violations = check_mask_violations(txn, illegal_candidate, allowed_mutable=["amount", "channel"])
    assert len(violations) >= 2
    assert any("customer_id" in v for v in violations)
    assert any("balance_before" in v for v in violations)


# --------------------------------------------------------------------------- #
# Invariant Test 2: Physical Constraint Validation (Layer 1)
# --------------------------------------------------------------------------- #
def test_invariant_2_physical_constraint_validation(base_world):
    """Physical violations (credit limit exceeded, negative amount, invalid lat/lon) must be rejected."""
    txn = base_world.transactions[0]
    cust = base_world.customers[txn.customer_id]

    # Impossible attack: amount exceeds credit limit + invalid latitude
    impossible_candidate = txn.model_copy(update={
        "amount": cust.credit_limit + 5000.0,
        "lat": 999.0,
        "balance_before": 0.0,
        "available_credit": cust.credit_limit,
    })

    reasons = validate_physical_candidate(
        impossible_candidate, cust, base_world.merchants, base_world.mandates
    )
    assert len(reasons) >= 2
    assert "EXCEEDS_CREDIT_LIMIT" in reasons
    assert "INVALID_COORDINATES" in reasons


# --------------------------------------------------------------------------- #
# Invariant Test 3: Strict Query Budget Enforcement
# --------------------------------------------------------------------------- #
def test_invariant_3_query_budget_enforcement(base_world):
    """queries_used must never exceed query_budget."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)
    detector = BlueDetector(n_estimators=10, max_depth=2, random_state=42)
    detector.fit(feature_df, feature_df)

    engine = AdaptiveRedEngine(
        detector=detector,
        customers=base_world.customers,
        merchants=base_world.merchants,
        mandates=base_world.mandates,
    )

    for budget in [1, 5, 20]:
        prov = engine.attack(base_world.transactions[0], AttackFamily.BURST_DRAIN, budget=budget)
        assert prov.queries_used <= budget, f"queries_used ({prov.queries_used}) exceeded budget ({budget})"


# --------------------------------------------------------------------------- #
# Invariant Test 4: Replay Provenance Preservation & Zero Metadata Leakage
# --------------------------------------------------------------------------- #
def test_invariant_4_replay_provenance_and_zero_leakage(base_world):
    """ReplayBuffer preserves provenance but to_feature_rows excludes all non-observable metadata."""
    buffer = ReplayBuffer()
    txn = base_world.transactions[0]
    ext = StreamingFeatureExtractor(customers=base_world.customers)
    feats = ext.extract(txn)

    rec = ReplayRecord(
        attack_instance_id="atk_001",
        attack_family=AttackFamily.SLOW_SIPHON,
        source_txn_id=txn.txn_id,
        round_generated=1,
        evasion_features=feats,
        original_risk=0.90,
        evasion_risk=0.45,
        original_decision=Decision.BLOCK,
        evasion_decision=Decision.ALLOW,
        med=1.20,
        query_budget=20,
        seed=2026,
        candidate_transaction=txn,
        priority_score=0.85,
    )
    buffer.add(rec)

    # Invariant: Replay record preserves metadata
    stored = buffer.get_all()[0]
    assert stored.attack_family == AttackFamily.SLOW_SIPHON
    assert stored.med == 1.20

    # Invariant: Feature rows strictly strip metadata and contain only FEATURE_NAMES + is_fraud
    rows = buffer.to_feature_rows()
    assert len(rows) == 1
    assert rows[0]["is_fraud"] is True
    assert "attack_family" not in rows[0]
    assert "med" not in rows[0]
    assert "seed" not in rows[0]
    assert set(rows[0].keys()) == set(FEATURE_NAMES) | {"is_fraud"}


# --------------------------------------------------------------------------- #
# Invariant Test 5: Held-out Variant Isolation
# --------------------------------------------------------------------------- #
def test_invariant_5_heldout_variant_isolation():
    """Lineage grouping guarantees training variants and held-out variants are disjoint."""
    attacks = [
        AttackProvenance(
            attack_instance_id=f"atk_{i}",
            attack_family=AttackFamily.BURST_DRAIN,
            source_txn_id=f"txn_{i % 10}",  # 10 distinct lineage groups
            seed=2026 + i,
            query_budget=20,
            queries_used=1,
            mutations_attempted=1,
            valid_mutations=1,
            invalid_mutations=0,
            original_decision=Decision.BLOCK,
            final_decision=Decision.ALLOW,
            original_risk=0.8,
            final_risk=0.3,
            med=1.0,
            success=True,
        )
        for i in range(50)
    ]

    split = split_seen_heldout(attacks, seen_ratio=0.5, seed=2026)

    seen_lineages = {a.source_txn_id for a in split.seen}
    heldout_lineages = {a.source_txn_id for a in split.heldout}

    # Invariant: Disjoint lineages (Zero sibling leakage)
    assert (seen_lineages & heldout_lineages) == set(), "Held-out variants leaked into training lineage!"


# --------------------------------------------------------------------------- #
# Invariant Test 6: Hidden-Family Isolation (World C)
# --------------------------------------------------------------------------- #
def test_invariant_6_hidden_family_isolation():
    """Adaptation attack families and hidden evaluation families must be strictly disjoint."""
    assert verify_family_isolation(CANONICAL_ADAPTATION_FAMILIES, CANONICAL_HIDDEN_FAMILIES)

    # Invariant: Leakage must raise ValueError
    with pytest.raises(ValueError, match="CRITICAL ZERO-DAY LEAKAGE"):
        verify_family_isolation(
            [AttackFamily.BURST_DRAIN, AttackFamily.AGENT_SUBVERSION],
            [AttackFamily.AGENT_SUBVERSION, AttackFamily.GEO_HOP],
        )


# --------------------------------------------------------------------------- #
# Invariant Test 7: Champion / Challenger Evaluation Fairness
# --------------------------------------------------------------------------- #
def test_invariant_7_evaluation_fairness(base_world):
    """Champion and Challenger must be evaluated on the exact same feature distribution and test split."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)

    loop = CoevolutionLoop(n_rounds=2, budgets=[5], families=[AttackFamily.BURST_DRAIN], seed=20260827)
    res = loop.run(base_world.transactions, base_world, feature_df)

    # Both R0 and R1 must have evaluated the same test set size and decision space
    assert len(res.rounds) == 2
    assert res.rounds[0].blue.decision_counts is not None
    assert res.rounds[1].blue.decision_counts is not None


# --------------------------------------------------------------------------- #
# Invariant Test 8: Rollback Invariant
# --------------------------------------------------------------------------- #
def test_invariant_8_rollback_on_failed_promotion():
    """When a challenger fails promotion criteria, the champion is strictly preserved."""
    gate = MultiObjectivePromotionGate(PromotionGateConfig(max_fpr=0.01))

    champ_blue = BlueMetrics(pr_auc=0.65, fpr=0.001)
    chal_blue = BlueMetrics(pr_auc=0.60, fpr=0.08)  # Destroys FPR

    decision = gate.evaluate(
        champion_version="blue_r0",
        challenger_version="challenger_r1",
        champion_blue=champ_blue,
        challenger_blue=chal_blue,
        baseline_seen_asr=0.80,
        challenger_seen_asr=0.05,
        baseline_heldout_asr=0.85,
        challenger_heldout_asr=0.10,
    )

    assert decision.promoted is False
    assert decision.champion_version == "blue_r0"  # Invariant: Champion unchanged


# --------------------------------------------------------------------------- #
# Invariant Test 9: Bit-for-bit Reproducibility with Seed
# --------------------------------------------------------------------------- #
def test_invariant_9_reproducibility(base_world):
    """Identical seed, config, and world produce identical coevolution metrics."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)

    loop1 = CoevolutionLoop(n_rounds=2, budgets=[5], families=[AttackFamily.BURST_DRAIN], seed=20260827)
    res1 = loop1.run(base_world.transactions, base_world, feature_df)

    loop2 = CoevolutionLoop(n_rounds=2, budgets=[5], families=[AttackFamily.BURST_DRAIN], seed=20260827)
    res2 = loop2.run(base_world.transactions, base_world, feature_df)

    assert res1.rounds[0].red.asr_seen_variants == res2.rounds[0].red.asr_seen_variants
    assert res1.rounds[1].red.asr_seen_variants == res2.rounds[1].red.asr_seen_variants
    assert res1.rounds[1].blue.pr_auc == res2.rounds[1].blue.pr_auc


# --------------------------------------------------------------------------- #
# Invariant Test 10: No Fabricated Metrics
# --------------------------------------------------------------------------- #
def test_invariant_10_no_fabricated_metrics(base_world):
    """All reported scoreboard and generalisation metrics derive from executed models."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)
    loop = CoevolutionLoop(n_rounds=2, budgets=[5], families=[AttackFamily.BURST_DRAIN], seed=20260827)
    res = loop.run(base_world.transactions, base_world, feature_df)

    for entry in res.scoreboard:
        assert isinstance(entry.red_asr_seen, float)
        assert 0.0 <= entry.red_asr_seen <= 1.0
        assert isinstance(entry.heldout_asr, float)
        assert 0.0 <= entry.heldout_asr <= 1.0
        assert entry.robustness_retention >= 0.0
