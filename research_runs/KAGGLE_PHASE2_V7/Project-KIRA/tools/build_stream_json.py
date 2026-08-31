#!/usr/bin/env python3
"""Stream Builder Utility.

Joins raw transactions and decisions, retains all fraud and hard negatives,
downsamples benign rows up to 2,000 items with ~14 concise fields to produce a
lightweight (<1.5 MB) stream.json for the frontend dashboard.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))


def build_stream(
    run_dir: Path,
    output_path: Path,
    max_benign: int = 1900,
    seed: int = 20260827,
    dry_run: bool = False,
) -> dict[str, Any]:
    txns_file = run_dir / "transactions.json"
    decisions_file = run_dir / "decisions.json"

    if not txns_file.exists():
        raise FileNotFoundError(f"Missing {txns_file}")
    if not decisions_file.exists():
        raise FileNotFoundError(f"Missing {decisions_file}")

    with open(txns_file, "r", encoding="utf-8") as f:
        raw_txns = json.load(f)
    with open(decisions_file, "r", encoding="utf-8") as f:
        raw_decisions = json.load(f)

    # Index decisions by txn_id
    dec_map: dict[str, dict[str, Any]] = {}
    for d in raw_decisions:
        txn_id = d.get("txn_id")
        if txn_id:
            dec_map[txn_id] = d

    frauds: list[dict[str, Any]] = []
    hard_negatives: list[dict[str, Any]] = []
    benign_rows: list[dict[str, Any]] = []

    for t in raw_txns:
        txn_id = t.get("txn_id")
        if not txn_id or txn_id not in dec_map:
            continue

        decision = dec_map[txn_id]
        is_fraud = bool(t.get("is_fraud", False))
        dec_val = decision.get("decision", "ALLOW")
        risk_score = float(decision.get("risk_score", 0.0))

        # Compact 14-field representation
        row = {
            "txn_id": txn_id,
            "timestamp": t.get("timestamp"),
            "card_id": t.get("card_id"),
            "merchant_id": t.get("merchant_id"),
            "device_id": t.get("device_id"),
            "amount": round(float(t.get("amount", 0.0)), 2),
            "currency": t.get("currency", "USD"),
            "channel": t.get("channel", "ECOM"),
            "is_fraud": is_fraud,
            "decision": dec_val,
            "risk_score": round(risk_score, 4),
            "calibrated_score": round(float(decision.get("calibrated_score", risk_score)), 4),
            "reason_codes": decision.get("reason_codes", []),
            "model_version": decision.get("model_version", "authoritative"),
        }

        if is_fraud:
            frauds.append(row)
        elif dec_val in ("BLOCK", "STEP_UP") or risk_score >= 0.5:
            # Hard negative (benign flagged with high risk or step-up)
            hard_negatives.append(row)
        else:
            benign_rows.append(row)

    # Deterministic sampling of benign rows
    rng = random.Random(seed)
    sampled_benign = benign_rows
    if len(benign_rows) > max_benign:
        sampled_benign = rng.sample(benign_rows, max_benign)

    combined = frauds + hard_negatives + sampled_benign
    # Sort chronologically
    combined.sort(key=lambda r: r.get("timestamp", 0))

    payload = {
        "run_id": run_dir.name,
        "total_stream_rows": len(combined),
        "fraud_count": len(frauds),
        "hard_negative_count": len(hard_negatives),
        "benign_count": len(sampled_benign),
        "rows": combined,
    }

    report = {
        "status": "PASS",
        "total_rows": len(combined),
        "fraud_count": len(frauds),
        "hard_negative_count": len(hard_negatives),
        "sampled_benign_count": len(sampled_benign),
        "dry_run": dry_run,
    }

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, separators=(",", ":"))
        file_size_kb = output_path.stat().st_size / 1024
        report["output_path"] = str(output_path)
        report["file_size_kb"] = round(file_size_kb, 2)
        report["size_under_target"] = file_size_kb < 1536  # < 1.5 MB

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build lightweight stream.json for frontend.")
    parser.add_argument("run_dir", type=Path, help="Path to run directory containing transactions.json")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "frontend" / "public" / "data" / "stream.json",
        help="Target output path",
    )
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without writing")
    args = parser.parse_args()

    try:
        report = build_stream(args.run_dir, args.output, dry_run=args.dry_run)
        print(json.dumps(report, indent=2))
    except Exception as exc:
        print(f"Error building stream: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
