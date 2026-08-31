"""Unit tests for evidence schema, adapter, and conflict detector."""

from pathlib import Path
from mcdl.evidence.schema import EvidenceRecord, ClaimClassification, MetricConflict
from mcdl.evidence.adapter import EvidenceAdapter
from mcdl.evidence.conflicts import ConflictDetector


def test_evidence_record_preserves_none():
    rec = EvidenceRecord(
        claim_id="CLM_TEST_001",
        experiment_id="EXP_TEST",
        dataset_id="KIRA_SYNTHETIC",
        run_id="test_run",
        scale="tiny",
        world_seed=20260827,
        metric="pr_auc",
        value=None,
        artifact_path="artifacts/test.json",
        json_path="metrics.pr_auc",
        git_sha="test_sha",
        classification=ClaimClassification.NOT_MEASURED,
    )
    assert rec.value is None
    assert rec.classification == ClaimClassification.NOT_MEASURED


def test_evidence_adapter_extracts_from_baseline():
    baseline_dir = Path("artifacts/run_tiny_s20260827_193f7897_40997ab")
    if baseline_dir.exists():
        adapter = EvidenceAdapter(baseline_dir, git_sha="40997ab")
        records = adapter.extract_all_records()
        assert len(records) >= 5
        metrics_found = {r.metric for r in records}
        assert "pr_auc" in metrics_found
        assert "roc_auc" in metrics_found


def test_conflict_detector_runs():
    baseline_dir = Path("artifacts/run_tiny_s20260827_193f7897_40997ab")
    if baseline_dir.exists():
        detector = ConflictDetector(baseline_dir)
        conflicts = detector.detect_all_conflicts()
        assert isinstance(conflicts, list)
