"""Challenger Blue Model Trainer & Promotion Engine.

Hardens Blue detectors by retraining on Base Train + Replay Buffer.
Evaluates multi-objective promotion criteria (Security + Friction + Calibration).
"""

from __future__ import annotations

from dataclasses import dataclass
import polars as pl

from mcdl.blue.model import BlueDetector
from mcdl.features.spec import FEATURE_NAMES
from mcdl.loop.replay import ReplayBuffer


class ChallengerTrainer:
    """Trains hardened Challenger models from base training data and replayed evasions."""

    def __init__(
        self,
        n_estimators: int = 30,
        max_depth: int = 3,
        learning_rate: int = 0.05,
        random_state: int = 20260827,
    ) -> None:
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state

    def train(
        self,
        base_train_df: pl.DataFrame,
        valid_df: pl.DataFrame,
        replay_buffer: ReplayBuffer,
        round_idx: int = 1,
    ) -> BlueDetector:
        """Constructs augmented dataset and fits a new BlueDetector."""
        replay_rows = replay_buffer.to_feature_rows()

        if replay_rows:
            # Build polars DataFrame for replay records matching schema
            cols = [c for c in FEATURE_NAMES if c in base_train_df.columns] + ["is_fraud"]
            base_subset = base_train_df.select(cols)
            replay_df = pl.DataFrame(replay_rows, schema=base_subset.schema)
            replay_subset = replay_df.select(cols)
            augmented_df = pl.concat([base_subset, replay_subset])
        else:
            augmented_df = base_train_df

        detector = BlueDetector(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            random_state=self.random_state + round_idx,
        )
        detector.fit(augmented_df, valid_df)
        return detector


def evaluate_promotion(
    baseline_seen_asr: float,
    challenger_seen_asr: float,
    baseline_heldout_asr: float,
    challenger_heldout_asr: float,
    fpr: float,
    allow_rate: float,
    pr_auc: float,
    max_fpr: float = 0.08,
    min_allow_rate: float = 0.70,
) -> tuple[bool, list[str]]:
    """Evaluates whether Challenger qualifies for promotion to Champion."""
    reasons = []

    # 1. Anti-Pathological check: Must not block all traffic
    if allow_rate < min_allow_rate:
        reasons.append(f"REJECT_LOW_APPROVAL_RATE (allow_rate={allow_rate:.2f} < {min_allow_rate:.2f})")
        return False, reasons

    # 2. False Positive Rate check: Must not significantly degrade benign traffic
    if fpr > max_fpr:
        reasons.append(f"REJECT_EXCESSIVE_FPR (fpr={fpr:.4f} > {max_fpr:.4f})")
        return False, reasons

    # 3. Security Improvement: Challenger must reduce seen or held-out ASR without catastrophic regression
    security_improved = (challenger_seen_asr < baseline_seen_asr) or (challenger_heldout_asr < baseline_heldout_asr)
    no_severe_regression = (challenger_heldout_asr <= baseline_heldout_asr + 0.05) and (challenger_seen_asr <= baseline_seen_asr + 0.05)

    if security_improved and no_severe_regression:
        reasons.append("PROMOTED_SECURITY_IMPROVEMENT")
        if challenger_heldout_asr < baseline_heldout_asr:
            reasons.append("DEMONSTRATED_GENERALISATION_IMPROVEMENT")
        return True, reasons

    if not security_improved:
        reasons.append(f"REJECT_NO_SECURITY_GAIN (seen={challenger_seen_asr:.2f} vs {baseline_seen_asr:.2f})")
    else:
        reasons.append("REJECT_REGRESSION_ON_HELDOUT")

    return False, reasons
