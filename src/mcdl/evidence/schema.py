"""Canonical Evidence and Claims Schema.

This module defines the unified, normalized data structure for all experimental
claims and metrics across KIRA without modifying underlying raw JSON formats.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, field_validator


class ClaimClassification(str, Enum):
    MEASURED = "MEASURED"
    MEASURED_WITH_CAVEAT = "MEASURED_WITH_CAVEAT"
    INCONCLUSIVE = "INCONCLUSIVE"
    LOW_SAMPLE = "LOW_SAMPLE"
    NOT_MEASURED = "NOT_MEASURED"
    FAILURE_FINDING = "FAILURE_FINDING"
    NOT_RUN = "NOT_RUN"


class EvidenceRecord(BaseModel):
    """Canonical representation of a single empirical evidence measurement."""

    claim_id: str = Field(..., description="Unique claim identifier, e.g. CLM_001_BASELINE_PRAUC")
    experiment_id: str = Field(..., description="Experiment or stage code, e.g. EXP_BASELINE_BLUE, G03, S02")
    dataset_id: str = Field(..., description="Dataset name, e.g. KIRA_SYNTHETIC, ULB_CREDITCARD")
    run_id: str = Field(..., description="Run identifier producing the measurement")
    scale: str = Field(..., description="Scale of world: tiny, small, medium, full")
    world_seed: int = Field(..., description="World generation seed")
    model_seed: int | None = Field(default=None, description="Model training seed")
    sample_count: int | None = Field(default=None, description="Number of evaluated transactions")
    positive_count: int | None = Field(default=None, description="Number of fraud transactions")
    metric: str = Field(..., description="Name of the measured metric, e.g. pr_auc, asr, ece, med")
    value: float | None = Field(default=None, description="Exact measured numeric value (None if unmeasured)")
    confidence_interval_95: tuple[float, float] | None = Field(
        default=None, description="95% confidence interval [lower, upper]"
    )
    p_value: float | None = Field(default=None, description="Statistical significance p-value")
    artifact_path: str = Field(..., description="Relative or absolute filesystem path to source artifact")
    json_path: str = Field(..., description="JSONPath or dot-separated path within artifact")
    git_sha: str = Field(..., description="Git commit hash under which artifact was produced")
    classification: ClaimClassification = Field(..., description="Empirical evidence status")

    @field_validator("value", mode="before")
    @classmethod
    def preserve_none_strictly(cls, v: Any) -> Any:
        # Prevent silent coercion of None to 0.0
        return v


class MetricConflict(BaseModel):
    """Conflict record when multiple artifacts report differing values for the same logical metric."""

    metric: str
    sources: list[dict[str, Any]]
    status: str = "CONFLICT"
    resolution: str = "REQUIRES_SCOPE_AUDIT"
    explanation: str
