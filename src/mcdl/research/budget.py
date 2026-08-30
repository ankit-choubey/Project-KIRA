"""Hard Resource Controls & Execution Budgeting.

Provides BudgetContext, GlobalBudget, StageTimeoutError, kill-switch detection,
and stage status lifecycle tracking for research expansion.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class StageTimeoutError(TimeoutError):
    """Raised when a research stage exceeds its allotted wall-clock budget."""

    def __init__(self, stage_id: str, elapsed_seconds: float, limit_seconds: float):
        super().__init__(
            f"Stage {stage_id} timed out after {elapsed_seconds:.2f}s "
            f"(limit: {limit_seconds:.2f}s)"
        )
        self.stage_id = stage_id
        self.elapsed_seconds = elapsed_seconds
        self.limit_seconds = limit_seconds


class KillSwitchTriggered(SystemExit):
    """Raised when the research_runs/STOP kill switch file is detected."""


# Default Wave 1 limits (in seconds)
WAVE_1_LIMITS: dict[str, int] = {
    "S-00": 600,   # 10 min
    "S-01": 300,   #  5 min
    "S-02": 1500,  # 25 min
    "S-03": 1200,  # 20 min
    "S-04": 1200,  # 20 min
    "S-05": 600,   # 10 min
    "WAVE_1_TOTAL": 5400,  # 90 min max
}

GLOBAL_WAVE_2_MAX_SECONDS: int = 28800  # 8 hours


def check_kill_switch(stop_file_path: Path | str = "research_runs/STOP") -> bool:
    """Checks if the emergency kill-switch file is present.
    
    If present, creates ABORT_REASON.txt and raises KillSwitchTriggered.
    """
    path = Path(stop_file_path)
    if path.exists():
        abort_file = path.parent / "ABORT_REASON.txt"
        abort_file.write_text(
            f"Kill switch activated via {path} at {datetime.now(timezone.utc).isoformat()}",
            encoding="utf-8",
        )
        raise KillSwitchTriggered(f"Emergency stop triggered by file: {path}")
    return False


class BudgetContext:
    """Context manager that tracks wall-clock execution for a single stage."""

    def __init__(
        self,
        stage_id: str,
        limit_seconds: Optional[float] = None,
        stop_file_path: Path | str = "research_runs/STOP",
    ):
        self.stage_id = stage_id
        self.limit_seconds = limit_seconds or WAVE_1_LIMITS.get(stage_id, 1200)
        self.stop_file_path = stop_file_path
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.started_at_iso: str = ""
        self.ended_at_iso: str = ""
        self.status: str = "PENDING"
        self.truncation_reason: Optional[str] = None

    def __enter__(self) -> "BudgetContext":
        check_kill_switch(self.stop_file_path)
        self.start_time = time.monotonic()
        self.started_at_iso = datetime.now(timezone.utc).isoformat()
        self.status = "RUNNING"
        return self

    def check_budget(self) -> None:
        """Pollable check to verify within limits during long loops."""
        check_kill_switch(self.stop_file_path)
        elapsed = time.monotonic() - self.start_time
        if elapsed > self.limit_seconds:
            self.status = "INCOMPLETE"
            self.truncation_reason = (
                f"Stage exceeded wall-clock limit of {self.limit_seconds:.1f}s (elapsed: {elapsed:.1f}s)"
            )
            raise StageTimeoutError(self.stage_id, elapsed, self.limit_seconds)

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        self.end_time = time.monotonic()
        self.ended_at_iso = datetime.now(timezone.utc).isoformat()
        
        if exc_type is None:
            self.status = "COMPLETE"
        elif issubclass(exc_type, StageTimeoutError):
            self.status = "INCOMPLETE"
            self.truncation_reason = str(exc_val)
            return True  # Handled safely
        elif issubclass(exc_type, KillSwitchTriggered):
            self.status = "KILLED"
            self.truncation_reason = str(exc_val)
            return False
        else:
            self.status = "FAILED"
            self.truncation_reason = f"{exc_type.__name__}: {str(exc_val)}"
            return False

    @property
    def elapsed_seconds(self) -> float:
        if self.start_time == 0.0:
            return 0.0
        end = self.end_time if self.end_time > 0.0 else time.monotonic()
        return round(end - self.start_time, 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "status": self.status,
            "wall_clock_seconds": self.elapsed_seconds,
            "budget_limit_seconds": self.limit_seconds,
            "started_at": self.started_at_iso,
            "ended_at": self.ended_at_iso,
            "truncation_reason": self.truncation_reason,
        }


class GlobalBudget:
    """Tracks cumulative wall-clock budget across multiple stages."""

    def __init__(self, max_seconds: float = 5400.0, stop_file: str = "research_runs/STOP"):
        self.max_seconds = max_seconds
        self.stop_file = stop_file
        self.start_time = time.monotonic()
        self.started_at = datetime.now(timezone.utc).isoformat()

    def check(self) -> None:
        check_kill_switch(self.stop_file)
        elapsed = time.monotonic() - self.start_time
        if elapsed > self.max_seconds:
            raise StageTimeoutError("GLOBAL", elapsed, self.max_seconds)

    @property
    def elapsed_seconds(self) -> float:
        return round(time.monotonic() - self.start_time, 4)
