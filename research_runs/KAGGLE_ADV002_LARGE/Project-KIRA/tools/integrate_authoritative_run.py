#!/usr/bin/env python3
"""Authoritative Run Integration Tool.

Validates, checks hashes, and prepares frontend-consumable data packages
from a completed authoritative research run without modifying raw sources.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

REQUIRED_ARTIFACTS = [
    "manifest.json",
    "blue_metrics.json",
    "red_metrics.json",
    "coevolution_metrics.json",
    "intent_ablation.json",
    "latency_benchmark.json",
    "promotion_history.json",
    "calibration.json",
    "external_anchor.json",
    "three_world_evaluation.json",
    "provenance.json",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def integrate_run(
    run_id: str,
    runs_dir: Path = REPO_ROOT / "artifacts",
    target_data_dir: Path = REPO_ROOT / "frontend" / "public" / "data",
    dry_run: bool = False,
) -> dict[str, Any]:
    run_dir = runs_dir / run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    report: dict[str, Any] = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "dry_run": dry_run,
        "status": "PENDING",
        "missing_artifacts": [],
        "invalid_json_artifacts": [],
        "hash_checks": {},
        "files_prepared": [],
    }

    # 1. Check artifact completeness & JSON validity
    for art in REQUIRED_ARTIFACTS:
        art_path = run_dir / art
        if not art_path.exists():
            report["missing_artifacts"].append(art)
            continue
        try:
            with open(art_path, "r", encoding="utf-8") as f:
                json.load(f)
        except Exception as e:
            report["invalid_json_artifacts"].append({"artifact": art, "error": str(e)})

    # 2. Check provenance hashes if provenance.json exists
    prov_path = run_dir / "provenance.json"
    if prov_path.exists():
        try:
            prov_data = json.loads(prov_path.read_text(encoding="utf-8"))
            expected_hashes = prov_data.get("artifact_hashes", {})
            for fname, exp_hash in expected_hashes.items():
                target_f = run_dir / fname
                if target_f.exists():
                    actual_hash = sha256_file(target_f)
                    match = actual_hash == exp_hash
                    report["hash_checks"][fname] = {
                        "expected": exp_hash,
                        "actual": actual_hash,
                        "match": match,
                    }
                    if not match:
                        report["status"] = "HASH_MISMATCH"
        except Exception as e:
            report["hash_checks"]["_error"] = str(e)

    if report["missing_artifacts"] or report["invalid_json_artifacts"]:
        report["status"] = "FAILED"
        return report

    if report["status"] != "HASH_MISMATCH":
        report["status"] = "PASS"

    # 3. Copy/prepare frontend consumable data if not dry_run
    if not dry_run and report["status"] == "PASS":
        target_data_dir.mkdir(parents=True, exist_ok=True)
        for art in REQUIRED_ARTIFACTS:
            src = run_dir / art
            dst = target_data_dir / art
            shutil.copy2(src, dst)
            report["files_prepared"].append(str(dst))

        # Update artifacts/LATEST
        latest_file = runs_dir / "LATEST"
        latest_file.write_text(f"{run_id}\n", encoding="utf-8")
        report["latest_updated"] = True

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Integrate authoritative run into frontend/API.")
    parser.add_argument("run_id", type=str, help="Run ID to integrate")
    parser.add_argument("--dry-run", action="store_true", help="Perform validation without copying")
    args = parser.parse_args()

    try:
        report = integrate_run(args.run_id, dry_run=args.dry_run)
        print(json.dumps(report, indent=2))
        if report["status"] != "PASS":
            sys.exit(1)
    except Exception as exc:
        print(f"Error during integration: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
