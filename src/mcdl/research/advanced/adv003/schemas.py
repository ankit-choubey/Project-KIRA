"""ADV-003 Schemas and Data Models.

Defines schemas for defensive knowledge records, challenger models,
promotion gating, round metrics, and adaptive defense curves.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class PromotionDecision(str, Enum):
    INITIAL = "INITIAL"
    PROMOTE = "PROMOTE"
    REJECT = "REJECT"
    ROLLBACK = "ROLLBACK"


class AntiForgettingStatus(str, Enum):
    NO_FORGETTING = "NO_FORGETTING"
    MINOR_DEGRADATION = "MINOR_DEGRADATION"
    SIGNIFICANT_FORGETTING = "SIGNIFICANT_FORGETTING"
    INCONCLUSIVE = "INCONCLUSIVE"


class KnowledgeEffect(str, Enum):
    EVASION_EXPLOIT = "EVASION_EXPLOIT"
    HIGH_RISK_NEAR_MISS = "HIGH_RISK_NEAR_MISS"
    MUTATION_VULNERABILITY = "MUTATION_VULNERABILITY"
    FALSE_NEGATIVE_RISK = "FALSE_NEGATIVE_RISK"


@dataclass
class DefensiveKnowledgeRecord:
    """A validated defensive knowledge item derived from an observed attack attempt."""

    knowledge_id: str
    source_experiment: str
    round_number: int
    attack_id: str
    attack_family: str
    features: dict[str, float]
    target_txn_id: str
    customer_id: str
    merchant_id: str
    amount: float
    observed_effect: KnowledgeEffect
    blue_score_before: float
    blue_decision_before: str
    perturbation_distance: float
    queries_used: int
    confidence: float
    is_validated: bool
    source_artifact_hash: str
    provenance: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["observed_effect"] = self.observed_effect.value
        return d


@dataclass
class PromotionGateConfig:
    """Configurable thresholds for challenger promotion gating."""

    min_asr_reduction: float = 0.00          # Challenger validation ASR must be <= champion validation ASR
    max_legacy_degradation: float = 0.02     # Maximum allowable increase in legacy baseline ASR
    max_heldout_degradation: float = 0.03    # Maximum allowable increase in held-out test ASR
    anti_forgetting_threshold: float = 0.05  # Delta > 0.05 triggers SIGNIFICANT_FORGETTING rejection
    max_brier_score_increase: float = 0.05   # Calibration stability boundary


@dataclass
class PromotionEvaluation:
    """Detailed evaluation report for a challenger promotion gate."""

    round_number: int
    challenger_version: str
    champion_version: str
    validation_asr_champion: float
    validation_asr_challenger: float
    delta_val_asr: float
    legacy_asr_champion: float
    legacy_asr_challenger: float
    delta_legacy_asr: float
    heldout_asr_champion: float
    heldout_asr_challenger: float
    delta_heldout_asr: float
    anti_forgetting_delta: float
    anti_forgetting_status: AntiForgettingStatus
    brier_score_champion: float | None
    brier_score_challenger: float | None
    decision: PromotionDecision
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["anti_forgetting_status"] = self.anti_forgetting_status.value
        d["decision"] = self.decision.value
        return d


@dataclass
class AttackAttemptSummary:
    """Summary metrics for a population of evaluated adversarial attacks."""

    total_attempts: int = 0
    valid_attempts: int = 0
    allowed_evasion: int = 0
    blocked: int = 0
    step_up: int = 0
    errors: int = 0
    timeouts: int = 0
    aggregate_asr: float = 0.0
    family_asr: dict[str, float] = field(default_factory=dict)
    query_budget_asr: dict[str, float] = field(default_factory=dict)
    median_queries: float | None = None
    median_med: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RoundMetricRecord:
    """Round-level telemetry and metrics for the Adaptive Defense Curve."""

    round_number: int
    arm_name: str
    blue_version: str
    parent_blue_version: str | None
    train_attack_count: int
    val_attack_count: int
    heldout_attack_count: int
    legacy_attack_count: int
    val_asr: float
    legacy_asr: float
    heldout_asr: float
    val_asr_delta_from_prev: float
    val_asr_delta_from_round0: float
    anti_forgetting_delta: float
    anti_forgetting_status: str
    promotion_decision: str
    replay_examples_added: int
    total_knowledge_count: int
    runtime_sec: float
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
