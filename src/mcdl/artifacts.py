"""Reading, writing, hashing, and validating run artifacts.

One rule enforced here: a metric that is not in a file under `artifacts/<run_id>/`
does not exist. The API, the gates, the brain updater, and the report all read
through this module, so there is exactly one definition of "the current run".
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from mcdl.config import REPO_ROOT, Config, artifacts_dir
from mcdl.features.spec import FEATURE_NAMES, get_feature_schema
from mcdl.evaluation.anchor import get_external_anchor_metadata
from mcdl.schemas import (
    BlueDecision,
    BlueMetrics,
    EvaluationResult,
    RedMetrics,
    RoundResult,
    RunManifest,
    Transaction,
)

LATEST_POINTER = "LATEST"
FINALIZED_MARKER = ".finalized"


def new_run_id(prefix: str = "run") -> str:
    """Generates a timestamped run ID."""
    return f"{prefix}_{datetime.now():%Y%m%d_%H%M%S}"


def deterministic_run_id(scale: str, seed: int, config_hash: str, commit: str | None = None) -> str:
    """Generates a deterministic run ID derived from configuration, seed, and git commit."""
    c_hash = (config_hash or "00000000")[:8]
    c_commit = (commit or git_commit() or "0000000")[:7]
    return f"run_{scale}_s{seed}_{c_hash}_{c_commit}"


def git_commit() -> str:
    """Retrieves the current git commit hash."""
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


def canonical_json_dumps(obj: Any) -> str:
    """Canonical JSON serialization: sorted keys, UTF-8, standardized indentation."""
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)


def make_manifest(cfg: Config, run_id: str, seed: int | None = None) -> RunManifest:
    """Creates a new RunManifest recording git commit and configuration hash."""
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
    """Returns the path to a specific run directory."""
    return (base or artifacts_dir()) / run_id


def is_run_finalized(d: Path) -> bool:
    """Checks if a run has been marked as finalized/immutable."""
    return (d / FINALIZED_MARKER).exists()


def mark_run_finalized(d: Path) -> None:
    """Marks a run as finalized to prevent accidental overwrite."""
    (d / FINALIZED_MARKER).write_text(datetime.now().isoformat(), encoding="utf-8")


def resolve_run(run_id: str | None = None, base: Path | None = None) -> Path:
    """Resolve a run id, or follow the LATEST pointer."""
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
    """Lists all available runs with manifests."""
    base = base or artifacts_dir()
    if not base.exists():
        return []
    return sorted(
        (p.name for p in base.iterdir() if p.is_dir() and (p / "manifest.json").exists()),
        reverse=True,
    )


def set_latest(run_id: str, base: Path | None = None) -> None:
    """Updates the LATEST run pointer."""
    (base or artifacts_dir()).joinpath(LATEST_POINTER).write_text(run_id, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Hashing & Integrity
# --------------------------------------------------------------------------- #


def calculate_sha256(file_path: Path) -> str:
    """Computes the SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_provenance_manifest(d: Path) -> dict[str, Any]:
    """Calculates SHA-256 hashes for all generated JSON and Markdown artifacts."""
    artifacts: dict[str, dict[str, Any]] = {}
    for p in sorted(d.iterdir()):
        if p.name in ("provenance.json", "LATEST", FINALIZED_MARKER):
            continue
        if p.is_file():
            artifacts[p.name] = {
                "size_bytes": p.stat().st_size,
                "sha256": calculate_sha256(p),
                "schema_version": "0.1.0",
            }
    return {
        "schema_version": "0.1.0",
        "generated_at": datetime.now().isoformat(),
        "run_id": d.name,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }


def verify_run_integrity(d: Path) -> tuple[bool, list[str]]:
    """Verifies that all files in provenance.json match their recorded SHA-256 hashes."""
    prov_file = d / "provenance.json"
    if not prov_file.exists():
        return False, ["MISSING_PROVENANCE_JSON"]

    try:
        prov = json.loads(prov_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [f"CORRUPT_PROVENANCE_JSON: {exc}"]

    errors = []

    for name, meta in prov.get("artifacts", {}).items():
        file_path = d / name
        if not file_path.exists():
            errors.append(f"MISSING_ARTIFACT:{name}")
            continue
        actual_hash = calculate_sha256(file_path)
        if actual_hash != meta["sha256"]:
            errors.append(f"HASH_MISMATCH:{name} (expected={meta['sha256'][:8]} actual={actual_hash[:8]})")

    return len(errors) == 0, errors


# --------------------------------------------------------------------------- #
# Typed loaders & writers
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
    """Writes the master evaluation and manifest artifacts."""
    d.mkdir(parents=True, exist_ok=True)
    (d / "evaluation.json").write_text(canonical_json_dumps(json.loads(result.model_dump_json())), encoding="utf-8")
    (d / "manifest.json").write_text(canonical_json_dumps(json.loads(result.manifest.model_dump_json())), encoding="utf-8")


def write_granular_artifacts(
    d: Path,
    evaluation: EvaluationResult,
    transactions: list[Transaction],
    decisions: list[BlueDecision],
    world_summary: dict[str, Any],
    coevolution_reports: list[dict[str, Any]],
    attack_summary: dict[str, Any],
    sample_txns_with_shap: list[dict[str, Any]],
    calibration_data: dict[str, Any] | None = None,
    evidence_pack_md: str | None = None,
    overwrite: bool = False,
    **kwargs: Any,
) -> None:
    """Writes all individual domain-specific artifacts and generates provenance checksums."""
    if is_run_finalized(d) and not overwrite:
        raise PermissionError(f"Run {d.name} is finalized. Overwrite is refused.")

    d.mkdir(parents=True, exist_ok=True)

    # 1. Master Evaluation & Manifest
    write_evaluation(d, evaluation)

    # 2. World Summary
    (d / "world_summary.json").write_text(canonical_json_dumps(world_summary), encoding="utf-8")

    # 3. Feature Schema (dynamic spec)
    (d / "feature_schema.json").write_text(canonical_json_dumps(get_feature_schema()), encoding="utf-8")

    # 4. Blue Metrics
    if evaluation.rounds:
        blue_dump = evaluation.rounds[-1].blue.model_dump()
    else:
        blue_dump = {}
    (d / "blue_metrics.json").write_text(canonical_json_dumps(blue_dump), encoding="utf-8")

    # 5. Red Metrics
    if evaluation.rounds:
        red_dump = evaluation.rounds[-1].red.model_dump()
    else:
        red_dump = {}
    (d / "red_metrics.json").write_text(canonical_json_dumps(red_dump), encoding="utf-8")

    # 6. Coevolution Metrics
    (d / "coevolution_metrics.json").write_text(canonical_json_dumps(coevolution_reports), encoding="utf-8")

    # 7. Policy Metrics
    policy_metrics = {
        "final_decision_counts": blue_dump.get("decision_counts", {}),
        "policy_version": "0.1.0",
        "parameters": {
            "c_fraud_multiplier": 1.0,
            "c_step_up_fixed": 0.50,
            "step_up_fraud_catch_rate": 0.90,
            "false_block_fixed": 10.0,
            "false_block_variable_pct": 0.05,
        },
    }
    (d / "policy_metrics.json").write_text(canonical_json_dumps(policy_metrics), encoding="utf-8")

    # 8. Attack Summary
    (d / "attack_summary.json").write_text(canonical_json_dumps(attack_summary), encoding="utf-8")

    # 9. Calibration Artifact
    calib = calibration_data or {
        "method": "isotonic_regression",
        "bins": 10,
        "ece": blue_dump.get("ece", 0.0),
        "brier": blue_dump.get("brier", 0.0),
    }
    (d / "calibration.json").write_text(canonical_json_dumps(calib), encoding="utf-8")

    # 10. External Anchor Artifact
    anchor_meta = get_external_anchor_metadata()
    if evaluation.anchor:
        anchor_meta["metrics"] = evaluation.anchor.model_dump()
    (d / "external_anchor.json").write_text(canonical_json_dumps(anchor_meta), encoding="utf-8")

    # 11. Sample Transactions with Explanations
    (d / "sample_transactions.json").write_text(canonical_json_dumps(sample_txns_with_shap), encoding="utf-8")

    # 12. Decisions & Transactions Collections
    (d / "decisions.json").write_text(
        canonical_json_dumps([json.loads(dec.model_dump_json()) for dec in decisions]),
        encoding="utf-8",
    )
    (d / "transactions.json").write_text(
        canonical_json_dumps([json.loads(t.model_dump_json()) for t in transactions]),
        encoding="utf-8",
    )

    # 13. Block 7 Granular Artifacts (if provided)
    failures = kwargs.get("failures")
    if failures is not None:
        (d / "failures.json").write_text(
            canonical_json_dumps([json.loads(f.model_dump_json()) if hasattr(f, "model_dump_json") else f for f in failures]),
            encoding="utf-8",
        )

    weakness_profile = kwargs.get("weakness_profile")
    if weakness_profile is not None:
        (d / "weakness_profile.json").write_text(
            canonical_json_dumps(json.loads(weakness_profile.model_dump_json()) if hasattr(weakness_profile, "model_dump_json") else weakness_profile),
            encoding="utf-8",
        )

    scoreboard = kwargs.get("scoreboard")
    if scoreboard is not None:
        (d / "scoreboard.json").write_text(
            canonical_json_dumps([json.loads(s.model_dump_json()) if hasattr(s, "model_dump_json") else s for s in scoreboard]),
            encoding="utf-8",
        )

    promotion_history = kwargs.get("promotion_history")
    if promotion_history is not None:
        (d / "promotion_history.json").write_text(
            canonical_json_dumps([json.loads(p.model_dump_json()) if hasattr(p, "model_dump_json") else p for p in promotion_history]),
            encoding="utf-8",
        )

    experiment_register = kwargs.get("experiment_register")
    if experiment_register is not None:
        (d / "experiment_register.json").write_text(
            canonical_json_dumps([json.loads(e.model_dump_json()) if hasattr(e, "model_dump_json") else e for e in experiment_register]),
            encoding="utf-8",
        )

    three_world_eval = kwargs.get("three_world_evaluation")
    if three_world_eval is not None:
        (d / "three_world_evaluation.json").write_text(
            canonical_json_dumps(json.loads(three_world_eval.model_dump_json()) if hasattr(three_world_eval, "model_dump_json") else three_world_eval),
            encoding="utf-8",
        )

    # 14. Evidence Pack Markdown
    if evidence_pack_md:
        (d / "evidence_pack.md").write_text(evidence_pack_md, encoding="utf-8")

    # 15. Provenance Manifest (Hashes of all above files)
    prov = generate_provenance_manifest(d)
    (d / "provenance.json").write_text(canonical_json_dumps(prov), encoding="utf-8")


def validate_artifacts(d: Path) -> tuple[bool, list[str]]:
    """Performs deep schema validation, range checks, and cross-artifact consistency checks."""
    errors: list[str] = []

    required_files = [
        "manifest.json",
        "evaluation.json",
        "world_summary.json",
        "feature_schema.json",
        "blue_metrics.json",
        "red_metrics.json",
        "coevolution_metrics.json",
        "policy_metrics.json",
        "attack_summary.json",
        "calibration.json",
        "external_anchor.json",
        "sample_transactions.json",
        "transactions.json",
        "decisions.json",
        "provenance.json",
    ]

    for req in required_files:
        if not (d / req).exists():
            errors.append(f"MISSING_REQUIRED_FILE:{req}")

    if errors:
        return False, errors

    # Load artifacts for cross-validation
    try:
        manifest = load_manifest(d)
        world_summary = json.loads((d / "world_summary.json").read_text(encoding="utf-8"))
        feature_schema = json.loads((d / "feature_schema.json").read_text(encoding="utf-8"))
        blue_metrics = json.loads((d / "blue_metrics.json").read_text(encoding="utf-8"))
        red_metrics = json.loads((d / "red_metrics.json").read_text(encoding="utf-8"))
        coev_metrics = json.loads((d / "coevolution_metrics.json").read_text(encoding="utf-8"))
        txns = json.loads((d / "transactions.json").read_text(encoding="utf-8"))
        decisions = json.loads((d / "decisions.json").read_text(encoding="utf-8"))
        anchor = json.loads((d / "external_anchor.json").read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"JSON_LOAD_ERROR:{exc}"]

    # 1. Numerical range validations
    if blue_metrics:
        pr_auc = blue_metrics.get("pr_auc")
        if pr_auc is not None and not (0.0 <= pr_auc <= 1.0):
            errors.append(f"INVALID_RANGE:blue_metrics.pr_auc={pr_auc}")
        ece = blue_metrics.get("ece")
        if ece is not None and not (0.0 <= ece <= 1.0):
            errors.append(f"INVALID_RANGE:blue_metrics.ece={ece}")
        fpr = blue_metrics.get("fpr")
        if fpr is not None and not (0.0 <= fpr <= 1.0):
            errors.append(f"INVALID_RANGE:blue_metrics.fpr={fpr}")

    if red_metrics:
        for b, asr in red_metrics.get("asr_by_budget", {}).items():
            if not (0.0 <= asr <= 1.0):
                errors.append(f"INVALID_RANGE:red_metrics.asr@{b}={asr}")
        med = red_metrics.get("mean_evasion_distance")
        if med is not None and med < 0:
            errors.append(f"INVALID_RANGE:red_metrics.med={med}")

    # 2. Cross-artifact consistency
    n_txns = len(txns)
    if manifest.n_transactions != n_txns:
        errors.append(f"COUNT_MISMATCH:manifest.n_transactions({manifest.n_transactions}) != len(txns)({n_txns})")
    if world_summary.get("transaction_count") != n_txns:
        errors.append(f"COUNT_MISMATCH:world_summary.transaction_count({world_summary.get('transaction_count')}) != len(txns)({n_txns})")
    if len(decisions) != n_txns:
        errors.append(f"COUNT_MISMATCH:len(decisions)({len(decisions)}) != len(txns)({n_txns})")

    # 3. Dynamic feature schema validation
    if feature_schema.get("feature_count") != len(feature_schema.get("features", [])):
        errors.append(f"FEATURE_COUNT_MISMATCH:spec_count={feature_schema.get('feature_count')} vs len={len(feature_schema.get('features', []))}")

    # 4. External Anchor namespace validation
    if anchor.get("namespace") != "REAL_WORLD":
        errors.append(f"NAMESPACE_VIOLATION:anchor.namespace={anchor.get('namespace')} (must be REAL_WORLD)")

    # 5. Cryptographic hash verification
    ok_hash, hash_errors = verify_run_integrity(d)
    if not ok_hash:
        errors.extend(hash_errors)

    return len(errors) == 0, errors

