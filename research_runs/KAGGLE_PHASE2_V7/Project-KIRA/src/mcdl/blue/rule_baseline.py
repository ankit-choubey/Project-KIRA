"""Heuristic Rule-Based Fraud Detector — Minimum Competitive Baseline.

Establishes the transparent, interpretable business-rule baseline that ML models must beat.
"""

from __future__ import annotations

import numpy as np
import polars as pl


class RuleBaseline:
    """Deterministic heuristic fraud detection engine."""

    def __init__(self) -> None:
        self.rules = [
            ("R1_VELOCITY_SPIKE", 0.35),
            ("R2_AMOUNT_SPIKE", 0.30),
            ("R3_GEO_IMPOSSIBLE", 0.35),
            ("R4_AUTH_FAILURE_BURST", 0.25),
            ("R5_NEW_DEVICE_HIGH_AMOUNT", 0.20),
            ("R6_LAG_MERCH_FRAUD", 0.20),
        ]

    def predict_proba(self, df: pl.DataFrame) -> np.ndarray:
        """Computes continuous rule-based risk score in [0.0, 1.0]."""
        n = len(df)
        if n == 0:
            return np.empty(0, dtype=np.float64)

        scores = np.zeros(n, dtype=np.float64)

        # R1: Velocity Spike (>= 3 txns in 1 hour)
        r1_mask = df["cust_velocity_1h_count"].to_numpy() >= 3
        scores += 0.35 * r1_mask.astype(np.float64)

        # R2: Amount Spike (ratio >= 3.5 and amount >= 150)
        r2_mask = (df["cust_amount_to_avg_ratio"].to_numpy() >= 3.5) & (df["amount"].to_numpy() >= 150.0)
        scores += 0.30 * r2_mask.astype(np.float64)

        # R3: High Implied Speed (>= 300 km/h and distance >= 50km)
        r3_mask = (df["speed_kmh"].to_numpy() >= 300.0) & (df["dist_from_prev_txn_km"].to_numpy() >= 50.0)
        scores += 0.35 * r3_mask.astype(np.float64)

        # R4: Repeated Auth Failures (>= 2)
        r4_mask = df["auth_failed_count"].to_numpy() >= 2
        scores += 0.25 * r4_mask.astype(np.float64)

        # R5: New Device on Large Amount (is_new_device == 1 and amount >= 200)
        r5_mask = (df["is_new_device"].to_numpy() == 1) & (df["amount"].to_numpy() >= 200.0)
        scores += 0.20 * r5_mask.astype(np.float64)

        # R6: Merchant 7-Day Lag Fraud Rate (>= 0.05)
        r6_mask = df["merch_fraud_rate_7d_lag"].to_numpy() >= 0.05
        scores += 0.20 * r6_mask.astype(np.float64)

        # Clip scores to [0.0, 1.0]
        return np.clip(scores, 0.0, 1.0)

    def predict(self, df: pl.DataFrame, threshold: float = 0.50) -> np.ndarray:
        """Binary classification decision based on decision threshold."""
        proba = self.predict_proba(df)
        return (proba >= threshold).astype(np.int64)
