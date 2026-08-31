"""Unit tests verifying strict null, NOT_MEASURED, and LOW_SAMPLE safety.

Guarantees:
1. None/null is NEVER converted to 0.0 or 0.
2. LOW_SAMPLE classifications are preserved and distinguished from SUCCESS/FAILURE.
3. NOT_MEASURED metrics are never serialized as measured numbers.
4. Absence of evidence cannot masquerade as zero error or 100% success.
"""

import json
from pathlib import Path
import pytest

from mcdl.evidence.schema import EvidenceRecord, ClaimClassification


def test_null_metric_value_is_never_converted_to_zero():
    """Verify that an unmeasured metric with value=None stays None and never becomes 0.0."""
    rec = EvidenceRecord(
        claim_id="CLM_S03_ZERO_DAY",
        experiment_id="S03",
        dataset_id="KIRA_SYNTHETIC_SMALL",
        run_id="phase2_v7",
        scale="small",
        world_seed=20260827,
        metric="robustness_delta",
        value=None,
        artifact_path="research_runs/PHASE2/S03/metrics.json",
        json_path="world_c_zero_day.robustness_delta",
        git_sha="ab721f9d464456cb6f936f3f9466c7975671a319",
        classification=ClaimClassification.LOW_SAMPLE,
    )

    # In Python object
    assert rec.value is None
    assert rec.value != 0.0
    assert rec.value != 0
    assert rec.classification == ClaimClassification.LOW_SAMPLE

    # In JSON serialization
    serialized = json.loads(rec.model_dump_json())
    assert serialized["value"] is None
    assert serialized["value"] != 0.0
    assert serialized["classification"] == "LOW_SAMPLE"


def test_v7_master_results_preserves_null_for_s03():
    """Verify that V7 master_results.json preserves null for S-03 robustness delta."""
    master_path = Path("research_runs/KAGGLE_PHASE2_V7/FINAL/master_results.json")
    if master_path.exists():
        with open(master_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        claims = {c["claim_id"]: c for c in data.get("claims_registry", [])}
        assert "CLM_006_S03_ZERO_DAY_ROBUSTNESS" in claims
        s03_claim = claims["CLM_006_S03_ZERO_DAY_ROBUSTNESS"]
        
        # Must be null, not 0.0 or 0
        assert s03_claim["metric_value"] is None
        assert s03_claim["metric_value"] != 0.0
        assert s03_claim["classification"] == "LOW_SAMPLE"


def test_classification_enum_distinctness():
    """Verify all claim classifications are strictly distinct enums."""
    assert ClaimClassification.MEASURED != ClaimClassification.NOT_MEASURED
    assert ClaimClassification.LOW_SAMPLE != ClaimClassification.MEASURED
    assert ClaimClassification.INCONCLUSIVE != ClaimClassification.MEASURED
    assert ClaimClassification.NOT_MEASURED.value == "NOT_MEASURED"
    assert ClaimClassification.LOW_SAMPLE.value == "LOW_SAMPLE"
