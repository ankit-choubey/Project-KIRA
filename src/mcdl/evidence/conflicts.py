"""Metric Conflict Detector.

Detects and flags conflicting empirical claims across raw artifacts and reports
to prevent publishing contradictory metrics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from mcdl.evidence.schema import MetricConflict
from mcdl.evidence.adapter import load_json_safe


class ConflictDetector:
    """Audits artifact files in a directory to identify cross-artifact value discrepancies."""

    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)

    def detect_all_conflicts(self) -> list[MetricConflict]:
        conflicts: list[MetricConflict] = []

        # 1. Check Baseline Held-out ASR Conflicts
        asr_sources: list[dict[str, Any]] = []

        # From coevolution / red metrics
        red_metrics = load_json_safe(self.run_dir / "red_metrics.json")
        if isinstance(red_metrics, dict):
            asr_sources.append({
                "source": "red_metrics.json",
                "json_path": "asr_heldout",
                "value": red_metrics.get("asr_heldout", red_metrics.get("asr")),
                "scope": "Red Adversarial Search Overall"
            })

        # From experiment register
        exp_reg = load_json_safe(self.run_dir / "experiment_register.json")
        if isinstance(exp_reg, list):
            for exp in exp_reg:
                exp_id = exp.get("experiment_id", "")
                metrics = exp.get("metrics", {})
                if "asr_heldout" in metrics:
                    asr_sources.append({
                        "source": f"experiment_register.json ({exp_id})",
                        "json_path": f"metrics.asr_heldout",
                        "value": metrics.get("asr_heldout"),
                        "scope": exp.get("hypothesis", "Experiment register entry")
                    })

        # From promotion history
        promo = load_json_safe(self.run_dir / "promotion_history.json")
        if isinstance(promo, list):
            for p in promo:
                metrics = p.get("challenger_metrics", {})
                if "asr" in metrics or "asr_heldout" in metrics:
                    asr_sources.append({
                        "source": f"promotion_history.json ({p.get('challenger_id')})",
                        "json_path": "challenger_metrics.asr",
                        "value": metrics.get("asr", metrics.get("asr_heldout")),
                        "scope": "Challenger Gate Evaluation"
                    })

        # Evaluate if differing non-null values exist across unconstrained scopes
        distinct_vals = {s["value"] for s in asr_sources if s["value"] is not None}
        if len(distinct_vals) > 1:
            conflicts.append(
                MetricConflict(
                    metric="Baseline Held-Out ASR",
                    sources=asr_sources,
                    status="CONFLICT",
                    resolution="REQUIRES_SCOPE_AUDIT",
                    explanation=(
                        "Multiple values found across artifacts (e.g. unhardened baseline ~14.55% "
                        "vs hardened challenger 0.0% vs zero-day 100%). Distinct populations must be explicitly partitioned."
                    )
                )
            )

        # 2. Check MED (Minimum Evading Distance)
        med_sources: list[dict[str, Any]] = []
        if isinstance(red_metrics, dict) and "med" in red_metrics:
            med_sources.append({
                "source": "red_metrics.json",
                "json_path": "med",
                "value": red_metrics.get("med"),
                "scope": "Overall Red Search"
            })
        if isinstance(exp_reg, list):
            for exp in exp_reg:
                if "med" in exp.get("metrics", {}):
                    med_sources.append({
                        "source": f"experiment_register.json ({exp.get('experiment_id')})",
                        "json_path": "metrics.med",
                        "value": exp.get("metrics", {}).get("med"),
                        "scope": exp.get("experiment_id")
                    })

        distinct_med = {s["value"] for s in med_sources if s["value"] is not None}
        if len(distinct_med) > 1 or any(s["value"] is None for s in med_sources):
            conflicts.append(
                MetricConflict(
                    metric="Minimum Evading Distance (MED)",
                    sources=med_sources,
                    status="CONFLICT",
                    resolution="REQUIRES_SCOPE_AUDIT",
                    explanation="Discrepancy in MED reporting across experiments (e.g. 2.8488 vs 0.0 vs null)."
                )
            )

        return conflicts
