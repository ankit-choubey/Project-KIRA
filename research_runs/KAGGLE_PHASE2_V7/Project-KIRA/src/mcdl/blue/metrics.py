"""Evaluation Metrics for Blue Team Fraud Classifiers.

Computes PR-AUC, ROC-AUC, Brier score, ECE, Precision, Recall, FPR, TPR,
and confusion matrix without information leakage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    roc_auc_score,
)

from mcdl.blue.calibration import compute_brier_score, compute_ece


@dataclass(frozen=True)
class ModelEvaluationReport:
    model_name: str
    dataset_split: str
    sample_count: int
    fraud_count: int
    pr_auc: float
    roc_auc: float
    brier_score: float
    ece: float
    precision: float
    recall: float
    fpr: float
    tpr: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int


def evaluate_predictions(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    model_name: str,
    dataset_split: str,
    threshold: float = 0.50,
) -> ModelEvaluationReport:
    """Computes comprehensive classification, ranking, and calibration metrics."""
    y_t = np.asarray(y_true, dtype=np.int64)
    y_p = np.clip(np.asarray(y_prob, dtype=np.float64), 0.0, 1.0)
    y_pred = (y_p >= threshold).astype(np.int64)

    n = len(y_t)
    fraud_count = int(np.sum(y_t))

    # Handle edge case of single-class labels
    if fraud_count == 0 or fraud_count == n:
        pr_auc = float(fraud_count / n)
        roc_auc = 0.5
    else:
        pr_auc = float(average_precision_score(y_t, y_p))
        roc_auc = float(roc_auc_score(y_t, y_p))

    brier = compute_brier_score(y_t, y_p)
    ece = compute_ece(y_t, y_p, n_bins=10)

    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_t, y_pred, labels=[0, 1]).ravel()

    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    tpr = recall

    return ModelEvaluationReport(
        model_name=model_name,
        dataset_split=dataset_split,
        sample_count=n,
        fraud_count=fraud_count,
        pr_auc=round(pr_auc, 6),
        roc_auc=round(roc_auc, 6),
        brier_score=round(brier, 6),
        ece=round(ece, 6),
        precision=round(precision, 6),
        recall=round(recall, 6),
        fpr=round(fpr, 6),
        tpr=round(tpr, 6),
        true_positives=int(tp),
        false_positives=int(fp),
        true_negatives=int(tn),
        false_negatives=int(fn),
    )
