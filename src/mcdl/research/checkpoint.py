"""Atomic Checkpointing & Artifact Serialization.

Ensures atomic writes via temporary files so partial crashes never corrupt
checkpoints or status records.
"""

from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Any, Optional
import numpy as np


def atomic_write_json(path: Path | str, data: Any, indent: int = 2) -> None:
    """Writes JSON payload atomically using a temporary file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target.parent / f".tmp_{target.name}_{os.getpid()}"
    
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)
    
    os.replace(temp_path, target)


def atomic_write_text(path: Path | str, text: str) -> None:
    """Writes text payload atomically using a temporary file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target.parent / f".tmp_{target.name}_{os.getpid()}"
    
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    os.replace(temp_path, target)


def capture_rng_state() -> dict[str, Any]:
    """Captures current Python and NumPy RNG state for checkpointing."""
    return {
        "python_rng": random.getstate(),
        "numpy_rng": np.random.get_state(),
    }


def restore_rng_state(state_dict: dict[str, Any]) -> None:
    """Restores Python and NumPy RNG state from a checkpoint."""
    if "python_rng" in state_dict:
        random.setstate(state_dict["python_rng"])
    if "numpy_rng" in state_dict:
        # numpy state tuple conversion
        np_state = state_dict["numpy_rng"]
        if isinstance(np_state, list) and len(np_state) == 5:
            np_state = (
                str(np_state[0]),
                np.array(np_state[1], dtype=np.uint32),
                int(np_state[2]),
                int(np_state[3]),
                float(np_state[4]),
            )
        np.random.set_state(np_state)


def save_stage_checkpoint(
    stage_dir: Path | str,
    stage_id: str,
    experiment_id: str,
    status_data: dict[str, Any],
    metrics_data: Optional[dict[str, Any]] = None,
    config_data: Optional[dict[str, Any]] = None,
) -> None:
    """Persists stage records atomically into target directory."""
    s_dir = Path(stage_dir)
    s_dir.mkdir(parents=True, exist_ok=True)
    
    atomic_write_json(s_dir / "status.json", status_data)
    if metrics_data is not None:
        atomic_write_json(s_dir / "metrics.json", metrics_data)
    if config_data is not None:
        atomic_write_json(s_dir / "config.json", config_data)
