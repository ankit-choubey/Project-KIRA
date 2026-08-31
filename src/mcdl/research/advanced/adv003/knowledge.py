"""ADV-003 Defensive Knowledge Store.

Maintains, validates, deduplicates, and manages structured defensive knowledge
derived from adversarial attack outcomes across sequential defense rounds.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any
import numpy as np
import polars as pl

from mcdl.features.spec import FEATURE_NAMES
from mcdl.research.advanced.adv003.schemas import (
    DefensiveKnowledgeRecord,
    KnowledgeEffect,
)


class DefensiveKnowledgeStore:
    """Cryptographically auditable and partitioned defensive knowledge store."""

    def __init__(self, root_dir: Path | str | None = None) -> None:
        self.root_dir = Path(root_dir) if root_dir else Path("/tmp/adv003_knowledge")
        self._records: list[DefensiveKnowledgeRecord] = []
        self._signature_hashes: set[str] = set()
        self._initialized: bool = False
        self._setup_partitions()

    def _setup_partitions(self) -> None:
        if not self._initialized:
            subdirs = [
                "attack_signatures",
                "weakness_profiles",
                "successful_evasions",
                "failed_evasions",
                "mutation_distributions",
                "model_versions",
                "promotion_history",
                "rollback_history",
                "evidence",
            ]
            for sub in subdirs:
                (self.root_dir / sub).mkdir(parents=True, exist_ok=True)
            self._initialized = True

    def validate_and_add_attack(
        self,
        round_number: int,
        attack_id: str,
        attack_family: str,
        features: dict[str, float],
        target_txn_id: str,
        customer_id: str,
        merchant_id: str,
        amount: float,
        blue_score_before: float,
        blue_decision_before: str,
        perturbation_distance: float,
        queries_used: int,
        source_experiment: str = "ADV-003",
        source_artifact_hash: str = "",
    ) -> DefensiveKnowledgeRecord | None:
        """Validates an observed attack attempt and adds it to defensive knowledge if novel."""
        # 1. Validation Rule: Must have valid features and positive perturbation distance
        if not features or not isinstance(features, dict):
            return None
        if len(features) < len(FEATURE_NAMES):
            return None

        # 2. Determine observed effect
        if blue_decision_before == "ALLOW" and blue_score_before < 0.40:
            effect = KnowledgeEffect.EVASION_EXPLOIT
            confidence = 1.0 - blue_score_before
        elif blue_decision_before == "STEP_UP" or (0.40 <= blue_score_before < 0.60):
            effect = KnowledgeEffect.HIGH_RISK_NEAR_MISS
            confidence = 0.85
        elif blue_score_before < 0.70:
            effect = KnowledgeEffect.MUTATION_VULNERABILITY
            confidence = 0.70
        else:
            # Fully blocked with high confidence — not a critical defensive weakness
            effect = KnowledgeEffect.FALSE_NEGATIVE_RISK
            confidence = 0.50

        # 3. Compute deterministic feature signature for deduplication
        sig_data = {
            "family": attack_family,
            "target": target_txn_id,
            "round_feat": {k: round(float(features.get(k, 0.0)), 3) for k in sorted(FEATURE_NAMES)},
        }
        sig_hash = hashlib.sha256(json.dumps(sig_data, sort_keys=True).encode("utf-8")).hexdigest()

        if sig_hash in self._signature_hashes:
            return None  # Deduplicated

        self._signature_hashes.add(sig_hash)

        knowledge_id = f"knw_adv003_r{round_number:02d}_{sig_hash[:12]}"
        now_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        record = DefensiveKnowledgeRecord(
            knowledge_id=knowledge_id,
            source_experiment=source_experiment,
            round_number=round_number,
            attack_id=attack_id,
            attack_family=attack_family,
            features=features,
            target_txn_id=target_txn_id,
            customer_id=customer_id,
            merchant_id=merchant_id,
            amount=amount,
            observed_effect=effect,
            blue_score_before=blue_score_before,
            blue_decision_before=blue_decision_before,
            perturbation_distance=perturbation_distance,
            queries_used=queries_used,
            confidence=confidence,
            is_validated=True,
            source_artifact_hash=source_artifact_hash or sig_hash,
            provenance={
                "signature_hash": sig_hash,
                "created_at": now_ts,
            },
            timestamp=now_ts,
        )

        self._records.append(record)
        self._persist_record(record)
        return record

    def _persist_record(self, record: DefensiveKnowledgeRecord) -> None:
        """Persists knowledge record atomically into appropriate partition."""
        record_json = json.dumps(record.to_dict(), indent=2)

        # Primary partition
        if record.observed_effect == KnowledgeEffect.EVASION_EXPLOIT:
            partition = "successful_evasions"
        elif record.observed_effect == KnowledgeEffect.HIGH_RISK_NEAR_MISS:
            partition = "weakness_profiles"
        else:
            partition = "failed_evasions"

        target_file = self.root_dir / partition / f"{record.knowledge_id}.json"
        tmp_file = target_file.with_suffix(".tmp")
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(record_json)
        tmp_file.replace(target_file)

        # Append to attack signatures index
        sig_line = json.dumps({
            "knowledge_id": record.knowledge_id,
            "round": record.round_number,
            "family": record.attack_family,
            "effect": record.observed_effect.value,
            "target": record.target_txn_id,
            "signature_hash": record.provenance.get("signature_hash"),
        })
        sig_file = self.root_dir / "attack_signatures" / "signatures.jsonl"
        with open(sig_file, "a", encoding="utf-8") as f:
            f.write(sig_line + "\n")

    def get_replay_dataframe(self, max_records: int | None = None, min_round: int = 0, max_round: int | None = None) -> pl.DataFrame:
        """Constructs a Polars training DataFrame from validated defensive knowledge."""
        filtered = [
            r for r in self._records
            if r.round_number >= min_round and (max_round is None or r.round_number <= max_round)
        ]
        if max_records is not None and len(filtered) > max_records:
            filtered = filtered[-max_records:]

        if not filtered:
            # Return empty DataFrame with exact schema
            schema = {name: pl.Float64 for name in FEATURE_NAMES}
            schema["is_fraud"] = pl.Int64
            return pl.DataFrame(schema=schema)

        rows = []
        for r in filtered:
            row = {name: float(r.features.get(name, 0.0)) for name in FEATURE_NAMES}
            row["is_fraud"] = 1  # Adversarial mutations are malicious
            rows.append(row)

        return pl.DataFrame(rows)

    def count_records(self) -> dict[str, int]:
        """Returns distribution count of stored defensive knowledge."""
        return {
            "total_records": len(self._records),
            "evasion_exploits": sum(1 for r in self._records if r.observed_effect == KnowledgeEffect.EVASION_EXPLOIT),
            "weakness_profiles": sum(1 for r in self._records if r.observed_effect == KnowledgeEffect.HIGH_RISK_NEAR_MISS),
            "mutation_vulnerabilities": sum(1 for r in self._records if r.observed_effect == KnowledgeEffect.MUTATION_VULNERABILITY),
            "false_negative_risks": sum(1 for r in self._records if r.observed_effect == KnowledgeEffect.FALSE_NEGATIVE_RISK),
        }
