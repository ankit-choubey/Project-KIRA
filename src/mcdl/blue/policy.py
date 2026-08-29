"""Cost-Sensitive Decision Policy & Routing Engine.

Maps calibrated risk probabilities and transaction parameters to optimal actions:
ALLOW, STEP_UP, BLOCK by minimizing expected financial loss and customer friction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from mcdl.schemas import BlueDecision, Decision, Transaction


@dataclass(frozen=True)
class PolicyCostConfig:
    """Configurable cost matrix for transaction decision routing."""
    c_fraud_multiplier: float = 1.0
    c_step_up_fixed: float = 2.50
    step_up_fraud_catch_rate: float = 0.90
    false_block_fixed: float = 10.0
    false_block_variable_pct: float = 0.15


class CostSensitiveRouter:
    """Evaluates expected cost across actions and routes transaction to optimal decision."""

    def __init__(self, cost_config: PolicyCostConfig | None = None) -> None:
        self.config = cost_config or PolicyCostConfig()

    def calculate_expected_costs(self, amount: float, p_fraud: float) -> dict[Decision, float]:
        """Calculates expected financial cost for each potential decision action.

        Expected Costs:
          E[Cost(ALLOW)]   = p * amount * c_fraud
          E[Cost(STEP_UP)] = c_step_up_fixed + (1 - catch_rate) * p * amount * c_fraud
          E[Cost(BLOCK)]   = (1 - p) * (false_block_fixed + false_block_variable_pct * amount)
        """
        p = max(0.0, min(1.0, float(p_fraud)))
        amt = max(0.0, float(amount))

        # 1. ALLOW: legitimate transactions cost $0; fraud costs full amount * multiplier
        cost_allow = p * amt * self.config.c_fraud_multiplier

        # 2. STEP_UP: fixed friction cost + residual uncaught fraud (10%)
        cost_step_up = (
            self.config.c_step_up_fixed
            + (1.0 - self.config.step_up_fraud_catch_rate) * p * amt * self.config.c_fraud_multiplier
        )

        # 3. BLOCK: fraud costs $0; legitimate transactions suffer false-block customer friction
        cost_block = (1.0 - p) * (
            self.config.false_block_fixed + self.config.false_block_variable_pct * amt
        )

        return {
            Decision.ALLOW: float(cost_allow),
            Decision.STEP_UP: float(cost_step_up),
            Decision.BLOCK: float(cost_block),
        }

    def route(
        self,
        txn_id: str,
        amount: float,
        risk_score: float,
        calibrated_score: float,
        feature_dict: dict[str, Any] | None = None,
        intent_drift_score: float | None = None,
        latency_ms: float = 1.0,
    ) -> BlueDecision:
        """Determines the cost-optimal decision and generates explainable reason codes."""
        costs = self.calculate_expected_costs(amount, calibrated_score)

        # Find action minimizing expected cost
        best_decision = min(costs, key=costs.get)  # type: ignore

        # Extract audit reason codes
        reason_codes: list[str] = []
        if calibrated_score >= 0.60:
            reason_codes.append("HIGH_FRAUD_PROBABILITY")
        elif calibrated_score >= 0.15:
            reason_codes.append("ELEVATED_RISK_SCORE")

        if feature_dict:
            if feature_dict.get("cust_velocity_1h_count", 0) >= 3:
                reason_codes.append("HIGH_VELOCITY_BURST")
            if feature_dict.get("cust_amount_to_avg_ratio", 1.0) >= 3.0:
                reason_codes.append("AMOUNT_HISTORICAL_SPIKE")
            if feature_dict.get("speed_kmh", 0.0) >= 300.0:
                reason_codes.append("GEOGRAPHIC_VELOCITY_ANOMALY")
            if feature_dict.get("is_new_device", 0) == 1 and amount >= 150.0:
                reason_codes.append("NEW_DEVICE_HIGH_VALUE")
            if feature_dict.get("auth_failed_count", 0) >= 2:
                reason_codes.append("AUTH_FAILURE_SEQUENCE")

        if intent_drift_score is not None and intent_drift_score >= 0.30:
            reason_codes.append("AGENT_MANDATE_INTENT_DRIFT")

        if not reason_codes and best_decision == Decision.ALLOW:
            reason_codes.append("STANDARD_LOW_RISK_PROFILE")

        return BlueDecision(
            txn_id=txn_id,
            risk_score=float(round(risk_score, 6)),
            calibrated_score=float(round(calibrated_score, 6)),
            decision=best_decision,
            reason_codes=reason_codes,
            intent_drift_score=intent_drift_score,
            model_version="lgbm_v1_champion",
            feature_version="feat_v1_causal",
            policy_version="cost_router_v1",
            latency_ms=float(round(latency_ms, 2)),
        )
