"""Blue Team Champion Detector — LightGBM Classifier with Isotonic Calibration.

Trains strictly on out-of-time train split with scale_pos_weight imbalance handling.
Calibrates strictly on out-of-time validation split. Evaluates on held-out test split.
"""

from __future__ import annotations

import time
from typing import Any
import lightgbm as lgb
import numpy as np
import polars as pl

from mcdl.blue.calibration import IsotonicCalibrator
from mcdl.blue.explainer import TreeSHAPExplainer
from mcdl.blue.intent import compute_intent_drift
from mcdl.blue.metrics import ModelEvaluationReport, evaluate_predictions
from mcdl.blue.policy import CostSensitiveRouter, PolicyCostConfig
from mcdl.blue.rule_baseline import RuleBaseline
from mcdl.blue.split import TemporalSplit
from mcdl.features.spec import FEATURE_NAMES
from mcdl.schemas import BlueDecision, Mandate, SHAPExplanation, Transaction


class BlueDetector:
    """Master Blue Team detector encapsulating training, calibration, routing, and explanations."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 5,
        learning_rate: float = 0.05,
        random_state: int = 20260827,
        cost_config: PolicyCostConfig | None = None,
    ) -> None:
        self.params = {
            "objective": "binary",
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "random_state": random_state,
            "n_jobs": -1,
            "verbosity": -1,
        }
        self.model: lgb.LGBMClassifier | None = None
        self.calibrator = IsotonicCalibrator()
        self.router = CostSensitiveRouter(cost_config=cost_config)
        self.explainer: TreeSHAPExplainer | None = None
        self.rule_baseline = RuleBaseline()
        self.train_scale_pos_weight: float = 1.0
        self.is_fitted: bool = False

    def fit(self, train_df: pl.DataFrame, valid_df: pl.DataFrame) -> BlueDetector:
        """Trains LightGBM on train_df and fits IsotonicCalibrator on valid_df."""
        # 1. Prepare training matrix
        x_train = train_df.select(FEATURE_NAMES).to_numpy()
        y_train = train_df["is_fraud"].to_numpy().astype(np.int64)

        pos_count = int(np.sum(y_train))
        neg_count = len(y_train) - pos_count
        if pos_count == 0:
            raise ValueError("Training split contains zero fraud examples")

        # Class imbalance weighting calculated strictly from train split
        self.train_scale_pos_weight = float(neg_count / pos_count)

        self.model = lgb.LGBMClassifier(
            scale_pos_weight=self.train_scale_pos_weight,
            **self.params,
        )
        self.model.fit(x_train, y_train)

        # 2. Fit IsotonicCalibrator on validation set predictions
        x_valid = valid_df.select(FEATURE_NAMES).to_numpy()
        y_valid = valid_df["is_fraud"].to_numpy().astype(np.int64)

        raw_valid_probs = self.model.predict_proba(x_valid)[:, 1]
        self.calibrator.fit(raw_valid_probs, y_valid)

        # 3. Initialize TreeSHAP explainer on trained booster
        self.explainer = TreeSHAPExplainer(self.model.booster_, feature_names=FEATURE_NAMES)
        self.is_fitted = True

        return self

    def predict_raw_proba(self, df: pl.DataFrame) -> np.ndarray:
        """Predicts uncalibrated model probabilities."""
        if not self.is_fitted or self.model is None:
            raise RuntimeError("BlueDetector must be fitted before making predictions")
        x_mat = df.select(FEATURE_NAMES).to_numpy()
        return self.model.predict_proba(x_mat)[:, 1]

    def predict_calibrated_proba(self, df: pl.DataFrame) -> np.ndarray:
        """Predicts isotonic-calibrated probabilities."""
        raw_probs = self.predict_raw_proba(df)
        return self.calibrator.transform(raw_probs)

    def evaluate_split(self, split: TemporalSplit) -> dict[str, ModelEvaluationReport]:
        """Evaluates Prior Sanity, Rule Baseline, and LightGBM across Train, Valid, and Test splits."""
        if not self.is_fitted:
            raise RuntimeError("Fit model before evaluating")

        reports: dict[str, ModelEvaluationReport] = {}

        # 1. Sanity Baseline (Prior probability predicting training base rate)
        train_base_rate = float(split.train_summary.fraud_rate)
        test_y = split.test_df["is_fraud"].to_numpy().astype(np.int64)
        prior_probs = np.full(len(test_y), train_base_rate)
        reports["prior_sanity_test"] = evaluate_predictions(
            test_y, prior_probs, model_name="SanityPrior", dataset_split="test"
        )

        # 2. Rule Baseline
        for name, d_df in [("train", split.train_df), ("valid", split.valid_df), ("test", split.test_df)]:
            rule_probs = self.rule_baseline.predict_proba(d_df)
            y_true = d_df["is_fraud"].to_numpy().astype(np.int64)
            reports[f"rule_baseline_{name}"] = evaluate_predictions(
                y_true, rule_probs, model_name="RuleBaseline", dataset_split=name
            )

        # 3. LightGBM Calibrated Detector
        for name, d_df in [("train", split.train_df), ("valid", split.valid_df), ("test", split.test_df)]:
            cal_probs = self.predict_calibrated_proba(d_df)
            y_true = d_df["is_fraud"].to_numpy().astype(np.int64)
            reports[f"lgbm_calibrated_{name}"] = evaluate_predictions(
                y_true, cal_probs, model_name="LightGBM_Calibrated", dataset_split=name
            )

        return reports

    def score_transaction(
        self,
        txn: Transaction,
        feature_dict: dict[str, Any],
        mandates: dict[str, Mandate] | None = None,
    ) -> BlueDecision:
        """Online single-transaction scoring with policy decision and reason codes."""
        t_start = time.perf_counter()

        feat_vector = np.array([[float(feature_dict[col]) for col in FEATURE_NAMES]], dtype=np.float64)
        raw_score = float(self.model.predict_proba(feat_vector)[0, 1])
        calibrated_score = float(self.calibrator.transform(np.array([raw_score]))[0])

        intent_drift = compute_intent_drift(txn, mandates=mandates) if txn.agent_id else None
        latency_ms = (time.perf_counter() - t_start) * 1000.0

        return self.router.route(
            txn_id=txn.txn_id,
            amount=txn.amount,
            risk_score=raw_score,
            calibrated_score=calibrated_score,
            feature_dict=feature_dict,
            intent_drift_score=intent_drift,
            latency_ms=latency_ms,
        )

    def explain_transaction(
        self,
        txn: Transaction | dict[str, Any],
        feature_dict: dict[str, Any] | None = None,
    ) -> SHAPExplanation:
        """Computes on-demand TreeSHAP explanation for an inspected transaction."""
        if not self.is_fitted or self.explainer is None:
            raise RuntimeError("Model must be fitted before explaining transactions")

        f_dict = feature_dict or (txn if isinstance(txn, dict) else {})
        t_id = txn.txn_id if isinstance(txn, Transaction) else str(txn.get("txn_id", "unknown_txn"))
        return self.explainer.explain(f_dict, txn_id=t_id)
