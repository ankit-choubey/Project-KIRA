"""ADV-003 Evaluation and Metric Aggregation Engine.

Computes attack success rates, family-level performance, calibration,
anti-forgetting deltas, and defense curve metrics across sequential defense rounds.
"""

from __future__ import annotations

from typing import Any
import numpy as np
import polars as pl
from sklearn.metrics import brier_score_loss, precision_recall_curve, roc_auc_score, auc

from mcdl.features.spec import FEATURE_NAMES
from mcdl.research.advanced.adv003.challenger import ChallengerDetector
from mcdl.research.advanced.adv003.schemas import AttackAttemptSummary
from mcdl.schemas import Decision


class ADV003Evaluator:
    """Evaluates detector robustness, ASR, and discrimination across attack populations."""

    @staticmethod
    def evaluate_attack_population(
        detector: ChallengerDetector,
        attacks: list[dict[str, Any]],
    ) -> AttackAttemptSummary:
        """Evaluates a set of attack dictionaries against a detector and summarizes outcomes."""
        if not attacks:
            return AttackAttemptSummary()

        total = len(attacks)
        allowed = 0
        blocked = 0
        step_up = 0
        family_counts: dict[str, int] = {}
        family_evasions: dict[str, int] = {}
        budget_counts: dict[str, int] = {}
        budget_evasions: dict[str, int] = {}
        queries_list: list[int] = []
        med_list: list[float] = []

        for atk in attacks:
            feats = atk["features"]
            amt = atk["amount"]
            dec = detector.score_features(feats, amount=amt)

            fam = atk.get("family", "unknown")
            family_counts[fam] = family_counts.get(fam, 0) + 1

            b_key = str(atk.get("queries_used", 20))
            budget_counts[b_key] = budget_counts.get(b_key, 0) + 1

            queries_list.append(atk.get("queries_used", 1))

            if dec.decision == Decision.ALLOW:
                allowed += 1
                family_evasions[fam] = family_evasions.get(fam, 0) + 1
                budget_evasions[b_key] = budget_evasions.get(b_key, 0) + 1
                dist = atk.get("perturbation_distance", 0.0)
                if dist > 0:
                    med_list.append(dist)
            elif dec.decision == Decision.STEP_UP:
                step_up += 1
            else:
                blocked += 1

        asr = round(allowed / max(1, total), 4)

        family_asr = {
            fam: round(family_evasions.get(fam, 0) / max(1, cnt), 4)
            for fam, cnt in family_counts.items()
        }

        budget_asr = {
            b: round(budget_evasions.get(b, 0) / max(1, cnt), 4)
            for b, cnt in budget_counts.items()
        }

        median_q = float(np.median(queries_list)) if queries_list else None
        median_m = float(np.median(med_list)) if med_list else None

        return AttackAttemptSummary(
            total_attempts=total,
            valid_attempts=total,
            allowed_evasion=allowed,
            blocked=blocked,
            step_up=step_up,
            errors=0,
            timeouts=0,
            aggregate_asr=asr,
            family_asr=family_asr,
            query_budget_asr=budget_asr,
            median_queries=median_q,
            median_med=median_m,
        )

    @staticmethod
    def compute_calibration_and_discrimination(
        detector: ChallengerDetector,
        evaluation_df: pl.DataFrame,
    ) -> dict[str, float | None]:
        """Computes PR-AUC, ROC-AUC, Brier score, and expected calibration error."""
        if len(evaluation_df) == 0 or "is_fraud" not in evaluation_df.columns:
            return {"pr_auc": None, "roc_auc": None, "brier_score": None, "ece": None}

        x_eval = evaluation_df.select(FEATURE_NAMES).to_numpy()
        y_eval = evaluation_df["is_fraud"].to_numpy().astype(np.int64)

        probs = np.array([
            detector.score_features({f: row[i] for i, f in enumerate(FEATURE_NAMES)}).calibrated_score
            for row in x_eval
        ], dtype=np.float64)

        n_pos = int(np.sum(y_eval == 1))
        n_neg = int(np.sum(y_eval == 0))

        pr_auc_val = None
        roc_auc_val = None
        if n_pos > 0 and n_neg > 0:
            prec, rec, _ = precision_recall_curve(y_eval, probs)
            pr_auc_val = round(float(auc(rec, prec)), 4)
            roc_auc_val = round(float(roc_auc_score(y_eval, probs)), 4)

        brier_val = round(float(brier_score_loss(y_eval, probs)), 4)

        # Compute simple 10-bin ECE
        bins = np.linspace(0.0, 1.0, 11)
        bin_indices = np.digitize(probs, bins) - 1
        bin_indices = np.clip(bin_indices, 0, 9)
        ece_sum = 0.0
        n_total = len(y_eval)

        for b in range(10):
            mask = (bin_indices == b)
            if np.any(mask):
                bin_acc = float(np.mean(y_eval[mask]))
                bin_conf = float(np.mean(probs[mask]))
                ece_sum += (np.sum(mask) / n_total) * abs(bin_acc - bin_conf)

        ece_val = round(float(ece_sum), 4)

        return {
            "pr_auc": pr_auc_val,
            "roc_auc": roc_auc_val,
            "brier_score": brier_val,
            "ece": ece_val,
        }
