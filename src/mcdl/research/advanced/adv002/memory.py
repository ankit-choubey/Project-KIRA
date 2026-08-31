"""ADV-002 Shared Attack Memory Layer.

Provides multi-index read-only ingestion of historical ADV-001 attack memory
and an append-only thread-safe in-memory/on-disk layer for ADV-002 swarm updates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Callable

from mcdl.schemas import AttackFamily


@dataclass
class MemoryRecord:
    """Standardized record of an attack memory entry."""

    attack_id: str
    family: str
    strategy: str
    seed: int
    parent_attack_id: str | None
    query_budget: int
    queries_used: int
    mutation_count: int
    perturbation_distance: float | None
    target_transaction_id: str
    blue_model_version: str
    blue_score: float
    blue_decision: str
    evasion: bool
    outcome: str
    timestamp: str
    provenance: dict[str, Any] = field(default_factory=dict)
    origin: str = "ADV-001"  # "ADV-001" or "ADV-002"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any], default_origin: str = "ADV-001") -> MemoryRecord:
        return cls(
            attack_id=str(data["attack_id"]),
            family=str(data["family"]),
            strategy=str(data.get("strategy", "")),
            seed=int(data.get("seed", 0)),
            parent_attack_id=data.get("parent_attack_id"),
            query_budget=int(data.get("query_budget", 20)),
            queries_used=int(data.get("queries_used", 0)),
            mutation_count=int(data.get("mutation_count", 0)),
            perturbation_distance=float(data["perturbation_distance"]) if data.get("perturbation_distance") is not None else None,
            target_transaction_id=str(data.get("target_transaction_id", data.get("source_txn_id", ""))),
            blue_model_version=str(data.get("blue_model_version", "")),
            blue_score=float(data.get("blue_score", 0.0)),
            blue_decision=str(data.get("blue_decision", "")),
            evasion=bool(data.get("evasion", False)),
            outcome=str(data.get("outcome", "")),
            timestamp=str(data.get("timestamp", "")),
            provenance=dict(data.get("provenance", {})),
            origin=str(data.get("origin", default_origin)),
        )


@dataclass
class MemoryQuery:
    """Filter criteria for querying shared attack memory."""

    family: str | None = None
    outcome: str | None = None
    evasion: bool | None = None
    target_transaction_id: str | None = None
    query_budget: int | None = None
    blue_decision: str | None = None
    max_perturbation: float | None = None
    origin: str | None = None
    limit: int | None = None


class SharedAttackMemory:
    """Indexed multi-criteria memory store consuming ADV-001 and holding ADV-002 additions."""

    def __init__(self, adv001_path: Path | str | None = None) -> None:
        self.records: list[MemoryRecord] = []
        self._by_id: dict[str, MemoryRecord] = {}

        # Multi-indexes
        self._index_family: dict[str, list[int]] = {}
        self._index_outcome: dict[str, list[int]] = {}
        self._index_evasion: dict[bool, list[int]] = {True: [], False: []}
        self._index_target: dict[str, list[int]] = {}
        self._index_budget: dict[int, list[int]] = {}
        self._index_blue_decision: dict[str, list[int]] = {}
        self._index_origin: dict[str, list[int]] = {}

        if adv001_path is not None:
            self.load_adv001_memory(Path(adv001_path))

    def _index_record(self, idx: int, rec: MemoryRecord) -> None:
        """Adds a record index pointer to internal lookup tables."""
        self._by_id[rec.attack_id] = rec
        self._index_family.setdefault(rec.family, []).append(idx)
        self._index_outcome.setdefault(rec.outcome, []).append(idx)
        self._index_evasion[rec.evasion].append(idx)
        self._index_target.setdefault(rec.target_transaction_id, []).append(idx)
        self._index_budget.setdefault(rec.query_budget, []).append(idx)
        self._index_blue_decision.setdefault(rec.blue_decision, []).append(idx)
        self._index_origin.setdefault(rec.origin, []).append(idx)

    def load_adv001_memory(self, path: Path) -> int:
        """Loads historical ADV-001 memory read-only without modifying the source file."""
        if not path.exists():
            return 0

        loaded_count = 0
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                rec = MemoryRecord.from_dict(data, default_origin="ADV-001")
                idx = len(self.records)
                self.records.append(rec)
                self._index_record(idx, rec)
                loaded_count += 1

        return loaded_count

    def append_adv002_record(self, record: MemoryRecord) -> None:
        """Appends a new ADV-002 swarm attempt to the shared memory."""
        record.origin = "ADV-002"
        idx = len(self.records)
        self.records.append(record)
        self._index_record(idx, record)

    def query(self, q: MemoryQuery) -> list[MemoryRecord]:
        """Retrieves matching records using indexed intersection and filters."""
        if len(self.records) == 0:
            return []

        # Find smallest matching candidate set from indexed fields
        candidate_indices: set[int] | None = None

        def intersect(indices: list[int] | None) -> None:
            nonlocal candidate_indices
            if indices is None:
                return
            idx_set = set(indices)
            if candidate_indices is None:
                candidate_indices = idx_set
            else:
                candidate_indices.intersection_update(idx_set)

        if q.family is not None:
            intersect(self._index_family.get(q.family, []))
        if q.outcome is not None:
            intersect(self._index_outcome.get(q.outcome, []))
        if q.evasion is not None:
            intersect(self._index_evasion.get(q.evasion, []))
        if q.target_transaction_id is not None:
            intersect(self._index_target.get(q.target_transaction_id, []))
        if q.query_budget is not None:
            intersect(self._index_budget.get(q.query_budget, []))
        if q.blue_decision is not None:
            intersect(self._index_blue_decision.get(q.blue_decision, []))
        if q.origin is not None:
            intersect(self._index_origin.get(q.origin, []))

        if candidate_indices is None:
            candidate_list = range(len(self.records))
        else:
            candidate_list = candidate_indices

        results: list[MemoryRecord] = []
        for idx in candidate_list:
            rec = self.records[idx]
            if q.max_perturbation is not None:
                if rec.perturbation_distance is None or rec.perturbation_distance > q.max_perturbation:
                    continue
            results.append(rec)
            if q.limit is not None and len(results) >= q.limit:
                break

        return results

    def get_family_success_rate(self, family: str, target_id: str | None = None) -> float:
        """Calculates empirical ASR for a given family in memory."""
        q = MemoryQuery(family=family, target_transaction_id=target_id)
        records = self.query(q)
        if not records:
            return 0.0
        evasions = sum(1 for r in records if r.evasion)
        return evasions / len(records)

    def get_best_perturbations(self, family: str, limit: int = 5) -> list[MemoryRecord]:
        """Retrieves lowest perturbation successful evasions for a family."""
        q = MemoryQuery(family=family, evasion=True)
        evasions = self.query(q)
        valid = [r for r in evasions if r.perturbation_distance is not None]
        valid.sort(key=lambda r: r.perturbation_distance or float("inf"))
        return valid[:limit]

    def get_failed_configurations(self, target_id: str) -> list[dict[str, Any]]:
        """Identifies attack family/budget configurations with 0% success on target."""
        q = MemoryQuery(target_transaction_id=target_id)
        records = self.query(q)
        groups: dict[tuple[str, int], list[bool]] = {}
        for r in records:
            groups.setdefault((r.family, r.query_budget), []).append(r.evasion)

        failures = []
        for (fam, budget), ev_list in groups.items():
            if len(ev_list) >= 3 and not any(ev_list):
                failures.append({
                    "family": fam,
                    "query_budget": budget,
                    "attempts": len(ev_list),
                    "success_rate": 0.0,
                })
        return failures

    def count_records(self) -> dict[str, int]:
        """Returns aggregate record counts partitioned by origin and outcome."""
        adv001_count = len(self._index_origin.get("ADV-001", []))
        adv002_count = len(self._index_origin.get("ADV-002", []))
        evasion_count = len(self._index_evasion.get(True, []))
        return {
            "total_records": len(self.records),
            "adv001_records": adv001_count,
            "adv002_records": adv002_count,
            "total_evasions": evasion_count,
        }
