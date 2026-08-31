import hashlib
import json
import logging
import os
import time
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

PHASE2_DIR = Path("research_runs/PHASE2")

VALID_STATES = {
    "NOT_STARTED",
    "RUNNING",
    "COMPLETED",
    "FAILED",
    "TIMEOUT",
    "OOM",
    "SKIPPED",
    "INCONCLUSIVE"
}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


class StageTimeout(Exception):
    pass


class CheckpointManager:
    def __init__(self, run_id: str, git_commit: str, baseline_run_id: str, baseline_git_commit: str):
        self.run_id = run_id
        self.git_commit = git_commit
        self.baseline_run_id = baseline_run_id
        self.baseline_git_commit = baseline_git_commit
        self.state_file = PHASE2_DIR / "state.json"
        self.global_start = time.monotonic()

    def get_state(self, stage_id: str) -> str:
        state = load_json(self.state_file)
        return state.get(stage_id, "NOT_STARTED")

    def update_state(self, stage_id: str, status: str, reason: Optional[str] = None, traceback_str: Optional[str] = None):
        if status not in VALID_STATES:
            raise ValueError(f"Invalid state: {status}")
        
        state = load_json(self.state_file)
        state[stage_id] = status
        
        if reason:
            state[f"{stage_id}_reason"] = reason
        if traceback_str:
            state[f"{stage_id}_traceback"] = traceback_str
            
        save_json(self.state_file, state)

    def write_provenance(self, stage_id: str, stage_dir: Path, inputs: Dict[str, str], env: dict, libs: dict):
        prov = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "notebook_version": 1,
            "notebook_git_commit": self.git_commit,
            "baseline_run_id": self.baseline_run_id,
            "baseline_git_commit": self.baseline_git_commit,
            "input_datasets": inputs,
            "library_versions": libs,
            "environment": env,
            "namespace": "RESEARCH_PHASE2"
        }
        save_json(stage_dir / "provenance.json", prov)

    def write_artifact(self, stage_id: str, start_time: float, metrics: dict, inputs: Dict[str, str], output_paths: list[str], status: str = "COMPLETED", exception: Optional[str] = None):
        stage_dir = PHASE2_DIR / stage_id
        
        output_sha256 = {}
        for p in output_paths:
            path = Path(p)
            if path.exists():
                output_sha256[path.name] = sha256_file(path)

        artifact = {
            "experiment_id": stage_id,
            "run_id": self.run_id,
            "git_commit": self.git_commit,
            "baseline_run_id": self.baseline_run_id,
            "baseline_git_commit": self.baseline_git_commit,
            "seed": 20260827,
            "stage_id": stage_id,
            "status": status,
            "start_time": datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat(),
            "runtime_sec": time.monotonic() - start_time,
            "peak_ram_mb": 0, # Will be filled if psutil available
            "peak_gpu_mb": 0, # Will be filled if torch available
            "config_hash": "", # To be filled by caller
            "input_artifact_hashes": inputs,
            "output_paths": output_paths,
            "output_sha256": output_sha256,
            "metrics": metrics,
            "exception": exception,
            "termination_reason": exception if exception else None
        }
        save_json(stage_dir / "status.json", artifact)


class StageExecution:
    def __init__(self, manager: CheckpointManager, stage_id: str, budget_seconds: int, allow_retry: bool = False):
        self.manager = manager
        self.stage_id = stage_id
        self.budget_seconds = budget_seconds
        self.allow_retry = allow_retry
        self.start_time = time.monotonic()
        self.should_skip = False

    def __enter__(self):
        status = self.manager.get_state(self.stage_id)
        if status == "COMPLETED":
            logger.info(f"{self.stage_id}: Already complete, skipping.")
            self.should_skip = True
            return self
        
        if status in ("FAILED", "TIMEOUT", "OOM"):
            state = load_json(self.manager.state_file)
            if self.allow_retry and not state.get(f"{self.stage_id}_retried"):
                state[f"{self.stage_id}_retried"] = True
                save_json(self.manager.state_file, state)
                logger.info(f"{self.stage_id}: Retrying failed stage.")
            else:
                logger.info(f"{self.stage_id}: Previously failed, not retrying. SKIPPED.")
                self.should_skip = True
                return self
        
        self.manager.update_state(self.stage_id, "RUNNING")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.should_skip:
            return True
            
        if exc_type is None:
            self.manager.update_state(self.stage_id, "COMPLETED")
        elif exc_type is TimeoutError or exc_type is StageTimeout:
            self.manager.update_state(self.stage_id, "TIMEOUT", reason="wall_clock_exceeded")
            logger.error(f"{self.stage_id} TIMEOUT")
        elif exc_type is MemoryError:
            self.manager.update_state(self.stage_id, "OOM", reason="memory_exceeded")
            logger.error(f"{self.stage_id} OOM")
        else:
            tb_str = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
            self.manager.update_state(self.stage_id, "FAILED", reason=str(exc_val), traceback_str=tb_str)
            logger.error(f"{self.stage_id} FAILED: {exc_val}")
        
        # We do not suppress exceptions if they are real errors (so notebook stops)
        # But for failure isolation, we can suppress it if we want subsequent stages to check dependencies.
        # The prompt says: "A failed independent stage must not crash the whole notebook. Dependencies must be checked."
        # So we suppress the exception here.
        return True


class SkipStage(Exception):
    pass
