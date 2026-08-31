"""Unit tests for atomic checkpointing and RNG state preservation."""

import json
from mcdl.research.checkpoint import (
    atomic_write_json,
    atomic_write_text,
    capture_rng_state,
    restore_rng_state,
    save_stage_checkpoint,
)
import numpy as np


def test_atomic_write_json(tmp_path):
    target = tmp_path / "test.json"
    data = {"key": "value", "count": 42}
    atomic_write_json(target, data)
    
    assert target.exists()
    assert json.loads(target.read_text(encoding="utf-8")) == data


def test_atomic_write_text(tmp_path):
    target = tmp_path / "test.txt"
    text = "Hello world"
    atomic_write_text(target, text)
    
    assert target.exists()
    assert target.read_text(encoding="utf-8") == text


def test_rng_state_capture_restore():
    state = capture_rng_state()
    val1 = np.random.rand()
    
    restore_rng_state(state)
    val2 = np.random.rand()
    assert val1 == val2


def test_save_stage_checkpoint(tmp_path):
    stage_dir = tmp_path / "S-01"
    status = {"stage_id": "S-01", "status": "COMPLETE"}
    metrics = {"pr_auc": 0.95}
    save_stage_checkpoint(stage_dir, "S-01", "RES-01", status, metrics)
    
    assert (stage_dir / "status.json").exists()
    assert (stage_dir / "metrics.json").exists()
