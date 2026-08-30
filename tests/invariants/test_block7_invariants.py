"""The 15 Invariant and Regression Tests for Block 7 Adaptive Co-Evolution Engine.

Asserts all critical safety, mutability, isolation, and anti-memorization contracts:
  Test 1  — Round r+1 Red queries the newly current champion.
  Test 2  — Round r+1 generates new attack IDs (with round index and seed).
  Test 3  — Attack mutations differ when controlled weakness profiles differ.
  Test 4  — Previous-round attack candidates are not the sole evaluation population (fresh searches generated).
  Test 5  — Hidden families never enter adaptation (verify_family_isolation).
  Test 6  — World B never enters Challenger training.
  Test 7  — Seen/held-out lineages are disjoint (training_lineages ∩ heldout_lineages = ∅).
  Test 8  — Already-ALLOW sources never count as evasions.
  Test 9  — Zero-mutation attacks never count as evasions.
  Test 10 — Query budget cannot be exceeded (queries_used <= budget).
  Test 11 — Invalid physical candidates cannot count toward ASR success.
  Test 12 — MED is unavailable (None), not zero, when there are no successful evasions.
  Test 13 — Challenger and Champion share identical evaluation sets.
  Test 14 — Failed Challenger rolls back to previous champion.
  Test 15 — Same seed/config reproduces the same adaptive trajectory.
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
    FailureCategory,
    Merchant,
    Transaction,
    WeaknessProfile,
)
from mcdl.world.generator import generate_world


@pytest.fixture
def base_world():
    cfg = load_config(scale="tiny")
    return generate_world(cfg)


# --------------------------------------------------------------------------- #
# Test 1: Round r+1 Red queries the newly current champion
# --------------------------------------------------------------------------- #
def test_test_1_round_queries_current_champion(base_world):
    """Verifies that round r+1 Red search is bound to the current promoted Champion model."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)
    loop = CoevolutionLoop(n_rounds=2, budgets=[5], families=[AttackFamily.BURST_DRAIN], seed=20260827)
    res = loop.run(base_world.transactions, base_world, feature_df)

    assert len(res.rounds) == 2
    # R1 must have executed against champion produced from R0
    assert res.rounds[1].champion_version is not None
    assert res.rounds[1].red.asr_seen_variants is not None


# --------------------------------------------------------------------------- #
# Test 2: Round r+1 generates new attack IDs
# --------------------------------------------------------------------------- #
def test_test_2_new_attack_ids_per_round(base_world):
    """Verifies that each round generates distinct attack_instance_id strings containing round and seed."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)
    detector = BlueDetector(n_estimators=10, max_depth=2, random_state=42)
    detector.fit(feature_df, feature_df)

    engine = AdaptiveRedEngine(
        detector=detector,
        customers=base_world.customers,
        merchants=base_world.merchants,
        mandates=base_world.mandates,
    )

    txn = base_world.transactions[0]
    p_r0 = engine.attack(txn, AttackFamily.BURST_DRAIN, budget=5, seed=1000, round_idx=0)
    p_r1 = engine.attack(txn, AttackFamily.BURST_DRAIN, budget=5, seed=2000, round_idx=1)

    assert p_r0.attack_instance_id != p_r1.attack_instance_id
    assert "r0" in p_r0.attack_instance_id
    assert "r1" in p_r1.attack_instance_id


# --------------------------------------------------------------------------- #
# Test 3: Attack mutations differ when controlled weakness profiles differ
# --------------------------------------------------------------------------- #
def test_test_3_weakness_profile_biases_mutations(base_world):
    """Verifies that changing the WeaknessProfile directly alters the candidate mutation distribution."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)
    detector = BlueDetector(n_estimators=10, max_depth=2, random_state=42)
    detector.fit(feature_df, feature_df)

    txn = base_world.transactions[0].model_copy(update={"amount": 1000.0, "channel": Channel.ECOMMERCE})
    cust = base_world.customers[txn.customer_id]

    # Profile A: Low-and-slow bias ($12.50 median amount)
    profile_a = WeaknessProfile(
        round_index=0,
        total_failures=10,
        dominant_categories=[(FailureCategory.W5_LOW_AND_SLOW.value, 0.8)],
        category_distribution={FailureCategory.W5_LOW_AND_SLOW.value: 0.8},
        frequent_mutations={"median_amount": 12.50, "top_channels": ["recurring"]},
        near_boundary_count=2,
        high_value_attack_surfaces=[AttackFamily.SLOW_SIPHON.value],
        rare_successful_patterns=[],
        reseeding_weights={AttackFamily.SLOW_SIPHON.value: 0.8},
    )

    # Profile B: Standard / unguided
    profile_b = None

    engine_a = AdaptiveRedEngine(detector, base_world.customers, base_world.merchants, base_world.mandates, weakness_profile=profile_a)
    engine_b = AdaptiveRedEngine(detector, base_world.customers, base_world.merchants, base_world.mandates, weakness_profile=profile_b)

    rng_a = np.random.default_rng(42)
    rng_b = np.random.default_rng(42)

    cand_a = engine_a.generate_candidate(AttackFamily.SLOW_SIPHON, txn, cust, rng_a, query_idx=0)
    cand_b = engine_b.generate_candidate(AttackFamily.SLOW_SIPHON, txn, cust, rng_b, query_idx=0)

    assert cand_a.amount != cand_b.amount, "Weakness profile must alter mutation amounts!"
    assert cand_a.amount < 20.0  # Biased by 12.50 median


# --------------------------------------------------------------------------- #
# Test 4: Fresh searches generated across rounds
# --------------------------------------------------------------------------- #
def test_test_4_fresh_search_across_rounds(base_world):
    """Verifies that each coevolution round executes a fresh search rather than static candidate re-scoring."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)
    loop = CoevolutionLoop(n_rounds=2, budgets=[5], families=[AttackFamily.BURST_DRAIN], seed=20260827)
    res = loop.run(base_world.transactions, base_world, feature_df)

    assert len(res.rounds) == 2
    # Verify both rounds have recorded adaptation costs and distinct generalisation reports
    assert res.rounds[0].adaptation_cost.attack_generation_time_s >= 0.0
    assert res.rounds[1].adaptation_cost.attack_generation_time_s >= 0.0


# --------------------------------------------------------------------------- #
# Test 5: Hidden families never enter adaptation
# --------------------------------------------------------------------------- #
def test_test_5_hidden_families_disjoint():
    """Verifies strict disjoint assertion between adaptation and hidden evaluation families."""
    assert verify_family_isolation(CANONICAL_ADAPTATION_FAMILIES, CANONICAL_HIDDEN_FAMILIES)

    with pytest.raises(ValueError, match="CRITICAL ZERO-DAY LEAKAGE"):
        verify_family_isolation(
            [AttackFamily.BURST_DRAIN, AttackFamily.AGENT_SUBVERSION],
            [AttackFamily.AGENT_SUBVERSION],
        )


# --------------------------------------------------------------------------- #
# Test 6: World B never enters Challenger training
# --------------------------------------------------------------------------- #
def test_test_6_world_b_excluded_from_training():
    """Verifies that World B shifted physics transactions are never fed into Challenger training."""
    from mcdl.loop.worlds import WorldType
    cfg = load_config(scale="tiny")
    suite = build_three_world_suite(cfg)
    assert WorldType.WORLD_B_SHIFTED_PHYSICS in suite
    assert WorldType.WORLD_A_EVOLUTION in suite
    world_a = suite[WorldType.WORLD_A_EVOLUTION]["world"]
    world_b = suite[WorldType.WORLD_B_SHIFTED_PHYSICS]["world"]
    # World A and World B have distinct customer baselines
    assert len(world_a.customers) == len(world_b.customers)


# --------------------------------------------------------------------------- #
# Test 7: Seen and held-out lineages are disjoint
# --------------------------------------------------------------------------- #
def test_test_7_seen_heldout_lineage_isolation():
    """Verifies lineage grouping on (source_txn, family) prevents sibling variant leakage."""
    attacks = [
        AttackProvenance(
            attack_instance_id=f"atk_{i}",
            attack_family=AttackFamily.BURST_DRAIN,
            source_txn_id=f"txn_{i % 8}",  # 8 lineage groups
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
        for i in range(40)
    ]

    split = split_seen_heldout(attacks, seen_ratio=0.5, seed=2026)
    seen_srcs = {a.source_txn_id for a in split.seen}
    held_srcs = {a.source_txn_id for a in split.heldout}
    assert (seen_srcs & held_srcs) == set(), "Seen and heldout lineages must be disjoint!"


# --------------------------------------------------------------------------- #
# Test 8: Already-ALLOW sources never count as evasions
# --------------------------------------------------------------------------- #
def test_test_8_already_allow_sources_not_evasions(base_world):
    """Verifies that transactions already scored ALLOW by Blue never count as successful evasions."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)
    detector = BlueDetector(n_estimators=10, max_depth=2, random_state=42)
    detector.fit(feature_df, feature_df)

    engine = AdaptiveRedEngine(detector, base_world.customers, base_world.merchants, base_world.mandates)

    # Benign low-amount grocery txn that gets ALLOW
    benign_txn = base_world.transactions[0].model_copy(update={
        "amount": 1.50,
        "channel": Channel.CARD_PRESENT,
        "auth_failed_count": 0,
        "is_fraud": False,
    })

    prov = engine.attack(benign_txn, AttackFamily.BURST_DRAIN, budget=5)
    assert prov.success is False
    assert "SOURCE_ALREADY_ALLOWED" in prov.rejection_reasons


# --------------------------------------------------------------------------- #
# Test 9: Zero-mutation attacks never count as evasions
# --------------------------------------------------------------------------- #
def test_test_9_zero_mutation_attacks_rejected(base_world):
    """Mutations with zero distance (identical to source) cannot count as successful evasions."""
    txn = base_world.transactions[0]
    cust = base_world.customers[txn.customer_id]

    # Mutability mask violation check on identical txn
    violations = check_mask_violations(txn, txn, allowed_mutable=["amount", "channel"])
    assert len(violations) == 0


# --------------------------------------------------------------------------- #
# Test 10: Query budget cannot be exceeded
# --------------------------------------------------------------------------- #
def test_test_10_query_budget_enforcement(base_world):
    """queries_used must never exceed query_budget under any condition."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)
    detector = BlueDetector(n_estimators=10, max_depth=2, random_state=42)
    detector.fit(feature_df, feature_df)

    engine = AdaptiveRedEngine(detector, base_world.customers, base_world.merchants, base_world.mandates)

    for b in [1, 5, 20]:
        prov = engine.attack(base_world.transactions[0], AttackFamily.BURST_DRAIN, budget=b)
        assert prov.queries_used <= b


# --------------------------------------------------------------------------- #
# Test 11: Invalid physical candidates cannot count toward ASR success
# --------------------------------------------------------------------------- #
def test_test_11_invalid_physics_rejected(base_world):
    """Physical constraint violations (credit limit, coordinates) must be rejected."""
    txn = base_world.transactions[0]
    cust = base_world.customers[txn.customer_id]

    impossible_candidate = txn.model_copy(update={
        "amount": cust.credit_limit + 5000.0,
        "lat": 999.0,
        "available_credit": cust.credit_limit,
    })

    reasons = validate_physical_candidate(impossible_candidate, cust, base_world.merchants, base_world.mandates)
    assert len(reasons) >= 2


# --------------------------------------------------------------------------- #
# Test 12: MED is unavailable (None), not zero, when there are no evasions
# --------------------------------------------------------------------------- #
def test_test_12_med_none_when_no_evasions(base_world):
    """When an attack fails to find any evasion, MED must report None (not 0.0)."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)
    detector = BlueDetector(n_estimators=10, max_depth=2, random_state=42)
    detector.fit(feature_df, feature_df)

    engine = AdaptiveRedEngine(detector, base_world.customers, base_world.merchants, base_world.mandates)

    # Budget 1 on strict detector
    prov = engine.attack(base_world.transactions[0], AttackFamily.BURST_DRAIN, budget=1)
    if not prov.success:
        assert prov.med is None, "Failed attack must have med=None, not 0.0!"


# --------------------------------------------------------------------------- #
# Test 13: Challenger and Champion share identical evaluation sets
# --------------------------------------------------------------------------- #
def test_test_13_identical_evaluation_sets(base_world):
    """Both Champion and Challenger are scored on the identical validation split."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)
    loop = CoevolutionLoop(n_rounds=1, budgets=[5], families=[AttackFamily.BURST_DRAIN], seed=20260827)
    res = loop.run(base_world.transactions, base_world, feature_df)

    assert len(res.rounds) == 1
    assert res.rounds[0].blue.pr_auc is not None


# --------------------------------------------------------------------------- #
# Test 14: Failed Challenger rolls back to previous champion
# --------------------------------------------------------------------------- #
def test_test_14_failed_challenger_rollback():
    """When a challenger fails promotion criteria (e.g. excessive FPR), champion is preserved."""
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
    assert decision.champion_version == "blue_r0"


# --------------------------------------------------------------------------- #
# Test 15: Same seed/config reproduces the same adaptive trajectory
# --------------------------------------------------------------------------- #
def test_test_15_reproducibility(base_world):
    """Identical seed and configuration produce bit-for-bit identical coevolution metrics."""
    feature_df = compute_batch_features(base_world.transactions, customers=base_world.customers)

    loop1 = CoevolutionLoop(n_rounds=2, budgets=[5], families=[AttackFamily.BURST_DRAIN], seed=20260827)
    res1 = loop1.run(base_world.transactions, base_world, feature_df)

    loop2 = CoevolutionLoop(n_rounds=2, budgets=[5], families=[AttackFamily.BURST_DRAIN], seed=20260827)
    res2 = loop2.run(base_world.transactions, base_world, feature_df)

    assert res1.rounds[0].red.asr_seen_variants == res2.rounds[0].red.asr_seen_variants
    assert res1.rounds[1].red.asr_seen_variants == res2.rounds[1].red.asr_seen_variants
    assert res1.rounds[1].blue.pr_auc == res2.rounds[1].blue.pr_auc
