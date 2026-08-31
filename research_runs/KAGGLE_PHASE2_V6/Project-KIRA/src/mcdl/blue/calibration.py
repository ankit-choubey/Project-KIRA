"""Probability Calibration & Calibration Error Metrics.

Uses Isotonic Regression fitted exclusively on validation predictions.
Computes Expected Calibration Error (ECE) and Brier Score.
"""

from __future__ import annotations

import numpy as np
from sklearn.isotonic import IsotonicRegression


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Computes Expected Calibration Error (ECE) with uniform confidence binning.

    Formula:
      ECE = sum_{m=1}^M (|B_m| / N) * |acc(B_m) - conf(B_m)|
    where empty bins contribute 0.0.
    """
    n = len(y_true)
    if n == 0:
        return 0.0

    y_true_arr = np.asarray(y_true, dtype=np.float64)
    y_prob_arr = np.clip(np.asarray(y_prob, dtype=np.float64), 0.0, 1.0)

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        lower = bin_boundaries[i]
        upper = bin_boundaries[i + 1]

        if i == 0:
            mask = (y_prob_arr >= lower) & (y_prob_arr <= upper)
        else:
            mask = (y_prob_arr > lower) & (y_prob_arr <= upper)

        bin_count = np.sum(mask)
        if bin_count > 0:
            bin_acc = np.mean(y_true_arr[mask])
            bin_conf = np.mean(y_prob_arr[mask])
            ece += (bin_count / n) * np.abs(bin_acc - bin_conf)

    return float(ece)


def compute_brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Computes Brier Score (Mean Squared Error between probability and binary truth)."""
    n = len(y_true)
    if n == 0:
        return 0.0
    y_true_arr = np.asarray(y_true, dtype=np.float64)
    y_prob_arr = np.clip(np.asarray(y_prob, dtype=np.float64), 0.0, 1.0)
    return float(np.mean((y_prob_arr - y_true_arr) ** 2))


class IsotonicCalibrator:
    """Monotonic non-parametric probability calibrator fitted on validation probabilities."""

    def __init__(self) -> None:
        self.regressor = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        self.is_fitted = False

    def fit(self, raw_probs: np.ndarray, y_true: np.ndarray) -> IsotonicCalibrator:
        """Fits isotonic regression on validation set raw probabilities."""
        p_arr = np.clip(np.asarray(raw_probs, dtype=np.float64), 0.0, 1.0)
        y_arr = np.asarray(y_true, dtype=np.float64)
        self.regressor.fit(p_arr, y_arr)
        self.is_fitted = True
        return self

    def transform(self, raw_probs: np.ndarray) -> np.ndarray:
        """Calibrates raw probabilities using the fitted isotonic mapping."""
        if not self.is_fitted:
            raise RuntimeError("IsotonicCalibrator must be fitted before transforming probabilities")
        p_arr = np.clip(np.asarray(raw_probs, dtype=np.float64), 0.0, 1.0)
        calibrated = self.regressor.predict(p_arr)
        return np.clip(calibrated, 0.0, 1.0)
