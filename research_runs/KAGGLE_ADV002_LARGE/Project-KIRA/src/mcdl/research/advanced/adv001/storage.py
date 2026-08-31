"""ADV-001 Storage and Checkpoint Management.

Handles streaming batch JSONL persistence, attack memory storage,
idempotent resume, and summary report generation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcdl.research.advanced.adv001.evaluator import AttackAttemptResult


class CheckpointManagerADV001:
    """Manages batch checkpointing, resume capability, and artifact writing for ADV-001."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.population_dir = self.output_dir / "population"
        self.population_dir.mkdir(parents=True, exist_ok=True)

    def get_completed_batch_indices(self) -> set[int]:
        """Scans population directory for existing completed batch files."""
        completed: set[int] = set()
        for f in self.population_dir.glob("batch_*.jsonl"):
            try:
                # Expected name: batch_0001.jsonl -> index 1
                parts = f.stem.split("_")
                if len(parts) >= 2 and parts[1].isdigit():
                    completed.add(int(parts[1]))
            except Exception:
                continue
        return completed

    def write_batch(self, batch_idx: int, results: list[AttackAttemptResult]) -> Path:
        """Writes a single batch of evaluated attacks to JSONL."""
        batch_file = self.population_dir / f"batch_{batch_idx:04d}.jsonl"
        with open(batch_file, "w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r.to_dict()) + "\n")
        return batch_file

    def read_all_results(self) -> list[AttackAttemptResult]:
        """Loads all results from completed batch files."""
        all_results: list[AttackAttemptResult] = []
        batch_files = sorted(self.population_dir.glob("batch_*.jsonl"))

        for bf in batch_files:
            with open(bf, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    all_results.append(
                        AttackAttemptResult(
                            attack_id=data["attack_id"],
                            family=data["family"],
                            strategy=data["strategy"],
                            seed=data["seed"],
                            parent_attack_id=data.get("parent_attack_id"),
                            query_budget=data["query_budget"],
                            queries_used=data["queries_used"],
                            mutation_count=data["mutation_count"],
                            perturbation_distance=data.get("perturbation_distance"),
                            target_transaction_id=data["target_transaction_id"],
                            blue_model_version=data["blue_model_version"],
                            blue_score=data["blue_score"],
                            blue_decision=data["blue_decision"],
                            evasion=data["evasion"],
                            outcome=data["outcome"],
                            timestamp=data["timestamp"],
                            provenance=data.get("provenance", {}),
                        )
                    )

        return all_results

    def save_final_artifacts(
        self,
        config: dict[str, Any],
        stats: dict[str, Any],
        comparison: dict[str, Any],
        provenance: dict[str, Any],
        evidence_md: str,
    ) -> None:
        """Persists consolidated metrics, attack memory, comparison table, and markdown report."""
        # 1. Config and Status
        (self.output_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
        (self.output_dir / "status.json").write_text(
            json.dumps({"status": "COMPLETED", "experiment_id": "ADV-001", "total_attempts": stats.get("total_attempts", 0)}, indent=2),
            encoding="utf-8",
        )

        # 2. Consolidated Attack Memory
        attack_memory_path = self.output_dir / "attack_memory.jsonl"
        all_results = self.read_all_results()
        with open(attack_memory_path, "w", encoding="utf-8") as f:
            for r in all_results:
                f.write(json.dumps(r.to_dict()) + "\n")

        # 3. Specific Metric Files
        (self.output_dir / "metrics.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
        (self.output_dir / "family_metrics.json").write_text(
            json.dumps(stats.get("family_metrics", {}), indent=2), encoding="utf-8"
        )
        (self.output_dir / "budget_metrics.json").write_text(
            json.dumps(stats.get("budget_metrics", {}), indent=2), encoding="utf-8"
        )
        (self.output_dir / "comparison_exp007a.json").write_text(
            json.dumps(comparison, indent=2), encoding="utf-8"
        )
        (self.output_dir / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
        (self.output_dir / "evidence.md").write_text(evidence_md, encoding="utf-8")
