"""Train-on-Synthetic, Test-on-Real (TSTR) Evaluation.

Evaluates detector transferability by training a detector on KIRA synthetic data
and evaluating on a permitted real-world dataset (REAL_WORLD namespace).
Compares with Train-on-Real, Test-on-Real (TRTR) baseline where feasible.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


def _compute_calibration_metrics(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> tuple[float, float]:
    """Computes Expected Calibration Error (ECE) and Brier Score."""
    brier = float(brier_score_loss(y_true, y_prob))
    
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total_samples = len(y_true)
    
    for i in range(n_bins):
        bin_lower, bin_upper = bin_boundaries[i], bin_boundaries[i + 1]
        mask = (y_prob >= bin_lower) & (y_prob < bin_upper) if i < n_bins - 1 else (y_prob >= bin_lower) & (y_prob <= bin_upper)
        bin_count = np.sum(mask)
        if bin_count > 0:
            bin_acc = np.mean(y_true[mask])
            bin_conf = np.mean(y_prob[mask])
            ece += (bin_count / total_samples) * abs(bin_acc - bin_conf)
            
    return round(float(ece), 6), round(brier, 6)


def evaluate_tstr_transfer(
    synthetic_train_X: np.ndarray,
    synthetic_train_y: np.ndarray,
    real_test_X: np.ndarray,
    real_test_y: np.ndarray,
    real_train_X: Optional[np.ndarray] = None,
    real_train_y: Optional[np.ndarray] = None,
    seed: int = 20260827,
) -> dict[str, Any]:
    """Evaluates TSTR (and optionally TRTR) transfer performance."""
    try:
        import lightgbm as lgb
        
        # 1. Train on Synthetic
        syn_model = lgb.LGBMClassifier(
            n_estimators=50,
            max_depth=4,
            learning_rate=0.05,
            random_state=seed,
            verbosity=-1,
        )
        syn_model.fit(synthetic_train_X, synthetic_train_y)
        tstr_probs = syn_model.predict_proba(real_test_X)[:, 1]
        
        tstr_pr_auc = float(average_precision_score(real_test_y, tstr_probs))
        tstr_roc_auc = float(roc_auc_score(real_test_y, tstr_probs))
        tstr_ece, tstr_brier = _compute_calibration_metrics(real_test_y, tstr_probs)
        
        tstr_metrics = {
            "pr_auc": round(tstr_pr_auc, 4),
            "roc_auc": round(tstr_roc_auc, 4),
            "ece": tstr_ece,
            "brier": tstr_brier,
            "n_train_synthetic": len(synthetic_train_y),
            "n_test_real": len(real_test_y),
            "n_test_real_fraud": int(np.sum(real_test_y)),
        }
    except Exception as e:
        return {
            "status": "FAILED",
            "error": str(e),
            "tstr": None,
            "trtr": None,
        }

    # 2. Train on Real (TRTR baseline) if available
    trtr_metrics = None
    if real_train_X is not None and real_train_y is not None and len(real_train_y) > 0:
        try:
            real_model = lgb.LGBMClassifier(
                n_estimators=50,
                max_depth=4,
                learning_rate=0.05,
                random_state=seed,
                verbosity=-1,
            )
            real_model.fit(real_train_X, real_train_y)
            trtr_probs = real_model.predict_proba(real_test_X)[:, 1]
            
            trtr_pr_auc = float(average_precision_score(real_test_y, trtr_probs))
            trtr_roc_auc = float(roc_auc_score(real_test_y, trtr_probs))
            trtr_ece, trtr_brier = _compute_calibration_metrics(real_test_y, trtr_probs)
            
            trtr_metrics = {
                "pr_auc": round(trtr_pr_auc, 4),
                "roc_auc": round(trtr_roc_auc, 4),
                "ece": trtr_ece,
                "brier": trtr_brier,
                "n_train_real": len(real_train_y),
            }
        except Exception:
            trtr_metrics = None

    return {
        "status": "COMPLETE",
        "tstr": tstr_metrics,
        "trtr": trtr_metrics,
        "delta_pr_auc": round(tstr_metrics["pr_auc"] - (trtr_metrics["pr_auc"] if trtr_metrics else 0.0), 4) if trtr_metrics else None,
    }
