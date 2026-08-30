"""Replay Buffer for Hardening Challenger Blue Models.

Stores and indexes successful Red evasions eligible for re-training.
Ensures strict provenance preservation and zero feature-metadata leakage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import numpy as np
from mcdl.features.spec import FEATURE_NAMES
from mcdl.schemas import AttackFamily, Decision, Transaction


@dataclass
class ReplayRecord:
    """Full provenance for a replayed successful Red evasion."""
    attack_instance_id: str
    attack_family: AttackFamily
    source_txn_id: str
    round_generated: int
    evasion_features: dict[str, float]
    original_risk: float
    evasion_risk: float
    original_decision: Decision
    evasion_decision: Decision
    med: float
    query_budget: int
    seed: int
    candidate_transaction: Transaction
    parent_variant_id: str | None = None
    priority_score: float = 1.0
    failure_record: Any | None = None


class ReplayBuffer:
    """Persistent replay store for adversarial training examples with prioritized sampling."""

    def __init__(self, capacity: int = 5000) -> None:
        self.capacity = capacity
        self._records: dict[str, ReplayRecord] = {}

    def add(self, record: ReplayRecord) -> bool:
        """Adds a record if not already present. Returns True if newly added."""
        if record.attack_instance_id in self._records:
            return False
        if len(self._records) >= self.capacity:
            # Evict lowest priority record
            lowest_id = min(self._records.keys(), key=lambda k: self._records[k].priority_score)
            del self._records[lowest_id]

        self._records[record.attack_instance_id] = record
        return True

    def get_all(self) -> list[ReplayRecord]:
        """Returns all replayed records in deterministic order."""
        return sorted(self._records.values(), key=lambda r: r.attack_instance_id)

    def filter_by_round(self, round_idx: int) -> list[ReplayRecord]:
        """Filters replayed records generated in a specific round."""
        return [r for r in self.get_all() if r.round_generated == round_idx]

    def filter_by_family(self, family: AttackFamily) -> list[ReplayRecord]:
        """Filters replayed records by attack family."""
        return [r for r in self.get_all() if r.attack_family == family]

    def sample_prioritized(self, k: int, seed: int = 20260827) -> list[ReplayRecord]:
        """Samples up to k records with probability proportional to priority_score."""
        records = self.get_all()
        if not records:
            return []
        if len(records) <= k:
            return records

        rng = np.random.default_rng(seed)
        priorities = np.array([max(1e-4, r.priority_score) for r in records], dtype=np.float64)
        probs = priorities / np.sum(priorities)

        indices = rng.choice(len(records), size=k, replace=False, p=probs)
        return [records[i] for i in sorted(indices)]

    def to_feature_rows(self, max_records: int | None = None, seed: int = 20260827) -> list[dict[str, Any]]:
        """Converts replay records into strictly observable feature rows with is_fraud=True.

        Excludes all provenance and metadata fields (attack_family, med, seed, priority, etc.).
        """
        if max_records is not None and max_records < len(self._records):
            records = self.sample_prioritized(max_records, seed=seed)
        else:
            records = self.get_all()

        rows = []
        for r in records:
            row = {f: float(r.evasion_features.get(f, 0.0)) for f in FEATURE_NAMES}
            row["is_fraud"] = True
            rows.append(row)
        return rows

    def __len__(self) -> int:
        return len(self._records)
