"""Agent Intent-Drift Scoring Engine.

Deterministic, auditable verification of autonomous agent delegation mandates.
Calculates intent drift score in [0.0, 1.0] without future leakage.
"""

from __future__ import annotations

from typing import Any
from mcdl.schemas import Mandate, Transaction


def compute_intent_drift(
    txn: Transaction | dict[str, Any],
    mandates: dict[str, Mandate] | None = None,
) -> float:
    """Calculates intent drift score for delegated payments against authorized mandate parameters."""
    if isinstance(txn, Transaction):
        agent_id = txn.agent_id
        mandate_id = txn.mandate_id
        amount = float(txn.amount)
        mcc = str(txn.mcc)
        auth_failed = int(txn.auth_failed_count)
    else:
        agent_id = txn.get("agent_id")
        mandate_id = txn.get("mandate_id")
        amount = float(txn.get("amount", 0.0))
        mcc = str(txn.get("mcc", ""))
        auth_failed = int(txn.get("auth_failed_count", 0))

    # If human-initiated transaction, no delegation drift applies
    if agent_id is None:
        return 0.0

    # If agent initiated without a valid registered mandate -> maximum drift
    if mandate_id is None or mandates is None or mandate_id not in mandates:
        return 1.0

    mandate = mandates[mandate_id]
    drift = 0.0

    # 1. Single transaction amount limit check
    if amount > mandate.max_amount:
        over_ratio = (amount - mandate.max_amount) / mandate.max_amount
        drift += min(0.50, 0.25 + 0.25 * over_ratio)

    # 2. MCC scope compliance check
    if mandate.allowed_mcc and mcc not in mandate.allowed_mcc:
        drift += 0.40

    # 3. Authentication anomalies on agent channel
    if auth_failed > 0:
        drift += min(0.30, 0.15 * auth_failed)

    return float(min(1.0, drift))
