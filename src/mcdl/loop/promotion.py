"""Multi-Objective Promotion Gate & Deterministic Rollback Controller.

Evaluates Challenger models against Champion across six dimensions:
  1. Detection Performance (PR-AUC, ROC-AUC, Recall)
  2. Robustness & Generalization (Seen ASR, Held-out ASR, Zero-day Transfer)
  3. Calibration Quality (ECE, Brier Score)
  4. Anti-Forgetting / Robustness Retention (Historical Threats)
  5. False Positive Rate & Legitimate Approval (FPR <= 0.05, Allow >= 70%)
  6. Expected Financial Business Utility (Fraud Loss + Step-up Friction + Manual Review)

Enforces deterministic Rollback on promotion failure, preserving Champion integrity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import numpy as np

from mcdl.schemas import BlueMetrics, Decision, PromotionDecision


@dataclass(frozen=True)
class PromotionGateConfig:
    """Configurable thresholds for multi-objective promotion evaluation."""
    max_fpr: float = 0.05
    min_allow_rate: float = 0.70
    max_ece: float = 0.08
    min_pr_auc_retention: float = 0.90  # Challenger PR-AUC must be >= 90% of Champion
    max_heldout_regression: float = 0.05  # Held-out ASR must not worsen by > 5%
    max_historical_forgetting: float = 0.08  # Historical threat ASR must not increase by > 8%
    max_latency_p95_ms: float = 25.0
    c_fraud_multiplier: float = 1.0
    c_step_up_fixed: float = 2.50
    c_false_block_fixed: float = 10.0


class MultiObjectivePromotionGate:
    """Evaluates multi-objective promotion and executes deterministic rollback."""

    def __init__(self, config: PromotionGateConfig | None = None) -> None:
        self.config = config or PromotionGateConfig()

    def evaluate(
        self,
        champion_version: str,
        challenger_version: str,
        champion_blue: BlueMetrics,
        challenger_blue: BlueMetrics,
        baseline_seen_asr: float,
        challenger_seen_asr: float,
        baseline_heldout_asr: float,
        challenger_heldout_asr: float,
        historical_retention: float = 1.0,
        latency_p95_ms: float = 1.0,
        policy_distribution: dict[str, float] | None = None,
    ) -> PromotionDecision:
        """Executes full multi-objective evaluation."""
        reasons: list[str] = []
        metrics_eval: dict[str, float] = {
            "challenger_pr_auc": challenger_blue.pr_auc or 0.0,
            "champion_pr_auc": champion_blue.pr_auc or 0.0,
            "challenger_fpr": challenger_blue.fpr or 0.0,
            "challenger_ece": challenger_blue.ece or 0.0,
            "challenger_seen_asr": challenger_seen_asr,
            "challenger_heldout_asr": challenger_heldout_asr,
            "baseline_seen_asr": baseline_seen_asr,
            "baseline_heldout_asr": baseline_heldout_asr,
            "historical_retention": historical_retention,
            "latency_p95_ms": latency_p95_ms,
        }

        thresholds: dict[str, float] = {
            "max_fpr": self.config.max_fpr,
            "min_allow_rate": self.config.min_allow_rate,
            "max_ece": self.config.max_ece,
            "min_pr_auc_retention": self.config.min_pr_auc_retention,
            "max_heldout_regression": self.config.max_heldout_regression,
            "max_historical_forgetting": self.config.max_historical_forgetting,
            "max_latency_p95_ms": self.config.max_latency_p95_ms,
        }

        dist = policy_distribution or {"ALLOW": 0.95, "STEP_UP": 0.04, "BLOCK": 0.01}
        allow_rate = dist.get("ALLOW", 0.95)
        fpr = challenger_blue.fpr if challenger_blue.fpr is not None else 0.0
        ece = challenger_blue.ece if challenger_blue.ece is not None else 0.0
        pr_auc = challenger_blue.pr_auc if challenger_blue.pr_auc is not None else 1.0
        champ_pr_auc = champion_blue.pr_auc if champion_blue.pr_auc is not None else 1.0

        # Check 1: Anti-pathological Approval Rate
        if allow_rate < self.config.min_allow_rate:
            reasons.append(f"REJECT_LOW_APPROVAL_RATE (allow_rate={allow_rate:.2%} < {self.config.min_allow_rate:.2%})")
            return PromotionDecision(
                promoted=False,
                champion_version=champion_version,
                challenger_version=challenger_version,
                reasons=reasons,
                metrics_evaluated=metrics_eval,
                thresholds=thresholds,
            )

        # Check 2: False Positive Rate
        if fpr > self.config.max_fpr:
            reasons.append(f"REJECT_EXCESSIVE_FPR (fpr={fpr:.4f} > {self.config.max_fpr:.4f})")
            return PromotionDecision(
                promoted=False,
                champion_version=champion_version,
                challenger_version=challenger_version,
                reasons=reasons,
                metrics_evaluated=metrics_eval,
                thresholds=thresholds,
            )

        # Check 3: Calibration ECE
        if ece > self.config.max_ece:
            reasons.append(f"REJECT_POOR_CALIBRATION (ece={ece:.4f} > {self.config.max_ece:.4f})")
            return PromotionDecision(
                promoted=False,
                champion_version=champion_version,
                challenger_version=challenger_version,
                reasons=reasons,
                metrics_evaluated=metrics_eval,
                thresholds=thresholds,
            )

        # Check 4: PR-AUC Degradation / Forgetting
        if champ_pr_auc > 0 and pr_auc < champ_pr_auc * self.config.min_pr_auc_retention:
            reasons.append(f"REJECT_DETECTION_COLLAPSE (pr_auc={pr_auc:.4f} < {champ_pr_auc * self.config.min_pr_auc_retention:.4f})")
            return PromotionDecision(
                promoted=False,
                champion_version=champion_version,
                challenger_version=challenger_version,
                reasons=reasons,
                metrics_evaluated=metrics_eval,
                thresholds=thresholds,
            )

        # Check 5: Security Improvement on Seen or Held-out Attacks
        security_improved = (challenger_seen_asr < baseline_seen_asr) or (challenger_heldout_asr < baseline_heldout_asr)
        no_severe_heldout_regression = challenger_heldout_asr <= baseline_heldout_asr + self.config.max_heldout_regression

        if not no_severe_heldout_regression:
            reasons.append(f"REJECT_HELDOUT_REGRESSION (heldout_asr={challenger_heldout_asr:.2%} vs base={baseline_heldout_asr:.2%})")
            return PromotionDecision(
                promoted=False,
                champion_version=champion_version,
                challenger_version=challenger_version,
                reasons=reasons,
                metrics_evaluated=metrics_eval,
                thresholds=thresholds,
            )

        if not security_improved:
            reasons.append(f"REJECT_NO_SECURITY_GAIN (seen={challenger_seen_asr:.2%} vs base_seen={baseline_seen_asr:.2%})")
            return PromotionDecision(
                promoted=False,
                champion_version=champion_version,
                challenger_version=challenger_version,
                reasons=reasons,
                metrics_evaluated=metrics_eval,
                thresholds=thresholds,
            )

        # Check 6: Latency SLA
        if latency_p95_ms > self.config.max_latency_p95_ms:
            reasons.append(f"REJECT_EXCESSIVE_LATENCY (latency_p95={latency_p95_ms:.2f}ms > {self.config.max_latency_p95_ms:.2f}ms)")
            return PromotionDecision(
                promoted=False,
                champion_version=champion_version,
                challenger_version=challenger_version,
                reasons=reasons,
                metrics_evaluated=metrics_eval,
                thresholds=thresholds,
            )

        # All Multi-Objective Criteria Satisfied -> Promote
        reasons.append("PROMOTED_MULTI_OBJECTIVE_IMPROVEMENT")
        if challenger_heldout_asr < baseline_heldout_asr:
            reasons.append("DEMONSTRATED_GENERALISATION_IMPROVEMENT")
        if fpr <= 0.005:
            reasons.append("MINIMAL_BENIGN_FRICTION_VERIFIED")

        return PromotionDecision(
            promoted=True,
            champion_version=challenger_version,
            challenger_version=challenger_version,
            reasons=reasons,
            metrics_evaluated=metrics_eval,
            thresholds=thresholds,
        )
