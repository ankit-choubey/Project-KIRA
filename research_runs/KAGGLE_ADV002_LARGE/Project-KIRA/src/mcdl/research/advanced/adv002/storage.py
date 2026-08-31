"""ADV-002 Storage and Checkpoint Manager.

Handles atomic persistence of campaign states, round results, memory additions,
and final metric summaries.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcdl.research.advanced.adv002.campaign import CampaignState
from mcdl.research.advanced.adv002.evaluator import SwarmAttemptResult


class ADV002Storage:
    """Manages output serialization and atomic checkpointing for ADV-002."""

    def __init__(self, run_dir: Path | str) -> None:
        self.run_dir = Path(run_dir)
        self.campaigns_dir = self.run_dir / "campaigns"
        self.rounds_dir = self.run_dir / "rounds"
        self.memory_adv002_path = self.run_dir / "attack_memory_adv002.jsonl"
        self.status_path = self.run_dir / "status.json"

        self.campaigns_dir.mkdir(parents=True, exist_ok=True)
        self.rounds_dir.mkdir(parents=True, exist_ok=True)

    def write_json_atomic(self, path: Path, data: Any) -> None:
        """Writes JSON safely via a temporary file replacement."""
        tmp_path = path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        tmp_path.replace(path)

    def save_round_result(self, result: SwarmAttemptResult) -> None:
        """Appends a round result to ADV-002 memory file atomically."""
        with open(self.memory_adv002_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result.to_dict()) + "\n")

    def save_campaign_state(self, campaign: CampaignState) -> None:
        """Saves current state of a campaign."""
        path = self.campaigns_dir / f"{campaign.campaign_id}.json"
        self.write_json_atomic(path, campaign.to_dict())

    def get_completed_campaign_ids(self) -> set[str]:
        """Returns set of campaign IDs that are already completed."""
        completed = set()
        for p in self.campaigns_dir.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("is_completed", False):
                        completed.add(data.get("campaign_id", p.stem))
            except Exception:
                continue
        return completed

    def save_final_artifacts(
        self,
        config: dict[str, Any],
        metrics: dict[str, Any],
        adaptation_metrics: dict[str, Any],
        comparability: dict[str, Any],
        provenance: dict[str, Any],
    ) -> None:
        """Writes all final summary artifacts upon experiment completion."""
        self.write_json_atomic(self.run_dir / "config.json", config)
        self.write_json_atomic(self.run_dir / "metrics.json", metrics)
        self.write_json_atomic(self.run_dir / "adaptation_metrics.json", adaptation_metrics)
        self.write_json_atomic(self.run_dir / "comparability_adv001.json", comparability)
        self.write_json_atomic(self.run_dir / "provenance.json", provenance)

        status_data = {
            "status": "COMPLETED",
            "experiment_id": "ADV-002",
            "total_attacks": metrics.get("total_attacks", 0),
            "aggregate_asr": metrics.get("aggregate_asr", 0.0),
        }
        self.write_json_atomic(self.status_path, status_data)

    def save_integrity(self, integrity_data: dict[str, Any]) -> None:
        """Saves integrity validation artifact."""
        self.write_json_atomic(self.run_dir / "integrity.json", integrity_data)
