"""Evidence normalization and claim validation package."""

from mcdl.evidence.schema import ClaimClassification, EvidenceRecord, MetricConflict
from mcdl.evidence.adapter import EvidenceAdapter
from mcdl.evidence.conflicts import ConflictDetector

__all__ = [
    "ClaimClassification",
    "EvidenceRecord",
    "MetricConflict",
    "EvidenceAdapter",
    "ConflictDetector",
]
