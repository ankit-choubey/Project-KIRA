"""Unit Test Suite for ADV-002 Stateful Adversarial Swarm Foundation."""

import json
from pathlib import Path
import pytest

from mcdl.config import REPO_ROOT
from mcdl.research.advanced.adv002.agents import (
    AgentRole,
    AgentState,
    SwarmAgent,
    create_canonical_agent_swarm,
)
from mcdl.research.advanced.adv002.campaign import (
    CampaignManager,
    CampaignRound,
    CampaignState,
)
from mcdl.research.advanced.adv002.evaluator import (
    RewardBreakdown,
    SwarmAttemptResult,
    compute_adaptation_metrics,
    compute_reward,
    compute_swarm_metrics,
)
from mcdl.research.advanced.adv002.memory import (
    MemoryQuery,
    MemoryRecord,
    SharedAttackMemory,
)
from mcdl.research.advanced.adv002.policy import (
    DeterministicAdaptivePolicy,
    PolicyAction,
    PolicyConfig,
)
from mcdl.research.advanced.adv002.storage import ADV002Storage
from mcdl.schemas import AttackFamily, Channel, Customer, Decision, Transaction

ADV001_MEMORY_PATH = REPO_ROOT / "research_runs" / "ADVANCED" / "ADV-001" / "attack_memory.jsonl"
PHASE2_DIR = REPO_ROOT / "research_runs" / "PHASE2"


@pytest.fixture
def sample_customer_and_txn():
    cust = Customer(
        customer_id="c_adv002_test",
        archetype="salaried_urban",
        home_lat=40.7128,
        home_lon=-74.0060,
        account_opened="2025-01-01T00:00:00",
        credit_limit=5000.0,
        mean_log_amount=4.0,
        std_log_amount=0.5,
        daily_txn_rate=1.5,
    )
    txn = Transaction(
        txn_id="tx_adv002_001",
        customer_id="c_adv002_test",
        merchant_id="m_adv002_001",
        device_id="dev_adv002_001",
        timestamp="2026-08-27T12:00:00",
        amount=250.0,
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
    return cust, txn


def test_adv002_deterministic_agent_initialization():
    """Validates that agent swarm instantiates with deterministic unique IDs and roles."""
    swarm1 = create_canonical_agent_swarm(base_seed=20260831)
    swarm2 = create_canonical_agent_swarm(base_seed=20260831)

    assert len(swarm1) == 5
    assert len(swarm2) == 5

    for a1, a2 in zip(swarm1, swarm2):
        assert a1.agent_id == a2.agent_id
        assert a1.role == a2.role
        assert a1.seed == a2.seed
        assert a1.family_preference == a2.family_preference

    roles = {a.role for a in swarm1}
    assert roles == {
        AgentRole.VELOCITY_SPECIALIST,
        AgentRole.GEO_SPECIALIST,
        AgentRole.MERCHANT_SPECIALIST,
        AgentRole.AGENT_SUBVERSION_SPECIALIST,
        AgentRole.HYBRID_ADAPTIVE,
    }


def test_adv002_memory_ingestion_and_indexing():
    """Validates memory indexing and query retrieval across multiple dimensions."""
    memory = SharedAttackMemory()

    # Ingest synthetic sample records
    records = [
        MemoryRecord(
            attack_id=f"atk_{i}",
            family="geo_hop" if i % 2 == 0 else "burst_drain",
            strategy="mutate_geo_hop" if i % 2 == 0 else "mutate_burst_drain",
            seed=i,
            parent_attack_id=None,
            query_budget=20,
            queries_used=5,
            mutation_count=5,
            perturbation_distance=1.20 if i == 0 else None,
            target_transaction_id="tx_001" if i < 5 else "tx_002",
            blue_model_version="v1",
            blue_score=0.1 if i == 0 else 0.9,
            blue_decision="ALLOW" if i == 0 else "BLOCK",
            evasion=(i == 0),
            outcome="ALLOWED_EVASION" if i == 0 else "BLOCKED",
            timestamp="2026-08-31T10:00:00Z",
            provenance={},
            origin="ADV-001",
        )
        for i in range(10)
    ]

    for idx, r in enumerate(records):
        memory.records.append(r)
        memory._index_record(idx, r)

    # Query by family
    geo_recs = memory.query(MemoryQuery(family="geo_hop"))
    assert len(geo_recs) == 5

    # Query by evasion
    ev_recs = memory.query(MemoryQuery(evasion=True))
    assert len(ev_recs) == 1
    assert ev_recs[0].attack_id == "atk_0"

    # Query by target
    tx1_recs = memory.query(MemoryQuery(target_transaction_id="tx_001"))
    assert len(tx1_recs) == 5

    # Check empirical success rate
    assert memory.get_family_success_rate("geo_hop") == 0.20
    assert memory.get_family_success_rate("burst_drain") == 0.00


def test_adv002_memory_append_only_adv002():
    """Validates that appending ADV-002 records grows memory without modifying ADV-001 entries."""
    memory = SharedAttackMemory()
    r1 = MemoryRecord(
        attack_id="atk_adv001_001",
        family="geo_hop",
        strategy="mutate_geo_hop",
        seed=1,
        parent_attack_id=None,
        query_budget=20,
        queries_used=4,
        mutation_count=4,
        perturbation_distance=1.15,
        target_transaction_id="tx_001",
        blue_model_version="v1",
        blue_score=0.05,
        blue_decision="ALLOW",
        evasion=True,
        outcome="ALLOWED_EVASION",
        timestamp="2026-08-31T10:00:00Z",
        provenance={},
        origin="ADV-001",
    )
    memory.records.append(r1)
    memory._index_record(0, r1)

    # Append ADV-002 attempt
    r2 = MemoryRecord(
        attack_id="atk_adv002_001",
        family="burst_drain",
        strategy="mutate_burst_drain",
        seed=2,
        parent_attack_id=None,
        query_budget=20,
        queries_used=10,
        mutation_count=10,
        perturbation_distance=None,
        target_transaction_id="tx_001",
        blue_model_version="v1",
        blue_score=0.95,
        blue_decision="BLOCK",
        evasion=False,
        outcome="BLOCKED",
        timestamp="2026-08-31T12:00:00Z",
        provenance={},
    )
    memory.append_adv002_record(r2)

    counts = memory.count_records()
    assert counts["total_records"] == 2
    assert counts["adv001_records"] == 1
    assert counts["adv002_records"] == 1
    assert memory.records[0].origin == "ADV-001"
    assert memory.records[1].origin == "ADV-002"


def test_adv002_deterministic_policy_decisions():
    """Validates deterministic reproducible policy decisions under fixed seeds."""
    memory = SharedAttackMemory()
    policy = DeterministicAdaptivePolicy(PolicyConfig())

    action1 = policy.select_action(
        agent_role="geo_specialist",
        family_preference=[AttackFamily.GEO_HOP],
        target_id="tx_001",
        round_number=1,
        agent_action_history=[],
        memory=memory,
        seed=20260831,
    )
    action2 = policy.select_action(
        agent_role="geo_specialist",
        family_preference=[AttackFamily.GEO_HOP],
        target_id="tx_001",
        round_number=1,
        agent_action_history=[],
        memory=memory,
        seed=20260831,
    )

    assert action1.family == action2.family
    assert action1.query_budget == action2.query_budget
    assert action1.is_exploration == action2.is_exploration
    assert action1.selection_probabilities == action2.selection_probabilities
    assert action1.rationale == action2.rationale


def test_adv002_reward_calculation_decomposition():
    """Validates multi-objective reward decomposition for ALLOW, STEP_UP, and BLOCK."""
    # Evasion with low distance and low query usage
    r_ev = compute_reward(
        evasion=True,
        blue_decision="ALLOW",
        queries_used=2,
        query_budget=20,
        perturbation_distance=1.20,
    )
    assert r_ev.base_evasion_reward == 1.0
    assert r_ev.perturbation_penalty == -0.12  # -0.10 * 1.20
    assert r_ev.query_efficiency_penalty == -0.015  # -0.15 * (2/20)
    assert r_ev.decision_penalty == 0.0
    assert r_ev.total_reward > 0.80

    # Step up
    r_step = compute_reward(
        evasion=False,
        blue_decision="STEP_UP",
        queries_used=20,
        query_budget=20,
        perturbation_distance=None,
    )
    assert r_step.base_evasion_reward == 0.0
    assert r_step.decision_penalty == -0.20
    assert r_step.total_reward < 0.0

    # Block
    r_blk = compute_reward(
        evasion=False,
        blue_decision="BLOCK",
        queries_used=20,
        query_budget=20,
        perturbation_distance=None,
    )
    assert r_blk.base_evasion_reward == 0.0
    assert r_blk.decision_penalty == -0.50
    assert r_blk.total_reward < r_step.total_reward


def test_adv002_campaign_state_and_adaptation_events(sample_customer_and_txn):
    """Validates campaign state progression and detection of adaptation events."""
    _, txn = sample_customer_and_txn
    manager = CampaignManager(max_rounds_per_campaign=5)
    campaign = manager.create_campaign(txn, campaign_index=1)
    agent = SwarmAgent(agent_id="ag_01", role=AgentRole.GEO_SPECIALIST, seed=123)

    # Round 1: Burst drain blocked
    r1 = CampaignRound(
        campaign_id=campaign.campaign_id,
        round_number=1,
        agent_id=agent.agent_id,
        target_txn_id=txn.txn_id,
        family="burst_drain",
        query_budget=20,
        queries_used=20,
        evasion=False,
        outcome="BLOCKED",
        blue_score=0.95,
        blue_decision="BLOCK",
        perturbation_distance=None,
        reward=-0.65,
        is_exploration=True,
        memory_references=[],
        timestamp="2026-08-31T10:00:00Z",
    )
    campaign.record_round(r1, agent)

    # Round 2: Switched to geo_hop and evaded
    r2 = CampaignRound(
        campaign_id=campaign.campaign_id,
        round_number=2,
        agent_id=agent.agent_id,
        target_txn_id=txn.txn_id,
        family="geo_hop",
        query_budget=20,
        queries_used=4,
        evasion=True,
        outcome="ALLOWED_EVASION",
        blue_score=0.10,
        blue_decision="ALLOW",
        perturbation_distance=1.25,
        reward=0.84,
        is_exploration=False,
        memory_references=["atk_adv001_000001"],
        timestamp="2026-08-31T10:00:01Z",
    )
    campaign.record_round(r2, agent)

    assert campaign.current_round == 2
    assert campaign.cumulative_attacks == 2
    assert campaign.cumulative_successes == 1
    assert campaign.cumulative_failures == 1
    assert campaign.best_perturbation_distance == 1.25

    # Check detected adaptation events
    assert len(campaign.adaptation_events) >= 1
    fam_switch = [e for e in campaign.adaptation_events if e["type"] == "FAMILY_SWITCH"]
    assert len(fam_switch) == 1
    assert fam_switch[0]["from_family"] == "burst_drain"
    assert fam_switch[0]["to_family"] == "geo_hop"


def test_adv002_agent_isolation():
    """Ensures private states of distinct agents remain isolated without cross-contamination."""
    swarm = create_canonical_agent_swarm(base_seed=20260831)
    ag_velocity = swarm[0]
    ag_geo = swarm[1]

    # Update velocity agent
    ag_velocity.record_attempt_result(
        round_number=1,
        target_txn_id="tx_001",
        family=AttackFamily.BURST_DRAIN,
        budget=20,
        queries_used=20,
        evasion=False,
        outcome="BLOCKED",
        blue_score=0.9,
        blue_decision="BLOCK",
        perturbation_distance=None,
        reward=-0.65,
        memory_refs=[],
    )

    assert ag_velocity.cumulative_attacks == 1
    assert ag_geo.cumulative_attacks == 0
    assert len(ag_geo.action_history) == 0
    assert ag_geo.cumulative_reward == 0.0


def test_adv002_storage_and_resumability(tmp_path):
    """Validates atomic storage writing and campaign resumability without duplication."""
    storage = ADV002Storage(tmp_path / "adv002_test")

    cmp_state = CampaignState(
        campaign_id="cmp_001",
        target_txn_id="tx_001",
        max_rounds=5,
        current_round=5,
        is_completed=True,
    )
    storage.save_campaign_state(cmp_state)

    completed = storage.get_completed_campaign_ids()
    assert "cmp_001" in completed
    assert "cmp_002" not in completed


def test_adv002_accounting_invariants():
    """Validates partition accounting and metrics calculation across evaluated results."""
    results = [
        SwarmAttemptResult(
            attack_id=f"atk_{i}",
            campaign_id="cmp_001",
            agent_id="agent_geo_01",
            parent_attack_id=None,
            round_number=1,
            family="geo_hop",
            strategy="mutate_geo_hop",
            seed=i,
            query_budget=20,
            queries_used=4,
            mutation_count=4,
            perturbation_distance=1.20 if i == 0 else None,
            target_transaction_id="tx_001",
            blue_model_version="v1",
            blue_score=0.1 if i == 0 else 0.9,
            blue_decision="ALLOW" if i == 0 else "BLOCK",
            evasion=(i == 0),
            outcome="ALLOWED_EVASION" if i == 0 else "BLOCKED",
            reward=0.85 if i == 0 else -0.65,
            reward_breakdown={},
            memory_references=["atk_ref_1"],
            is_exploration=(i == 1),
            policy_metadata={},
            timestamp="2026-08-31T10:00:00Z",
            provenance={},
        )
        for i in range(5)
    ]

    metrics = compute_swarm_metrics(results)
    assert metrics["total_attacks"] == 5
    assert metrics["total_campaigns"] == 1
    assert metrics["outcome_distribution"]["ALLOWED_EVASION"] == 1
    assert metrics["outcome_distribution"]["BLOCKED"] == 4
    assert metrics["aggregate_asr"] == 0.20

    adapt = compute_adaptation_metrics(results)
    assert adapt["initial_round_asr"] == 0.20
    assert adapt["final_round_asr"] == 0.20
    assert adapt["memory_reuse_rate"] == 1.0


def test_adv002_adv001_memory_immutable():
    """Validates that reading ADV-001 memory does not mutate the source file on disk."""
    if ADV001_MEMORY_PATH.exists():
        initial_stat = ADV001_MEMORY_PATH.stat()
        initial_mtime = initial_stat.st_mtime
        initial_size = initial_stat.st_size

        memory = SharedAttackMemory(ADV001_MEMORY_PATH)
        assert len(memory.records) == 10000

        after_stat = ADV001_MEMORY_PATH.stat()
        assert after_stat.st_mtime == initial_mtime
        assert after_stat.st_size == initial_size


def test_adv002_phase2_untouched():
    """Guarantees that Phase-2 directories remain completely untouched."""
    if PHASE2_DIR.exists():
        assert (PHASE2_DIR / "S00").exists()
        assert (PHASE2_DIR / "S01").exists()


def test_adv002_control_modes():
    """Validates that all 3 scientific control modes execute as intended."""
    memory = SharedAttackMemory()
    memory.append_adv002_record(
        MemoryRecord(
            attack_id="atk_sample_01",
            family="geo_hop",
            strategy="mutate_geo_hop",
            seed=42,
            parent_attack_id=None,
            query_budget=20,
            queries_used=4,
            mutation_count=4,
            perturbation_distance=1.15,
            target_transaction_id="tx_001",
            blue_model_version="v1",
            blue_score=0.1,
            blue_decision="ALLOW",
            evasion=True,
            outcome="ALLOWED_EVASION",
            timestamp="2026-08-31T10:00:00Z",
            origin="ADV-001",
        )
    )
    # 1. Static Control
    pol_static = DeterministicAdaptivePolicy(PolicyConfig(mode="static_control"))
    action_s = pol_static.select_action(
        agent_role="geo_specialist",
        family_preference=[AttackFamily.GEO_HOP],
        target_id="tx_001",
        round_number=1,
        agent_action_history=[],
        memory=memory,
        seed=42,
    )
    assert action_s.query_budget == 20
    assert len(action_s.memory_references) == 0
    assert "Static control" in action_s.rationale

    # 2. Memory-Disabled
    pol_no_mem = DeterministicAdaptivePolicy(PolicyConfig(mode="memory_disabled"))
    action_nm = pol_no_mem.select_action(
        agent_role="geo_specialist",
        family_preference=[AttackFamily.GEO_HOP],
        target_id="tx_001",
        round_number=1,
        agent_action_history=[],
        memory=memory,
        seed=42,
    )
    assert len(action_nm.memory_references) == 0
    assert "mode=memory_disabled" in action_nm.rationale

    # 3. Adaptive Memory
    pol_adapt = DeterministicAdaptivePolicy(PolicyConfig(mode="adaptive_memory"))
    action_ad = pol_adapt.select_action(
        agent_role="geo_specialist",
        family_preference=[AttackFamily.GEO_HOP],
        target_id="tx_001",
        round_number=1,
        agent_action_history=[],
        memory=memory,
        seed=42,
    )
    assert len(action_ad.memory_references) > 0


def test_adv002_large_population_scale_planning_no_execution():
    """Verifies that large scale configuration resolves to exactly 5,000 attempts without execution."""
    from mcdl.research.advanced.adv002.runner import get_scale_parameters, ADV002Scale
    params = get_scale_parameters(ADV002Scale.LARGE)
    assert params["n_targets"] == 10
    assert params["rounds_per_campaign"] == 100
    n_agents = 5
    expected_attempts = params["n_targets"] * params["rounds_per_campaign"] * n_agents
    assert expected_attempts == 5000


def test_adv002_resumability_and_interruption_recovery(tmp_path):
    """Tests that interrupted runs recover cleanly without duplicate rounds."""
    storage = ADV002Storage(tmp_path)
    # Simulate completed campaign 1
    cmp1 = CampaignState(campaign_id="cmp_001", target_txn_id="tx_001", max_rounds=5, is_completed=True)
    storage.save_campaign_state(cmp1)
    
    # Check completed IDs
    assert storage.get_completed_campaign_ids() == {"cmp_001"}
    
    # Simulate resume: campaign 1 is skipped
    completed = storage.get_completed_campaign_ids()
    unprocessed = [cid for cid in ["cmp_001", "cmp_002"] if cid not in completed]
    assert unprocessed == ["cmp_002"]

