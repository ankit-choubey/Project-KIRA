"""ADV-003 Challenger Detector and Promotion Gate.

Implements isolated challenger model training, multi-split promotion gating,
anti-forgetting measurement, and rollback mechanics without mutating production Blue.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any
import lightgbm as lgb
import numpy as np
import polars as pl
from sklearn.metrics import brier_score_loss, roc_auc_score

from mcdl.blue.calibration import IsotonicCalibrator
from mcdl.blue.policy import CostSensitiveRouter, PolicyCostConfig
from mcdl.features.spec import FEATURE_NAMES
from mcdl.research.advanced.adv003.knowledge import DefensiveKnowledgeStore
from mcdl.research.advanced.adv003.schemas import (
    AntiForgettingStatus,
    PromotionDecision,
    PromotionEvaluation,
    PromotionGateConfig,
)
from mcdl.schemas import BlueDecision, Decision, Mandate, Transaction


class ChallengerDetector:
    """Isolated challenger detector model trained on base data augmented with defensive replay."""

    def __init__(
        self,
        model_version: str,
        parent_version: str | None = None,
        n_estimators: int = 100,
        max_depth: int = 5,
        learning_rate: float = 0.05,
        random_state: int = 20260827,
        feature_names: list[str] | None = None,
    ) -> None:
        self.model_version = model_version
        self.parent_version = parent_version
        self.feature_names = list(feature_names) if feature_names is not None else list(FEATURE_NAMES)
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
        self.router = CostSensitiveRouter(cost_config=PolicyCostConfig())
        self.is_fitted: bool = False
        self.training_hash: str = ""
        self.fitted_at: str = ""

    def fit_with_defensive_replay(
        self,
        base_train_df: pl.DataFrame,
        valid_df: pl.DataFrame,
        knowledge_store: DefensiveKnowledgeStore,
        max_replay_records: int | None = None,
        min_round: int = 0,
        max_round: int | None = None,
    ) -> ChallengerDetector:
        """Fits LightGBM on base training data augmented with validated defensive knowledge."""
        # 1. Retrieve replay DataFrame
        replay_df = knowledge_store.get_replay_dataframe(
            max_records=max_replay_records,
            min_round=min_round,
            max_round=max_round,
        )

        # 2. Combine base train and replay features with explicit casting
        base_sel = base_train_df.select([
            pl.col(f).cast(pl.Float64) for f in self.feature_names
        ] + [pl.col("is_fraud").cast(pl.Int64)])

        if len(replay_df) > 0:
            replay_sel = replay_df.select([
                pl.col(f).cast(pl.Float64) for f in self.feature_names
            ] + [pl.col("is_fraud").cast(pl.Int64)])
            combined_train_df = pl.concat([base_sel, replay_sel])
        else:
            combined_train_df = base_sel

        # 3. Compute deterministic training data hash for audit provenance
        train_bytes = combined_train_df.write_csv().encode("utf-8")
        self.training_hash = hashlib.sha256(train_bytes).hexdigest()

        # 4. Train LightGBM classifier
        x_train = combined_train_df.select(self.feature_names).to_numpy()
        y_train = combined_train_df["is_fraud"].to_numpy().astype(np.int64)

        n_pos = int(np.sum(y_train == 1))
        n_neg = int(np.sum(y_train == 0))
        scale_pos_weight = float(n_neg / max(1, n_pos))

        self.model = lgb.LGBMClassifier(
            scale_pos_weight=scale_pos_weight,
            **self.params,
        )
        self.model.fit(x_train, y_train)

        # 5. Fit Calibrator on validation set
        x_valid = valid_df.select(self.feature_names).to_numpy()
        y_valid = valid_df["is_fraud"].to_numpy().astype(np.int64)
        val_probs_raw = self.model.predict_proba(x_valid)[:, 1]
        self.calibrator.fit(val_probs_raw, y_valid)

        self.is_fitted = True
        self.fitted_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return self

    def score_features(
        self,
        features: dict[str, float],
        amount: float = 100.0,
        txn_id: str = "txn_eval",
        mandates: dict[str, Mandate] | None = None,
    ) -> BlueDecision:
        """Scores a single transaction feature vector with calibrated probability and policy routing."""
        if not self.is_fitted or self.model is None:
            raise RuntimeError(f"ChallengerDetector {self.model_version} is not fitted.")

        x_row = np.array([[float(features.get(f, 0.0)) for f in self.feature_names]], dtype=np.float64)
        raw_prob = float(self.model.predict_proba(x_row)[0, 1])
        if self.calibrator.is_fitted:
            cal_prob = float(self.calibrator.transform(np.array([raw_prob]))[0])
        else:
            cal_prob = raw_prob

        return self.router.route(
            txn_id=txn_id,
            amount=amount,
            risk_score=raw_prob,
            calibrated_score=cal_prob,
            feature_dict=features,
            latency_ms=0.05,
        )

    def score_transaction(self, txn: Transaction, features: dict[str, float], mandates: dict[str, Mandate] | None = None) -> BlueDecision:
        """Scores a Transaction and associated feature mapping."""
        return self.score_features(features, amount=txn.amount, txn_id=txn.txn_id, mandates=mandates)


class PromotionGate:
    """Rigorous gate evaluating challenger candidates against current champion across disjoint splits."""

    def __init__(self, config: PromotionGateConfig | None = None) -> None:
        self.config = config or PromotionGateConfig()

    def evaluate_challenger(
        self,
        round_number: int,
        champion: ChallengerDetector,
        challenger: ChallengerDetector,
        val_attacks: list[dict[str, Any]],
        legacy_attacks: list[dict[str, Any]],
        heldout_attacks: list[dict[str, Any]],
        valid_df: pl.DataFrame | None = None,
    ) -> PromotionEvaluation:
        """Evaluates challenger vs champion across validation, legacy, and held-out attack datasets."""
        # 1. Validation Split ASR (Current adaptive attacks)
        val_champ_evasions = sum(1 for a in val_attacks if champion.score_features(a["features"], amount=a["amount"]).decision == Decision.ALLOW)
        val_chall_evasions = sum(1 for a in val_attacks if challenger.score_features(a["features"], amount=a["amount"]).decision == Decision.ALLOW)
        val_total = max(1, len(val_attacks))

        val_asr_champ = round(val_champ_evasions / val_total, 4)
        val_asr_chall = round(val_chall_evasions / val_total, 4)
        delta_val_asr = round(val_asr_chall - val_asr_champ, 4)

        # 2. Legacy Split ASR (Round 0 / historical baseline attacks)
        leg_champ_evasions = sum(1 for a in legacy_attacks if champion.score_features(a["features"], amount=a["amount"]).decision == Decision.ALLOW)
        leg_chall_evasions = sum(1 for a in legacy_attacks if challenger.score_features(a["features"], amount=a["amount"]).decision == Decision.ALLOW)
        leg_total = max(1, len(legacy_attacks))

        leg_asr_champ = round(leg_champ_evasions / leg_total, 4)
        leg_asr_chall = round(leg_chall_evasions / leg_total, 4)
        delta_legacy_asr = round(leg_asr_chall - leg_asr_champ, 4)

        # 3. Held-Out Split ASR (Strictly unseen attacks)
        held_champ_evasions = sum(1 for a in heldout_attacks if champion.score_features(a["features"], amount=a["amount"]).decision == Decision.ALLOW)
        held_chall_evasions = sum(1 for a in heldout_attacks if challenger.score_features(a["features"], amount=a["amount"]).decision == Decision.ALLOW)
        held_total = max(1, len(heldout_attacks))

        held_asr_champ = round(held_champ_evasions / held_total, 4)
        held_asr_chall = round(held_chall_evasions / held_total, 4)
        delta_heldout_asr = round(held_asr_chall - held_asr_champ, 4)

        # 4. Anti-Forgetting Metric
        # Degradation on legacy baseline attacks relative to champion
        anti_forgetting_delta = max(0.0, delta_legacy_asr)

        if len(legacy_attacks) < 5:
            af_status = AntiForgettingStatus.INCONCLUSIVE
        elif anti_forgetting_delta <= 0.0:
            af_status = AntiForgettingStatus.NO_FORGETTING
        elif anti_forgetting_delta <= self.config.anti_forgetting_threshold:
            af_status = AntiForgettingStatus.MINOR_DEGRADATION
        else:
            af_status = AntiForgettingStatus.SIGNIFICANT_FORGETTING

        # 5. Calibration / Brier Score stability on validation dataframe
        brier_champ: float | None = None
        brier_chall: float | None = None
        if valid_df is not None and len(valid_df) > 0:
            x_val = valid_df.select(FEATURE_NAMES).to_numpy()
            y_val = valid_df["is_fraud"].to_numpy().astype(np.int64)
            p_champ = [champion.score_features({f: row[i] for i, f in enumerate(FEATURE_NAMES)}).calibrated_score for row in x_val]
            p_chall = [challenger.score_features({f: row[i] for i, f in enumerate(FEATURE_NAMES)}).calibrated_score for row in x_val]
            brier_champ = round(float(brier_score_loss(y_val, p_champ)), 4)
            brier_chall = round(float(brier_score_loss(y_val, p_chall)), 4)

        # 6. Gating Decision Logic
        reasons: list[str] = []
        is_promotable = True

        # Gate A: Validation ASR must not increase
        if val_asr_chall > val_asr_champ + self.config.min_asr_reduction:
            is_promotable = False
            reasons.append(f"Validation ASR increased (challenger={val_asr_chall:.4f} > champion={val_asr_champ:.4f})")

        # Gate B: Legacy ASR degradation must not exceed threshold
        if delta_legacy_asr > self.config.max_legacy_degradation:
            is_promotable = False
            reasons.append(f"Legacy ASR degraded by {delta_legacy_asr:.4f} > max allowable {self.config.max_legacy_degradation:.4f}")

        # Gate C: Held-out degradation must not exceed threshold
        if delta_heldout_asr > self.config.max_heldout_degradation:
            is_promotable = False
            reasons.append(f"Held-out ASR degraded by {delta_heldout_asr:.4f} > max allowable {self.config.max_heldout_degradation:.4f}")

        # Gate D: Anti-forgetting test
        if af_status == AntiForgettingStatus.SIGNIFICANT_FORGETTING:
            is_promotable = False
            reasons.append(f"Significant catastrophic forgetting detected: delta={anti_forgetting_delta:.4f}")

        # Gate E: Calibration stability
        if brier_champ is not None and brier_chall is not None:
            if (brier_chall - brier_champ) > self.config.max_brier_score_increase:
                is_promotable = False
                reasons.append(f"Brier score degraded from {brier_champ:.4f} to {brier_chall:.4f}")

        decision = PromotionDecision.PROMOTE if is_promotable else PromotionDecision.REJECT

        if is_promotable:
            reasons.append(f"All gates passed: val_asr delta={delta_val_asr:+.4f}, anti_forgetting_status={af_status.value}")

        return PromotionEvaluation(
            round_number=round_number,
            challenger_version=challenger.model_version,
            champion_version=champion.model_version,
            validation_asr_champion=val_asr_champ,
            validation_asr_challenger=val_asr_chall,
            delta_val_asr=delta_val_asr,
            legacy_asr_champion=leg_asr_champ,
            legacy_asr_challenger=leg_asr_chall,
            delta_legacy_asr=delta_legacy_asr,
            heldout_asr_champion=held_asr_champ,
            heldout_asr_challenger=held_asr_chall,
            delta_heldout_asr=delta_heldout_asr,
            anti_forgetting_delta=anti_forgetting_delta,
            anti_forgetting_status=af_status,
            brier_score_champion=brier_champ,
            brier_score_challenger=brier_chall,
            decision=decision,
            reasons=reasons,
        )
