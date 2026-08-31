"""Canonical Evidence Adapter.

Parses existing raw KIRA JSON artifacts and converts them into normalized
EvidenceRecord instances without mutating any source files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcdl.evidence.schema import ClaimClassification, EvidenceRecord


def load_json_safe(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


class EvidenceAdapter:
    """Normalizes artifacts from an authoritative run directory into canonical EvidenceRecords."""

    def __init__(self, run_dir: Path, git_sha: str = "unknown"):
        self.run_dir = Path(run_dir)
        self.git_sha = git_sha
        self.run_id = self.run_dir.name
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        manifest_path = self.run_dir / "manifest.json"
        data = load_json_safe(manifest_path)
        if isinstance(data, dict):
            return data
        return {
            "run_id": self.run_id,
            "scale": "tiny",
            "world_seed": 20260827,
            "git_commit": self.git_sha,
        }

    def extract_all_records(self) -> list[EvidenceRecord]:
        records: list[EvidenceRecord] = []
        scale = str(self.manifest.get("scale", "tiny"))
        world_seed = int(self.manifest.get("world_seed", 20260827))
        git_sha = str(self.manifest.get("git_commit", self.git_sha))

        # 1. Blue Metrics (Tabular Baseline)
        blue = load_json_safe(self.run_dir / "blue_metrics.json")
        if isinstance(blue, dict):
            pr_auc = blue.get("pr_auc")
            # If PR-AUC is 1.0 on small sample, annotate caveat
            cls_prauc = ClaimClassification.MEASURED
            if pr_auc == 1.0 and blue.get("test_positives", 5) < 30:
                cls_prauc = ClaimClassification.MEASURED_WITH_CAVEAT

            records.append(
                EvidenceRecord(
                    claim_id="CLM_BASELINE_PR_AUC",
                    experiment_id="EXP_BASELINE_BLUE",
                    dataset_id="KIRA_SYNTHETIC",
                    run_id=self.run_id,
                    scale=scale,
                    world_seed=world_seed,
                    model_seed=world_seed,
                    sample_count=blue.get("test_transactions", blue.get("n_test")),
                    positive_count=blue.get("test_positives", blue.get("n_positives")),
                    metric="pr_auc",
                    value=float(pr_auc) if pr_auc is not None else None,
                    artifact_path=str(self.run_dir / "blue_metrics.json"),
                    json_path="pr_auc",
                    git_sha=git_sha,
                    classification=cls_prauc,
                )
            )

            roc_auc = blue.get("roc_auc")
            records.append(
                EvidenceRecord(
                    claim_id="CLM_BASELINE_ROC_AUC",
                    experiment_id="EXP_BASELINE_BLUE",
                    dataset_id="KIRA_SYNTHETIC",
                    run_id=self.run_id,
                    scale=scale,
                    world_seed=world_seed,
                    model_seed=world_seed,
                    sample_count=blue.get("test_transactions"),
                    positive_count=blue.get("test_positives"),
                    metric="roc_auc",
                    value=float(roc_auc) if roc_auc is not None else None,
                    artifact_path=str(self.run_dir / "blue_metrics.json"),
                    json_path="roc_auc",
                    git_sha=git_sha,
                    classification=ClaimClassification.MEASURED,
                )
            )

        # 2. Coevolution Metrics (Red vs Blue adaptation)
        coev = load_json_safe(self.run_dir / "coevolution_metrics.json")
        if isinstance(coev, dict):
            rounds = coev.get("rounds", [])
            for idx, r in enumerate(rounds):
                red_info = r.get("red", {})
                asr_heldout = red_info.get("asr_heldout_variants")
                records.append(
                    EvidenceRecord(
                        claim_id=f"CLM_COEV_ROUND_{idx}_ASR_HELDOUT",
                        experiment_id=f"EXP_COEV_ROUND_{idx}",
                        dataset_id="KIRA_SYNTHETIC",
                        run_id=self.run_id,
                        scale=scale,
                        world_seed=world_seed,
                        model_seed=world_seed,
                        sample_count=red_info.get("n_variants"),
                        positive_count=red_info.get("n_evasions"),
                        metric="asr_heldout",
                        value=float(asr_heldout) if asr_heldout is not None else None,
                        artifact_path=str(self.run_dir / "coevolution_metrics.json"),
                        json_path=f"rounds[{idx}].red.asr_heldout_variants",
                        git_sha=git_sha,
                        classification=ClaimClassification.MEASURED,
                    )
                )

        # 3. Intent Engine Ablation
        intent = load_json_safe(self.run_dir / "intent_ablation.json")
        if isinstance(intent, dict):
            delta_asr = intent.get("delta_asr", intent.get("delta_asr_zero_day"))
            records.append(
                EvidenceRecord(
                    claim_id="CLM_INTENT_ABLATION_ZERO_DAY_DELTA_ASR",
                    experiment_id="EXP_007_H",
                    dataset_id="KIRA_SYNTHETIC",
                    run_id=self.run_id,
                    scale=scale,
                    world_seed=world_seed,
                    model_seed=world_seed,
                    sample_count=intent.get("sample_count"),
                    positive_count=intent.get("positive_count"),
                    metric="delta_asr",
                    value=float(delta_asr) if delta_asr is not None else None,
                    artifact_path=str(self.run_dir / "intent_ablation.json"),
                    json_path="delta_asr",
                    git_sha=git_sha,
                    classification=ClaimClassification.MEASURED if delta_asr is not None else ClaimClassification.NOT_MEASURED,
                )
            )

        # 4. Latency Benchmark
        lat = load_json_safe(self.run_dir / "latency_benchmark.json")
        if isinstance(lat, dict):
            p95 = lat.get("p95_ms", lat.get("p95_latency_ms"))
            records.append(
                EvidenceRecord(
                    claim_id="CLM_BENCHMARK_LOOPBACK_P95_LATENCY",
                    experiment_id="BENCH_LATENCY_LOOPBACK",
                    dataset_id="SYNTHETIC_BENCHMARK",
                    run_id=self.run_id,
                    scale=scale,
                    world_seed=world_seed,
                    model_seed=world_seed,
                    sample_count=lat.get("n_queries", 1000),
                    positive_count=None,
                    metric="p95_latency_ms",
                    value=float(p95) if p95 is not None else None,
                    artifact_path=str(self.run_dir / "latency_benchmark.json"),
                    json_path="p95_ms",
                    git_sha=git_sha,
                    classification=ClaimClassification.MEASURED_WITH_CAVEAT,
                )
            )

        # 5. External Anchor (ULB Dataset)
        anchor = load_json_safe(self.run_dir / "external_anchor.json")
        if isinstance(anchor, dict):
            val_prauc = anchor.get("pr_auc")
            records.append(
                EvidenceRecord(
                    claim_id="CLM_EXTERNAL_ANCHOR_ULB_PRAUC",
                    experiment_id="EXP_EXTERNAL_ANCHOR",
                    dataset_id="ULB_CREDITCARD",
                    run_id=self.run_id,
                    scale="external_full",
                    world_seed=world_seed,
                    model_seed=world_seed,
                    sample_count=anchor.get("sample_count", 284807),
                    positive_count=anchor.get("positive_count", 492),
                    metric="pr_auc",
                    value=float(val_prauc) if val_prauc is not None else None,
                    artifact_path=str(self.run_dir / "external_anchor.json"),
                    json_path="pr_auc",
                    git_sha=git_sha,
                    classification=ClaimClassification.MEASURED,
                )
            )

        # 6. Promotion History
        promo = load_json_safe(self.run_dir / "promotion_history.json")
        if isinstance(promo, list):
            for idx, p in enumerate(promo):
                action = p.get("decision", p.get("action", "REJECT"))
                records.append(
                    EvidenceRecord(
                        claim_id=f"CLM_PROMOTION_GATE_DECISION_{idx}",
                        experiment_id=f"EXP_GATE_CHALLENGER_{idx}",
                        dataset_id="KIRA_SYNTHETIC",
                        run_id=self.run_id,
                        scale=scale,
                        world_seed=world_seed,
                        model_seed=world_seed,
                        sample_count=None,
                        positive_count=None,
                        metric="promoted",
                        value=1.0 if action == "PROMOTE" else 0.0,
                        artifact_path=str(self.run_dir / "promotion_history.json"),
                        json_path=f"[{idx}].decision",
                        git_sha=git_sha,
                        classification=ClaimClassification.MEASURED if action == "PROMOTE" else ClaimClassification.FAILURE_FINDING,
                    )
                )

        return records
