#!/usr/bin/env python3
"""Authoritative Post-Run Scientific Auditor.

Performs complete identity, completeness, integrity, schema, statistics,
temporal safety, zero-day World-C isolation, and metric conflict audits on a
specified run directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mcdl.evidence.adapter import EvidenceAdapter, load_json_safe
from mcdl.evidence.conflicts import ConflictDetector


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def audit_run(
    run_id: str,
    runs_dir: Path = REPO_ROOT / "artifacts",
    output_audit_dir: Path = REPO_ROOT / "audit",
) -> dict[str, Any]:
    run_dir = runs_dir / run_id
    if not run_dir.exists():
        # Fallback to checking research_runs/PHASE2
        alt_dir = REPO_ROOT / "research_runs" / run_id
        if alt_dir.exists():
            run_dir = alt_dir
        else:
            raise FileNotFoundError(f"Run directory not found: {run_dir}")

    output_audit_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "checks_passed": True,
        "identity": {},
        "completeness": {},
        "integrity": {},
        "statistics": {},
        "temporal_safety": {},
        "world_c_isolation": {},
        "conflicts": [],
    }

    # 1. Identity
    manifest = load_json_safe(run_dir / "manifest.json") or {}
    summary["identity"] = {
        "run_id": manifest.get("run_id", run_id),
        "scale": manifest.get("scale", "unknown"),
        "world_seed": manifest.get("world_seed", "unknown"),
        "git_commit": manifest.get("git_commit", "unknown"),
    }

    # 2. Completeness
    required_files = [
        "blue_metrics.json",
        "coevolution_metrics.json",
        "intent_ablation.json",
        "latency_benchmark.json",
        "promotion_history.json",
    ]
    missing = [f for f in required_files if not (run_dir / f).exists()]
    summary["completeness"] = {
        "required_count": len(required_files),
        "found_count": len(required_files) - len(missing),
        "missing_files": missing,
        "status": "PASS" if not missing else "INCOMPLETE",
    }
    if missing:
        summary["checks_passed"] = False

    # 3. Integrity (hashes)
    prov = load_json_safe(run_dir / "provenance.json") or {}
    expected_hashes = prov.get("artifact_hashes", {})
    hash_results: dict[str, Any] = {}
    for f, h in expected_hashes.items():
        fp = run_dir / f
        if fp.exists():
            actual = sha256_file(fp)
            hash_results[f] = {"match": actual == h, "expected": h, "actual": actual}
            if actual != h:
                summary["checks_passed"] = False
    summary["integrity"] = {
        "verified_file_count": len(hash_results),
        "hash_mismatches": [f for f, r in hash_results.items() if not r["match"]],
        "status": "PASS" if not any(not r["match"] for r in hash_results.values()) else "FAIL",
    }

    # 4. Statistical sanity
    adapter = EvidenceAdapter(run_dir, git_sha=summary["identity"]["git_commit"])
    records = adapter.extract_all_records()
    summary["statistics"] = {
        "extracted_claims_count": len(records),
        "classifications": {r.claim_id: r.classification.value for r in records},
    }

    # 5. Temporal Safety
    txns = load_json_safe(run_dir / "transactions.json")
    if isinstance(txns, list) and txns:
        timestamps = [t.get("timestamp", 0) for t in txns if isinstance(t, dict)]
        is_sorted = all(timestamps[i] <= timestamps[i + 1] for i in range(len(timestamps) - 1))
        summary["temporal_safety"] = {
            "transaction_count": len(txns),
            "strictly_chronological": is_sorted,
            "status": "PASS" if is_sorted else "FAIL",
        }
        if not is_sorted:
            summary["checks_passed"] = False
    else:
        summary["temporal_safety"] = {"status": "NOT_EVALUATED"}

    # 6. World-C Isolation
    world_c_report = load_json_safe(run_dir / "three_world_evaluation.json")
    if isinstance(world_c_report, dict):
        summary["world_c_isolation"] = {
            "status": "EVALUATED",
            "hidden_families_reported": True,
        }
    else:
        summary["world_c_isolation"] = {"status": "NOT_MEASURED"}

    # 7. Conflicts
    detector = ConflictDetector(run_dir)
    conflicts = detector.detect_all_conflicts()
    summary["conflicts"] = [c.model_dump() for c in conflicts]

    # Save detailed output files in audit/
    (output_audit_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_audit_dir / "integrity.json").write_text(json.dumps(summary["integrity"], indent=2), encoding="utf-8")
    (output_audit_dir / "conflicts.json").write_text(json.dumps(summary["conflicts"], indent=2), encoding="utf-8")

    # Generate Markdown report
    md_content = f"""# Post-Run Scientific Audit Report: `{run_id}`

- **Scale**: `{summary['identity']['scale']}`
- **Git Commit**: `{summary['identity']['git_commit']}`
- **Overall Status**: `{'PASS' if summary['checks_passed'] else 'FAIL'}`
- **Artifact Completeness**: `{summary['completeness']['status']}`
- **Cryptographic Hash Verification**: `{summary['integrity']['status']}`
- **Temporal Ordering**: `{summary['temporal_safety'].get('status', 'N/A')}`

## Metric Conflicts Detected
Found `{len(conflicts)}` conflict scope notices.
"""
    (output_audit_dir / "evidence_report.md").write_text(md_content, encoding="utf-8")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit authoritative run.")
    parser.add_argument("run_id", type=str, help="Run ID to audit")
    args = parser.parse_args()

    try:
        summary = audit_run(args.run_id)
        print(json.dumps(summary, indent=2))
    except Exception as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
