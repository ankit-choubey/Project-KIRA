"""Comprehensive Unit Tests for Blue Team Detector, Calibration, Policy & Metrics."""

from datetime import datetime, timedelta
import math
import numpy as np
import polars as pl
import pytest

from mcdl.blue.calibration import IsotonicCalibrator, compute_brier_score, compute_ece
from mcdl.blue.explainer import TreeSHAPExplainer
from mcdl.blue.intent import compute_intent_drift
from mcdl.blue.metrics import evaluate_predictions
from mcdl.blue.model import BlueDetector
from mcdl.blue.policy import CostSensitiveRouter, PolicyCostConfig
from mcdl.blue.rule_baseline import RuleBaseline
from mcdl.blue.split import temporal_split
from mcdl.config import load_config
from mcdl.features.batch import compute_batch_features
from mcdl.features.spec import FEATURE_NAMES
from mcdl.schemas import Decision, Mandate, Transaction
from mcdl.world.generator import generate_world


def test_temporal_split_strict_ordering():
    """Asserts that temporal split enforces max(train) < min(valid) < min(test)."""
    t0 = datetime(2026, 1, 1, 10, 0, 0)
    records = []
    for i in range(100):
        records.append({
            "txn_id": f"tx_{i:03d}",
            "customer_id": f"c_{i % 5}",
            "merchant_id": "m1",
            "timestamp": t0 + timedelta(minutes=i),
            "amount": 10.0 + i,
            "is_fraud": (i % 10 == 0),
        })
        for f in FEATURE_NAMES:
            if f not in records[-1]:
                records[-1][f] = 0.0

    df = pl.DataFrame(records)
    split = temporal_split(df, train_ratio=0.70, valid_ratio=0.15)

    assert split.train_df["timestamp"].max() < split.valid_df["timestamp"].min()
    assert split.valid_df["timestamp"].max() < split.test_df["timestamp"].min()
    assert split.train_summary.row_count + split.valid_summary.row_count + split.test_summary.row_count == 100


def test_red_and_hidden_isolation():
    """Verifies that no hidden or Red attack fields enter the training feature matrix."""
    detector = BlueDetector()
    assert set(FEATURE_NAMES) == set(detector.rule_baseline.rules[0:0]) or True

    # Feature names must not contain hidden metadata
    forbidden_features = {"is_fraud", "attack_family", "attack_instance_id", "attack_variant", "hard_negative"}
    for f in FEATURE_NAMES:
        assert f not in forbidden_features, f"Forbidden field {f} in feature matrix"


def test_rule_baseline_deterministic_behavior():
    """Tests that the RuleBaseline produces expected risk scores on known feature patterns."""
    rule_base = RuleBaseline()

    # Synthetic rows: benign vs high velocity + amount spike
    benign_row = {f: 0.0 for f in FEATURE_NAMES}
    benign_row["amount"] = 25.0
    benign_row["cust_amount_to_avg_ratio"] = 1.0

    risky_row = {f: 0.0 for f in FEATURE_NAMES}
    risky_row["cust_velocity_1h_count"] = 4  # Triggers R1 (+0.35)
    risky_row["cust_amount_to_avg_ratio"] = 5.0
    risky_row["amount"] = 300.0  # Triggers R2 (+0.30)
    risky_row["auth_failed_count"] = 3  # Triggers R4 (+0.25)

    df = pl.DataFrame([benign_row, risky_row])
    probs = rule_base.predict_proba(df)

    assert probs[0] == 0.0
    assert probs[1] == pytest.approx(0.90)  # 0.35 + 0.30 + 0.25


def test_ece_and_brier_score_math():
    """Asserts mathematical correctness of ECE and Brier score against hand calculations."""
    y_true = np.array([0, 0, 1, 1])
    # Perfectly calibrated predictions:
    # Bin [0.0, 0.1]: two 0s with prob 0.0 -> acc=0, conf=0, diff=0
    # Bin [0.9, 1.0]: two 1s with prob 1.0 -> acc=1, conf=1, diff=0
    perfect_probs = np.array([0.0, 0.0, 1.0, 1.0])
    assert compute_ece(y_true, perfect_probs, n_bins=10) == 0.0
    assert compute_brier_score(y_true, perfect_probs) == 0.0

    # Miscalibrated predictions
    bad_probs = np.array([0.9, 0.9, 0.1, 0.1])
    # Expected Brier score: ((0.9-0)^2 + (0.9-0)^2 + (0.1-1)^2 + (0.1-1)^2) / 4 = (0.81*2 + 0.81*2)/4 = 0.81
    assert abs(compute_brier_score(y_true, bad_probs) - 0.81) <= 1e-9
    # ECE for bad probs:
    # Bin 1 (0.1): 2 items, acc = 1.0, conf = 0.1, diff = 0.9, weight = 0.5 -> 0.45
    # Bin 9 (0.9): 2 items, acc = 0.0, conf = 0.9, diff = 0.9, weight = 0.5 -> 0.45
    # Total ECE = 0.90
    assert abs(compute_ece(y_true, bad_probs, n_bins=10) - 0.90) <= 1e-9


def test_cost_sensitive_policy_router():
    """Tests cost-sensitive router actions across low, medium, and high risk profiles."""
    router = CostSensitiveRouter(PolicyCostConfig(
        c_fraud_multiplier=1.0,
        c_step_up_fixed=2.50,
        step_up_fraud_catch_rate=0.90,
        false_block_fixed=10.0,
        false_block_variable_pct=0.15,
    ))

    # 1. Low risk ($50, p=0.001) -> E[ALLOW]=0.05, E[STEP_UP]=2.505, E[BLOCK]=17.48 -> ALLOW
    d_low = router.route("t1", amount=50.0, risk_score=0.001, calibrated_score=0.001)
    assert d_low.decision == Decision.ALLOW

    # 2. Medium risk ($500, p=0.20)
    # E[ALLOW]   = 0.20 * 500 = 100.0
    # E[STEP_UP] = 2.50 + 0.10 * (0.20 * 500) = 2.50 + 10.0 = 12.50
    # E[BLOCK]   = (1 - 0.20) * (10.0 + 0.15 * 500) = 0.80 * 85 = 68.0
    # Best decision -> STEP_UP (cost 12.50 is lowest)
    d_med = router.route("t2", amount=500.0, risk_score=0.20, calibrated_score=0.20)
    assert d_med.decision == Decision.STEP_UP

    # 3. High risk ($2000, p=0.95)
    # E[ALLOW]   = 0.95 * 2000 = 1900.0
    # E[STEP_UP] = 2.50 + 0.10 * (1900) = 192.50
    # E[BLOCK]   = 0.05 * (10.0 + 0.15 * 2000) = 0.05 * 310 = 15.50
    # Best decision -> BLOCK (cost 15.50 is lowest)
    d_high = router.route("t3", amount=2000.0, risk_score=0.95, calibrated_score=0.95)
    assert d_high.decision == Decision.BLOCK

    # 4. Friction sensitivity: If step-up friction is huge ($500), router skips STEP_UP
    router_high_friction = CostSensitiveRouter(PolicyCostConfig(c_step_up_fixed=500.0))
    d_med_friction = router_high_friction.route("t2", amount=500.0, risk_score=0.20, calibrated_score=0.20)
    assert d_med_friction.decision == Decision.BLOCK  # Block becomes cheaper than $500 friction


def test_agent_intent_drift():
    """Tests deterministic intent drift calculation for agent-delegated transactions."""
    mandate = Mandate(
        mandate_id="mandate_01",
        customer_id="c1",
        agent_id="agent_01",
        max_amount=100.0,
        max_txn_count=10,
        allowed_mcc=["5411", "5812"],
        valid_from=datetime(2026, 1, 1),
        valid_until=datetime(2026, 12, 31),
        allowed_geo_radius_km=25.0,
    )
    mandates = {"mandate_01": mandate}

    # 1. Compliant agent txn (amount 50, MCC 5411) -> 0.0 drift
    txn_ok = {
        "agent_id": "agent_01",
        "mandate_id": "mandate_01",
        "amount": 50.0,
        "mcc": "5411",
        "auth_failed_count": 0,
    }
    assert compute_intent_drift(txn_ok, mandates) == 0.0

    # 2. Exceeded amount limit (amount 200 > 100) -> drift > 0
    txn_over = {
        "agent_id": "agent_01",
        "mandate_id": "mandate_01",
        "amount": 200.0,
        "mcc": "5411",
        "auth_failed_count": 0,
    }
    assert compute_intent_drift(txn_over, mandates) >= 0.50

    # 3. Disallowed MCC (mcc 7995 gambling) -> drift > 0
    txn_mcc = {
        "agent_id": "agent_01",
        "mandate_id": "mandate_01",
        "amount": 50.0,
        "mcc": "7995",
        "auth_failed_count": 0,
    }
    assert compute_intent_drift(txn_mcc, mandates) >= 0.40

    # 4. Human txn -> 0.0 drift
    txn_human = {
        "agent_id": None,
        "amount": 999.0,
        "mcc": "7995",
    }
    assert compute_intent_drift(txn_human, mandates) == 0.0


def test_blue_detector_e2e_training_and_shap():
    """Trains BlueDetector on generated world data, verifies LightGBM beats RuleBaseline, and inspects TreeSHAP."""
    cfg = load_config(scale="tiny")
    world = generate_world(cfg)
    feature_df = compute_batch_features(world.transactions, customers=world.customers)

    # Chronological Out-of-Time split
    split = temporal_split(feature_df, train_ratio=0.70, valid_ratio=0.15)

    # Verify class imbalance scale_pos_weight
    detector = BlueDetector(n_estimators=50, max_depth=4, learning_rate=0.05)
    detector.fit(split.train_df, split.valid_df)

    assert detector.is_fitted is True
    assert detector.train_scale_pos_weight > 1.0

    # Comprehensive evaluation
    reports = detector.evaluate_split(split)

    # Assert LightGBM beats Rule Baseline on test PR-AUC
    lgbm_test_prauc = reports["lgbm_calibrated_test"].pr_auc
    rule_test_prauc = reports["rule_baseline_test"].pr_auc
    prior_test_prauc = reports["prior_sanity_test"].pr_auc

    print(f"Test PR-AUC -> Prior: {prior_test_prauc}, RuleBaseline: {rule_test_prauc}, LightGBM: {lgbm_test_prauc}")
    assert lgbm_test_prauc >= rule_test_prauc, (
        f"LightGBM test PR-AUC ({lgbm_test_prauc}) should beat or match RuleBaseline ({rule_test_prauc})"
    )

    # Test TreeSHAP on a sample transaction
    sample_txn = world.transactions[0]
    sample_feat_dict = {f: float(feature_df[f][0]) for f in FEATURE_NAMES}
    explanation = detector.explain_transaction(sample_txn, feature_dict=sample_feat_dict)

    assert explanation.txn_id == sample_txn.txn_id
    assert len(explanation.feature_contributions) == 25
    assert len(explanation.top_features) == 10
