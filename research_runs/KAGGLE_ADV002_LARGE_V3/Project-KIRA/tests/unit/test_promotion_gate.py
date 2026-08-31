"""Unit tests for Multi-Objective Promotion Gate and Rollback."""

from __future__ import annotations

import pytest
from mcdl.loop.promotion import MultiObjectivePromotionGate, PromotionGateConfig
from mcdl.schemas import BlueMetrics


def test_promotion_gate_success():
    gate = MultiObjectivePromotionGate(PromotionGateConfig())

    champ_blue = BlueMetrics(pr_auc=0.65, fpr=0.001, ece=0.00)
    chal_blue = BlueMetrics(pr_auc=0.66, fpr=0.001, ece=0.00)

    decision = gate.evaluate(
        champion_version="blue_r0",
        challenger_version="challenger_r1",
        champion_blue=champ_blue,
        challenger_blue=chal_blue,
        baseline_seen_asr=0.80,
        challenger_seen_asr=0.10,  # Huge security improvement
        baseline_heldout_asr=0.85,
        challenger_heldout_asr=0.20,  # Demonstrates generalization
        policy_distribution={"ALLOW": 0.98, "STEP_UP": 0.015, "BLOCK": 0.005},
    )

    assert decision.promoted is True
    assert decision.champion_version == "challenger_r1"
    assert "PROMOTED_MULTI_OBJECTIVE_IMPROVEMENT" in decision.reasons


def test_promotion_gate_rollback_on_excessive_fpr():
    gate = MultiObjectivePromotionGate(PromotionGateConfig(max_fpr=0.05))

    champ_blue = BlueMetrics(pr_auc=0.65, fpr=0.001, ece=0.00)
    chal_blue = BlueMetrics(pr_auc=0.70, fpr=0.09, ece=0.00)  # Excessive false positives!

    decision = gate.evaluate(
        champion_version="blue_r0",
        challenger_version="challenger_r1",
        champion_blue=champ_blue,
        challenger_blue=chal_blue,
        baseline_seen_asr=0.80,
        challenger_seen_asr=0.05,
        baseline_heldout_asr=0.85,
        challenger_heldout_asr=0.10,
        policy_distribution={"ALLOW": 0.90, "STEP_UP": 0.05, "BLOCK": 0.05},
    )

    assert decision.promoted is False
    assert decision.champion_version == "blue_r0"  # Rollback preserves previous champion
    assert any("REJECT_EXCESSIVE_FPR" in r for r in decision.reasons)


def test_promotion_gate_rollback_on_heldout_regression():
    gate = MultiObjectivePromotionGate(PromotionGateConfig())

    champ_blue = BlueMetrics(pr_auc=0.65, fpr=0.001, ece=0.00)
    chal_blue = BlueMetrics(pr_auc=0.65, fpr=0.001, ece=0.00)

    decision = gate.evaluate(
        champion_version="blue_r0",
        challenger_version="challenger_r1",
        champion_blue=champ_blue,
        challenger_blue=chal_blue,
        baseline_seen_asr=0.80,
        challenger_seen_asr=0.05,  # Memorized seen attacks
        baseline_heldout_asr=0.30,
        challenger_heldout_asr=0.65,  # Catastrophic regression on held-out variants!
        policy_distribution={"ALLOW": 0.98, "STEP_UP": 0.015, "BLOCK": 0.005},
    )

    assert decision.promoted is False
    assert decision.champion_version == "blue_r0"
    assert any("REJECT_HELDOUT_REGRESSION" in r for r in decision.reasons)
