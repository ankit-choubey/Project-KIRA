"""Integration and dry-run tests for Wave 1 Research Runner."""

import json
from pathlib import Path
from mcdl.research.wave1_runner import run_wave1_expansion

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_wave1_dry_run(tmp_path):
    output_dir = tmp_path / "research_runs"
    res = run_wave1_expansion(REPO_ROOT, output_dir=output_dir, dry_run=True)
    
    assert res["status"] == "PHASE_1_COMPLETE"
    assert (output_dir / "WAVE1_REPORT.md").exists()
    assert (output_dir / "MASTER_COMPARISON.json").exists()
    assert (output_dir / "S-00" / "status.json").exists()
    assert (output_dir / "S-01" / "champion_snapshot.json").exists()
    assert (output_dir / "RES-L3" / "metrics.json").exists()
    assert (output_dir / "RES-C2ST" / "metrics.json").exists()
    assert (output_dir / "RES-TSTR" / "metrics.json").exists()
    assert (output_dir / "S-05" / "leakage_audit.json").exists()
    
    snap = json.loads((output_dir / "S-01" / "champion_snapshot.json").read_text())
    assert snap["integrity_status"] == "PASS_22_OF_22"
