"""Cross-module contracts.

Everything that crosses a module boundary is defined here. Red and Blue are built
by different people in parallel; this file is what stops them drifting apart.

`frontend/src/api.ts` mirrors these models. Change both in the same commit so the
UI breaks loudly rather than rendering the wrong number silently.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# --------------------------------------------------------------------------- #
# Enumerations
# --------------------------------------------------------------------------- #


class Archetype(str, Enum):
    SALARIED_URBAN = "salaried_urban"
    STUDENT = "student"
    SMALL_BUSINESS = "small_business"
    HIGH_NET_WORTH = "high_net_worth"


class Channel(str, Enum):
    CARD_PRESENT = "card_present"
    ECOMMERCE = "ecommerce"
    MOBILE_WALLET = "mobile_wallet"
    RECURRING = "recurring"
    AGENT = "agent"  # initiated by an autonomous payment agent


class Decision(str, Enum):
    ALLOW = "ALLOW"
    STEP_UP = "STEP_UP"
    BLOCK = "BLOCK"


class AttackFamily(str, Enum):
    R1_ATO = "R1_ato"
    R2_VELOCITY_BURST = "R2_velocity_burst"
    R3_LOW_AND_SLOW = "R3_low_and_slow"
    R4_MULE_RING = "R4_mule_ring"
    R8_INTENT_DRIFT = "R8_intent_drift"


class HardNegative(str, Enum):
    """Legitimate behaviour that looks fraudulent. Without these the detector
    learns 'unusual == fraud' and the reported false-positive rate is a lie."""

    NONE = "none"
    TRAVELLER = "traveller"
    FLASH_SALE = "flash_sale"
    SHARED_FAMILY_DEVICE = "shared_family_device"


# --------------------------------------------------------------------------- #
# World entities
# --------------------------------------------------------------------------- #


class Customer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str
    archetype: Archetype
    home_lat: float
    home_lon: float
    account_opened: datetime
    credit_limit: float
    # Behavioural parameters, drawn per customer at world creation. The detector
    # never sees these; they are what it has to infer from history.
    mean_log_amount: float
    std_log_amount: float
    daily_txn_rate: float
    has_agent: bool = False


class Merchant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    merchant_id: str
    mcc: str = Field(description="4-digit merchant category code")
    category: str
    lat: float
    lon: float
    risk_tier: Literal["low", "medium", "high"] = "low"


class Device(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: str
    first_seen: datetime
    # A device may legitimately be shared (family) or illegitimately (device farm).
    # The label is hidden evaluation metadata, never a feature.
    shared: bool = False


class Mandate(BaseModel):
    """A user's authorisation to an AI payment agent.

    Modelled after the problem Mastercard's Verifiable Intent framework addresses:
    linking what the user authorised to what the agent actually did. This is our
    prototype mechanism, not a claim about Mastercard's production scoring.
    """

    model_config = ConfigDict(extra="forbid")

    mandate_id: str
    customer_id: str
    agent_id: str
    max_amount: float
    max_txn_count: int
    allowed_mcc: list[str]
    merchant_allowlist: list[str] = Field(default_factory=list)
    valid_from: datetime
    valid_until: datetime
    allowed_geo_radius_km: float = 100.0


# --------------------------------------------------------------------------- #
# The central record
# --------------------------------------------------------------------------- #


class Transaction(BaseModel):
    """One payment event.

    Fields are split into three groups. Only `observable` fields may ever become
    model features; `hidden` fields exist for evaluation only and leaking one into
    the feature set is the fastest way to produce a fake 0.99 PR-AUC.
    """

    model_config = ConfigDict(extra="forbid")

    # --- identity -----------------------------------------------------------
    txn_id: str
    customer_id: str
    merchant_id: str
    device_id: str
    timestamp: datetime

    # --- observable ---------------------------------------------------------
    amount: float = Field(gt=0)
    mcc: str
    channel: Channel
    lat: float
    lon: float
    ip_prefix: str
    is_new_device: bool
    auth_failed_count: int = 0
    agent_id: str | None = None
    mandate_id: str | None = None

    # --- ledger state at time of event (observable, causal by construction) --
    balance_before: float
    available_credit: float

    # --- hidden evaluation metadata -- NEVER a feature ----------------------
    is_fraud: bool = False
    attack_family: AttackFamily | None = None
    attack_instance_id: str | None = None
    attack_variant: int | None = None
    hard_negative: HardNegative = HardNegative.NONE

    @field_validator("mcc")
    @classmethod
    def _mcc_shape(cls, v: str) -> str:
        if not (v.isdigit() and len(v) == 4):
            raise ValueError(f"mcc must be 4 digits, got {v!r}")
        return v

    @classmethod
    def observable_fields(cls) -> list[str]:
        """Fields the Blue team is allowed to see. Used by the leakage probe."""
        return [
            "txn_id", "customer_id", "merchant_id", "device_id", "timestamp",
            "amount", "mcc", "channel", "lat", "lon", "ip_prefix",
            "is_new_device", "auth_failed_count", "agent_id", "mandate_id",
            "balance_before", "available_credit",
        ]

    @classmethod
    def hidden_fields(cls) -> list[str]:
        return [
            "is_fraud", "attack_family", "attack_instance_id",
            "attack_variant", "hard_negative",
        ]


# --------------------------------------------------------------------------- #
# Red team
# --------------------------------------------------------------------------- #


class MutabilityMask(BaseModel):
    """Which fields an attacker can actually control.

    Enforced inside the sampler, not checked afterwards. An "evasion" that changes
    an immutable field is a bug in the mask, not a discovery.
    """

    model_config = ConfigDict(extra="forbid")

    mutable: list[str]
    immutable: list[str]

    def violations(self, before: dict[str, Any], after: dict[str, Any]) -> list[str]:
        return [f for f in self.immutable if before.get(f) != after.get(f)]


class AttackCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attack_id: str
    family: AttackFamily
    variant: int = Field(ge=0, description="variant index within the family")
    transactions: list[Transaction]
    # How many times Blue was probed to produce this. ASR without a budget
    # describes an attacker with impossible capabilities (audit F-05).
    queries_used: int = 0
    perturbation_cost: float = 0.0
    generator_version: str = "0.1.0"
    seed: int = 0


class BlueDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    txn_id: str
    risk_score: float = Field(ge=0.0, le=1.0)
    calibrated_score: float = Field(ge=0.0, le=1.0)
    decision: Decision
    reason_codes: list[str] = Field(default_factory=list)
    intent_drift_score: float | None = None
    model_version: str = "0.1.0"
    feature_version: str = "0.1.0"
    policy_version: str = "0.1.0"
    latency_ms: float = 0.0


class SHAPExplanation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    txn_id: str
    base_value: float
    feature_contributions: dict[str, float] = Field(default_factory=dict)
    top_features: list[tuple[str, float]] = Field(default_factory=list)


class Counterfactual(BaseModel):
    """Minimum Evasion Distance: the smallest change to attacker-controllable
    fields that flips BLOCK -> ALLOW. Reported instead of ASR as the headline
    security metric because it does not move when the threshold moves."""

    model_config = ConfigDict(extra="forbid")

    txn_id: str
    found: bool
    changed_field: str | None = None
    original_value: float | None = None
    evading_value: float | None = None
    distance: float | None = None
    human_readable: str | None = None


# --------------------------------------------------------------------------- #
# Evaluation
# --------------------------------------------------------------------------- #


class FidelityReport(BaseModel):
    """The five-layer realism filter.

    L1 is a hard boolean gate (physics). L2 is necessary but not sufficient.
    L3 and L4 are what actually answer 'is this data good'.
    """

    model_config = ConfigDict(extra="forbid")

    # L1 - validity
    l1_violations: int
    l1_checks: dict[str, int] = Field(default_factory=dict)

    # L2 - marginals and dependency
    l2_ks_by_column: dict[str, float] = Field(default_factory=dict)
    l2_correlation_distance: float | None = None

    # L3 - behavioural, normalised to real-data variability (1.0 == real)
    l3_p1_interarrival_ratio: float | None = None
    l3_p2_burstiness_ratio: float | None = None
    l3_p3_graph_motif_ratio: float | None = None
    l3_p4_velocity_trigger_ratio: float | None = None
    l3_published_baselines: dict[str, float] = Field(default_factory=dict)

    # L4 - detectability. ~0.5 means indistinguishable from real.
    l4_c2st_auc_row: float | None = None
    l4_c2st_auc_entity: float | None = None
    l4_top_giveaway_features: list[str] = Field(default_factory=list)

    # L5 - utility
    l5_tstr_pr_auc: float | None = None
    l5_trtr_pr_auc: float | None = None


class BlueMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pr_auc: float | None = None
    roc_auc: float | None = None
    precision: float | None = None
    recall: float | None = None
    fpr: float | None = None
    ece: float | None = None
    brier: float | None = None
    decision_counts: dict[str, int] = Field(default_factory=dict)
    latency_p50_ms: float | None = None
    latency_p95_ms: float | None = None
    latency_p99_ms: float | None = None


class RedMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # ASR keyed by query budget, e.g. {"1": 0.02, "5": 0.09, "20": 0.21, "100": 0.34}
    asr_by_budget: dict[str, float] = Field(default_factory=dict)
    asr_seen_variants: float | None = None
    asr_heldout_variants: float | None = None  # <- the honest headline
    asr_unseen_family: float | None = None
    mean_evasion_distance: float | None = None
    mask_violations: int = 0
    invalid_attacks: int = 0


class RoundResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    round_index: int
    champion_version: str
    challenger_version: str | None = None
    promoted: bool = False
    promotion_reasons: list[str] = Field(default_factory=list)
    blue: BlueMetrics
    red: RedMetrics


class RunManifest(BaseModel):
    """Provenance for one run. A metric with no manifest does not go in the
    report or the UI."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    created_at: datetime
    git_commit: str = "unknown"
    config_hash: str = "unknown"
    seed: int
    scale: str
    is_fixture: bool = Field(
        default=False,
        description="True for fake artifacts from fixtures.py. The UI must label these.",
    )
    stages_completed: list[str] = Field(default_factory=list)
    timings_sec: dict[str, float] = Field(default_factory=dict)
    n_customers: int = 0
    n_merchants: int = 0
    n_transactions: int = 0
    notes: str = ""


class EvaluationResult(BaseModel):
    """The single artifact the API and the report both read."""

    model_config = ConfigDict(extra="forbid")

    manifest: RunManifest
    fidelity: FidelityReport
    rounds: list[RoundResult] = Field(default_factory=list)
    anchor: BlueMetrics | None = Field(
        default=None,
        description="Performance on the external real dataset. Makes the rest credible.",
    )
    ablations: dict[str, BlueMetrics] = Field(default_factory=dict)


class GateResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gate: int
    name: str
    passed: bool
    checks: list[dict[str, Any]] = Field(default_factory=list)
    ran_at: datetime
