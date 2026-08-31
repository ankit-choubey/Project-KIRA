"""On-Demand TreeSHAP Feature Attribution Explainer.

Generates exact local feature attributions for individual transaction inspections
using LightGBM's native TreeSHAP implementation.
"""

from __future__ import annotations

from typing import Any
import numpy as np
import polars as pl

from mcdl.features.spec import FEATURE_NAMES
from mcdl.schemas import SHAPExplanation


class TreeSHAPExplainer:
    """On-demand feature attribution engine for Blue model predictions."""

    def __init__(self, booster: Any, feature_names: list[str] | None = None) -> None:
        self.booster = booster
        self.feature_names = feature_names or FEATURE_NAMES

    def explain(self, row: dict[str, Any] | pl.DataFrame, txn_id: str | None = None) -> SHAPExplanation:
        """Computes exact TreeSHAP contributions for a single transaction."""
        if isinstance(row, pl.DataFrame):
            t_id = str(row["txn_id"][0]) if "txn_id" in row.columns else "unknown_txn"
            feature_vector = row.select(self.feature_names).to_numpy()
        else:
            t_id = str(row.get("txn_id", txn_id or "unknown_txn"))
            feature_vector = np.array([[float(row[col]) for col in self.feature_names]], dtype=np.float64)

        # LightGBM pred_contrib=True returns [shap_val_1, ..., shap_val_k, base_value]
        contribs = self.booster.predict(feature_vector, pred_contrib=True)[0]
        base_value = float(contribs[-1])
        shap_values = contribs[:-1]

        feature_contributions = {
            name: float(round(val, 6))
            for name, val in zip(self.feature_names, shap_values)
        }

        # Sort top drivers by absolute contribution magnitude descending
        sorted_drivers = sorted(
            feature_contributions.items(),
            key=lambda item: abs(item[1]),
            reverse=True,
        )

        return SHAPExplanation(
            txn_id=t_id,
            base_value=float(round(base_value, 6)),
            feature_contributions=feature_contributions,
            top_features=sorted_drivers[:10],
        )
