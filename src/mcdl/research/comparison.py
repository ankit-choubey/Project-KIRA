"""Research Master Comparison & Decision Matrix Engine.

Aggregates stage metrics, assigns statistical certainty flags, and generates
transparent decision tables without fabricating unmeasured data.
"""

from __future__ import annotations

from typing import Any, Optional


def apply_statistical_flags(
    n_samples: int,
    n_positive: int,
    ci_width: Optional[float] = None,
) -> list[str]:
    """Applies standardized data power and uncertainty flags."""
    flags = []
    if n_samples < 100:
        flags.append("UNDERPOWERED")
    if n_positive < 30:
        flags.append("LOW_SAMPLE")
    if ci_width is not None and ci_width > 0.15:
        flags.append("HIGH_VARIANCE")
    return flags


def generate_wave1_summary_table(
    s00_status: dict[str, Any],
    s01_status: dict[str, Any],
    l3_metrics: Optional[dict[str, Any]],
    c2st_metrics: Optional[dict[str, Any]],
    tstr_metrics: Optional[dict[str, Any]],
    graph_audit: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """Compiles the Phase 1 Wave 1 research results into a unified schema."""
    entries = []

    # 1. L3
    l3_complete = l3_metrics is not None and l3_metrics.get("status") == "COMPLETE"
    entries.append({
        "track": "L3 Behavioral Fidelity (P1–P4)",
        "stage_id": "S-02",
        "status": l3_metrics.get("status", "NOT_MEASURED") if l3_metrics else "NOT_MEASURED",
        "primary_metric": f"P1..P4 Ratios: {l3_metrics.get('p1_interarrival', {}).get('ratio', 'null')}" if l3_metrics else "null",
        "flags": apply_statistical_flags(l3_metrics.get("sample_count_synthetic", 0), 0) if l3_metrics else ["NOT_MEASURED"],
        "preliminary_decision": "RESEARCH ONLY" if l3_complete else "INCONCLUSIVE",
    })

    # 2. C2ST
    c2st_auc = c2st_metrics.get("c2st_auc") if c2st_metrics else None
    c2st_samples = c2st_metrics.get("sample_counts", {}).get("n_total", 0) if c2st_metrics else 0
    entries.append({
        "track": "C2ST Discriminator AUC",
        "stage_id": "S-03",
        "status": c2st_metrics.get("status", "NOT_MEASURED") if c2st_metrics else "NOT_MEASURED",
        "primary_metric": f"AUC = {c2st_auc}" if c2st_auc is not None else "null",
        "flags": apply_statistical_flags(c2st_samples, c2st_samples // 2) if c2st_metrics else ["NOT_MEASURED"],
        "preliminary_decision": "RESEARCH ONLY" if c2st_auc is not None else "INCONCLUSIVE",
    })

    # 3. TSTR
    tstr_auc = tstr_metrics.get("tstr", {}).get("pr_auc") if tstr_metrics and tstr_metrics.get("tstr") else None
    entries.append({
        "track": "TSTR Transfer PR-AUC",
        "stage_id": "S-04",
        "status": tstr_metrics.get("status", "NOT_MEASURED") if tstr_metrics else "NOT_MEASURED",
        "primary_metric": f"PR-AUC = {tstr_auc}" if tstr_auc is not None else "null",
        "flags": apply_statistical_flags(tstr_metrics.get("tstr", {}).get("n_test_real", 0), tstr_metrics.get("tstr", {}).get("n_test_real_fraud", 0)) if tstr_metrics and tstr_metrics.get("tstr") else ["NOT_MEASURED"],
        "preliminary_decision": "RESEARCH ONLY" if tstr_auc is not None else "INCONCLUSIVE",
    })

    # 4. Graph Leakage Audit
    audit_passed = graph_audit.get("audit_passed", False) if graph_audit else False
    entries.append({
        "track": "Graph Topology Causal Leakage Audit",
        "stage_id": "S-05",
        "status": graph_audit.get("status", "NOT_MEASURED") if graph_audit else "NOT_MEASURED",
        "primary_metric": "0 Violations (Causal OK)" if audit_passed else "LEAKAGE DETECTED",
        "flags": [],
        "preliminary_decision": "ELIGIBLE_FOR_GPU_G01" if audit_passed else "BLOCKED_LEAKAGE_AUDIT",
    })

    return {
        "baseline_run_id": "run_tiny_s20260827_193f7897_40997ab",
        "environment_status": s00_status.get("status", "UNKNOWN"),
        "baseline_integrity_status": s01_status.get("status", "UNKNOWN"),
        "entries": entries,
    }
