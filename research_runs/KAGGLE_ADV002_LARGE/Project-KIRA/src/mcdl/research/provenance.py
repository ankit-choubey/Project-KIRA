"""Dataset Provenance & Namespace Enforcement.

Ensures strict namespace separation (SYNTHETIC vs REAL_WORLD vs INFERRED),
computes cryptographic hashes for datasets and artifacts, and prevents silent leakage.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class Namespace(str, Enum):
    SYNTHETIC = "SYNTHETIC"
    REAL_WORLD = "REAL_WORLD"
    INFERRED = "INFERRED"


def compute_file_sha256(path: Path | str) -> str:
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_bytes_sha256(data: bytes) -> str:
    """Computes SHA-256 hash of bytes in memory."""
    return hashlib.sha256(data).hexdigest()


def create_dataset_provenance(
    dataset_name: str,
    source_url: str,
    license_type: str,
    namespace: Namespace | str,
    sample_count: int,
    positive_count: int,
    split_method: str,
    file_path: Optional[Path | str] = None,
    extra_metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Builds a standardized provenance record for any dataset used in research."""
    namespace_str = str(namespace.value if isinstance(namespace, Namespace) else namespace)
    if namespace_str not in [n.value for n in Namespace]:
        raise ValueError(f"Invalid namespace: {namespace_str}")

    content_hash = compute_file_sha256(file_path) if file_path and Path(file_path).exists() else "UNAVAILABLE_LOCAL"

    meta = {
        "dataset_name": dataset_name,
        "source_url": source_url,
        "license": license_type,
        "access_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "sha256_content_hash": content_hash,
        "namespace": namespace_str,
        "sample_count": sample_count,
        "positive_count": positive_count,
        "fraud_rate": round(positive_count / max(1, sample_count), 6),
        "split_method": split_method,
    }
    if extra_metadata:
        meta.update(extra_metadata)
    return meta
