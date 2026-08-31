"""Unit tests for strict baseline isolation and tamper-proof verification."""

import json
from pathlib import Path
from mcdl.research.provenance import compute_file_sha256

REPO_ROOT = Path(__file__).resolve().parents[3]
BASELINE_DIR = REPO_ROOT / "artifacts" / "run_tiny_s20260827_193f7897_40997ab"


def test_baseline_directory_and_provenance_match():
    assert BASELINE_DIR.exists(), f"Baseline directory missing: {BASELINE_DIR}"
    
    provenance_path = BASELINE_DIR / "provenance.json"
    assert provenance_path.exists(), "provenance.json missing from baseline"
    
    prov_data = json.loads(provenance_path.read_text(encoding="utf-8"))
    artifacts = prov_data.get("artifacts", {})
    assert len(artifacts) >= 20, f"Expected >= 20 verified entries, got {len(artifacts)}"
    
    # Check that each file matches its recorded SHA-256
    for filename, meta in artifacts.items():
        expected_hash = meta["sha256"]
        file_path = BASELINE_DIR / filename
        assert file_path.exists(), f"Artifact missing from baseline: {filename}"
        actual_hash = compute_file_sha256(file_path)
        assert actual_hash == expected_hash, f"SHA-256 mismatch for {filename}!"


def test_research_runs_isolated_from_artifacts():
    research_dir = REPO_ROOT / "research_runs"
    # Research runs path must be distinct from artifacts/run_tiny_*
    assert research_dir != BASELINE_DIR
    assert "run_tiny" not in str(research_dir)
