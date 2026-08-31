"""Unit Tests for Adversarial Coevolution Loop Components."""

from datetime import datetime
import numpy as np
import polars as pl
import pytest

from mcdl.blue.model import BlueDetector
from mcdl.config import load_config
from mcdl.features.batch import compute_batch_features
from mcdl.features.spec import FEATURE_NAMES
from mcdl.loop.challenger import ChallengerTrainer, evaluate_promotion
from mcdl.loop.metrics import compute_generalisation_metrics
from mcdl.loop.replay import ReplayBuffer, ReplayRecord
from mcdl.loop.split import split_seen_heldout
from mcdl.red.search import AttackProvenance
from mcdl.schemas import AttackFamily, BlueMetrics, Channel, Decision, Transaction
from mcdl.world.generator import generate_world


def test_replay_buffer_deduplication_and_feature_isolation():
    """Verifies that ReplayBuffer deduplicates by ID and strictly excludes metadata from feature rows."""
    buf = ReplayBuffer()
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    dummy_txn = Transaction(
        txn_id="tx_1",
        customer_id="c_1",
        merchant_id="m_1",
        device_id="d_1",
        timestamp=t0,
        amount=50.0,
        mcc="5411",
        channel=Channel.CARD_PRESENT,
        lat=40.0,
        lon=-74.0,
        ip_prefix="10.0",
        is_new_device=False,
        auth_failed_count=0,
        balance_before=100.0,
        available_credit=4900.0,
        is_fraud=True,
    )

    rec1 = ReplayRecord(
        attack_instance_id="atk_1",
        attack_family=AttackFamily.BURST_DRAIN,
        source_txn_id="tx_1",
        round_generated=0,
        evasion_features={"amount": 50.0, "log_amount": 3.93},
        original_risk=0.95,
        evasion_risk=0.05,
        original_decision=Decision.BLOCK,
        evasion_decision=Decision.ALLOW,
        med=2.1,
        query_budget=20,
        seed=42,
        candidate_transaction=dummy_txn,
    )

    # 1. Insertion
    assert buf.add(rec1) is True
    # 2. Deduplication on identical ID
    assert buf.add(rec1) is False
    assert len(buf) == 1

    # 3. Feature matrix isolation
    feature_rows = buf.to_feature_rows()
    assert len(feature_rows) == 1
    row = feature_rows[0]
    assert row["is_fraud"] is True
    # Verify no metadata fields in row
    for metadata_field in ["attack_family", "attack_instance_id", "med", "seed", "query_budget"]:
        assert metadata_field not in row
    # Verify exact feature names
    for f in FEATURE_NAMES:
        assert f in row


def test_lineage_grouped_seen_heldout_split():
    """Asserts that lineage grouping prevents siblings from the same source txn from leaking between sets."""
    attacks = []
    for i in range(10):
        src_id = f"tx_src_{i}"
        for b in [1, 5, 20, 100]:
            at = AttackProvenance(
                attack_instance_id=f"atk_{src_id}_bd_{b}",
                attack_family=AttackFamily.BURST_DRAIN,
                source_txn_id=src_id,
                seed=42 + b,
                query_budget=b,
                queries_used=b,
                mutations_attempted=b,
                valid_mutations=b,
                invalid_mutations=0,
                original_decision=Decision.BLOCK,
                final_decision=Decision.ALLOW,
                original_risk=0.9,
                final_risk=0.1,
                med=1.5,
                success=True,
            )
            attacks.append(at)

    split = split_seen_heldout(attacks, seen_ratio=0.5, seed=12345)

    seen_ids = set(a.attack_instance_id for a in split.seen)
    heldout_ids = set(a.attack_instance_id for a in split.heldout)
    # Zero ID overlap
    assert len(seen_ids & heldout_ids) == 0

    seen_sources = set(a.source_txn_id for a in split.seen)
    heldout_sources = set(a.source_txn_id for a in split.heldout)
    # Strict lineage separation: no source txn appears in both seen and held-out
    assert len(seen_sources & heldout_sources) == 0


def test_promotion_evaluation_criteria():
    """Verifies promotion rules: security gain accepted, regression or pathological blocking rejected."""
    # 1. Successful promotion (reduced seen/held-out ASR, low FPR, high approval)
    promoted, reasons = evaluate_promotion(
        baseline_seen_asr=0.90,
        challenger_seen_asr=0.40,
        baseline_heldout_asr=0.85,
        challenger_heldout_asr=0.50,
        fpr=0.01,
        allow_rate=0.92,
        pr_auc=0.95,
    )
    assert promoted is True
    assert "PROMOTED_SECURITY_IMPROVEMENT" in reasons

    # 2. Pathological model rejection (blocking everything -> allow_rate < 0.70)
    promoted_pathological, r_path = evaluate_promotion(
        baseline_seen_asr=0.90,
        challenger_seen_asr=0.10,
        baseline_heldout_asr=0.85,
        challenger_heldout_asr=0.10,
        fpr=0.01,
        allow_rate=0.40,  # blocks 60% of benign traffic!
        pr_auc=0.95,
    )
    assert promoted_pathological is False
    assert any("REJECT_LOW_APPROVAL_RATE" in r for r in r_path)

    # 3. Excessive FPR rejection
    promoted_high_fpr, r_fpr = evaluate_promotion(
        baseline_seen_asr=0.90,
        challenger_seen_asr=0.40,
        baseline_heldout_asr=0.85,
        challenger_heldout_asr=0.50,
        fpr=0.15,  # FPR > 0.08
        allow_rate=0.85,
        pr_auc=0.90,
    )
    assert promoted_high_fpr is False
    assert any("REJECT_EXCESSIVE_FPR" in r for r in r_fpr)
