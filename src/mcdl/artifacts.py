"""Reading and writing run artifacts.

One rule enforced here: a metric that is not in a file under `artifacts/<run_id>/`
does not exist. The API, the gates, the brain updater and the report all read
through this module, so there is exactly one definition of "the current run".
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

from mcdl.config import REPO_ROOT, Config, artifacts_dir
from mcdl.schemas import BlueDecision, EvaluationResult, RunManifest, Transaction

LATEST_POINTER = "LATEST"


def new_run_id(prefix: str = "run") -> str:
    return f"{prefix}_{datetime.now():%Y%m%d_%H%M%S}"


def git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def make_manifest(cfg: Config, run_id: str, seed: int | None = None) -> RunManifest:
    return RunManifest(
        run_id=run_id,
        created_at=datetime.now(),
        git_commit=git_commit(),
        config_hash=cfg.hash,
        seed=seed if seed is not None else cfg["seed"],
        scale=cfg["scale"],
        is_fixture=False,
    )


def run_dir(run_id: str, base: Path | None = None) -> Path:
    return (base or artifacts_dir()) / run_id


def resolve_run(run_id: str | None = None, base: Path | None = None) -> Path:
    """Resolve a run id, or follow the LATEST pointer.

    Raises with an actionable message rather than a KeyError three frames later.
    """
    base = base or artifacts_dir()
    if run_id:
        d = base / run_id
        if not d.is_dir():
            raise FileNotFoundError(f"no such run: {d}")
        return d

    pointer = base / LATEST_POINTER
    if not pointer.exists():
        raise FileNotFoundError(
            f"no {LATEST_POINTER} pointer in {base}. Run `make gate 0` to write fixtures, "
            "or `make run SCALE=tiny` for a real run."
        )
    return base / pointer.read_text(encoding="utf-8").strip()


def list_runs(base: Path | None = None) -> list[str]:
    base = base or artifacts_dir()
    return sorted(
        (p.name for p in base.iterdir() if p.is_dir() and (p / "manifest.json").exists()),
        reverse=True,
    )


def set_latest(run_id: str, base: Path | None = None) -> None:
    (base or artifacts_dir()).joinpath(LATEST_POINTER).write_text(run_id, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Typed loaders
# --------------------------------------------------------------------------- #


def load_manifest(d: Path) -> RunManifest:
    return RunManifest.model_validate_json((d / "manifest.json").read_text(encoding="utf-8"))


def load_evaluation(d: Path) -> EvaluationResult:
    return EvaluationResult.model_validate_json((d / "evaluation.json").read_text(encoding="utf-8"))


def load_transactions(d: Path, limit: int | None = None, offset: int = 0) -> list[Transaction]:
    rows = json.loads((d / "transactions.json").read_text(encoding="utf-8"))
    rows = rows[offset : offset + limit] if limit else rows[offset:]
    return [Transaction.model_validate(r) for r in rows]


def load_decisions(d: Path) -> dict[str, BlueDecision]:
    rows = json.loads((d / "decisions.json").read_text(encoding="utf-8"))
    return {r["txn_id"]: BlueDecision.model_validate(r) for r in rows}


def write_evaluation(d: Path, result: EvaluationResult) -> None:
    d.mkdir(parents=True, exist_ok=True)
    (d / "evaluation.json").write_text(result.model_dump_json(indent=2), encoding="utf-8")
    (d / "manifest.json").write_text(result.manifest.model_dump_json(indent=2), encoding="utf-8")
