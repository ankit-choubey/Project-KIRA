"""Regenerate `brain/PROJECT_CONTEXT.md` from what actually exists on disk.

The point: a coding agent reading PROJECT_CONTEXT.md gets the true current state -
which gates passed, what the real metrics are, which modules exist - rather than
whatever someone last remembered to type. Nothing here is hand-written, so nothing
here can be stale or aspirational.

Run directly, or via `make brain` (which every gate calls on completion).
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mcdl.config import artifacts_dir  # noqa: E402

MARKER = "<!-- AUTO-GENERATED BELOW - DO NOT HAND-EDIT -->"

BLOCKS = [
    (0, "Foundation & unblock", ["src/mcdl/schemas.py", "src/mcdl/fixtures.py", "tools/gates.py"]),
    (1, "Synthetic world + API/UI shell", ["src/mcdl/world/generator.py", "api/main.py"]),
    (2, "Causal features + filter L1/L2/L4", ["src/mcdl/features/spec.py",
                                              "src/mcdl/features/batch.py",
                                              "src/mcdl/features/stream.py"]),
    (3, "Blue baseline + anchor", ["src/mcdl/blue/model.py", "src/mcdl/evaluation/tstr.py"]),
    (4, "Red engine + filter L3", ["src/mcdl/red/search.py", "src/mcdl/evaluation/behavioral.py"]),
    (5, "Closed loop + intent engine", ["src/mcdl/loop/coevolution.py",
                                        "src/mcdl/blue/intent.py"]),
    (6, "Full cloud run", ["notebooks/kaggle/02_full_run.ipynb"]),
    (7, "Evidence & docs", ["docs/LIMITATIONS.md", "docs/COMPETITION.md"]),
]


def _git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _gates() -> dict:
    p = artifacts_dir() / "gates.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _latest_evaluation():
    try:
        from mcdl.artifacts import load_evaluation, resolve_run

        return load_evaluation(resolve_run())
    except Exception:
        return None


def _fmt(v, suffix: str = "") -> str:
    return "not measured" if v is None else f"{v}{suffix}"


def build() -> str:
    gates = _gates()
    ev = _latest_evaluation()
    lines: list[str] = []
    add = lines.append

    add("# PROJECT CONTEXT")
    add("")
    add("Read this before touching anything. See `AGENTS.md` for the rules and")
    add("`.agents/rules/` for per-area detail.")
    add("")
    add(MARKER)
    add("")
    add(f"_Generated {datetime.now():%Y-%m-%d %H:%M} from artifacts and git. Do not edit below._")
    add("")

    # --- state ------------------------------------------------------------
    passed = [int(k) for k, v in gates.items() if v.get("passed")]
    last_gate = max(passed) if passed else None
    add("## Current state")
    add("")
    add(f"- **Last gate passed:** {last_gate if last_gate is not None else 'none yet'}")
    add(f"- **Git:** `{_git('rev-parse', '--short', 'HEAD') or 'no commits yet'}` "
        f"on `{_git('rev-parse', '--abbrev-ref', 'HEAD') or '-'}`")
    if ev is not None:
        kind = "FIXTURE (not real)" if ev.manifest.is_fixture else "real run"
        add(f"- **Latest run:** `{ev.manifest.run_id}` — {kind}, scale `{ev.manifest.scale}`")
    else:
        add("- **Latest run:** none. Run `make gate 0` to write fixtures.")
    add("")

    # --- gate ladder ------------------------------------------------------
    add("## Gate ladder")
    add("")
    add("| Gate | Name | Status | Last run |")
    add("|---|---|---|---|")
    for n in range(8):
        g = gates.get(str(n))
        if not g:
            status, when = "not run", "—"
        elif g.get("status") == "pending":
            status, when = "pending (block not built)", g.get("ran_at", "—")
        else:
            status = "PASS" if g.get("passed") else "**FAIL**"
            when = g.get("ran_at", "—")
        add(f"| {n} | {GATE_NAMES[n]} | {status} | {when} |")
    add("")

    # --- metrics ----------------------------------------------------------
    add("## Live metrics")
    add("")
    if ev is None:
        add("_No run yet._")
    elif ev.manifest.is_fixture:
        add("_Latest run is FIXTURE data. These are not measurements and must never_")
        add("_be cited in the report, the UI, or a commit message._")
    else:
        last = ev.rounds[-1] if ev.rounds else None
        if last:
            add(f"- PR-AUC `{_fmt(last.blue.pr_auc)}` · ECE `{_fmt(last.blue.ece)}` · "
                f"FPR `{_fmt(last.blue.fpr)}`")
            add(f"- ASR held-out variants `{_fmt(last.red.asr_heldout_variants)}` · "
                f"unseen family `{_fmt(last.red.asr_unseen_family)}`")
            add(f"- Minimum Evasion Distance `{_fmt(last.red.mean_evasion_distance)}`")
            add(f"- Latency P50/P95/P99 `{_fmt(last.blue.latency_p50_ms)}` / "
                f"`{_fmt(last.blue.latency_p95_ms)}` / `{_fmt(last.blue.latency_p99_ms)}` ms")
        f = ev.fidelity
        add(f"- Filter L1 violations `{f.l1_violations}` · "
            f"L4 C2ST row `{_fmt(f.l4_c2st_auc_row)}` entity `{_fmt(f.l4_c2st_auc_entity)}`")
        add(f"- Filter L3 ratios — P1 `{_fmt(f.l3_p1_interarrival_ratio)}` · "
            f"P2 `{_fmt(f.l3_p2_burstiness_ratio)}` · P3 `{_fmt(f.l3_p3_graph_motif_ratio)}` · "
            f"P4 `{_fmt(f.l3_p4_velocity_trigger_ratio)}` (1.0 = real)")
        add(f"- External anchor: {'measured' if ev.anchor else '**not measured**'}")
    add("")

    # --- what exists ------------------------------------------------------
    add("## What exists")
    add("")
    for n, name, paths in BLOCKS:
        present = [p for p in paths if (REPO_ROOT / p).exists()]
        mark = "done" if len(present) == len(paths) else (
            f"partial ({len(present)}/{len(paths)})" if present else "not started"
        )
        add(f"- **BLOCK {n} — {name}:** {mark}")
    add("")

    # --- blockers ---------------------------------------------------------
    add("## Open blockers")
    add("")
    failing = [int(k) for k, v in gates.items() if v.get("status") == "ran" and not v.get("passed")]
    if failing:
        for n in sorted(failing):
            add(f"- **GATE {n} is failing.** {FAILURE_MEANING[n]}")
    else:
        add("- None recorded. Check `brain/ERRORS.md` for anything not yet gated.")
    add("")

    add("## Forbidden changes")
    add("")
    add("- Do not hand-edit this file below the marker.")
    add("- Do not edit anything under `artifacts/` — it is generated.")
    add("- Do not weaken a gate assertion to make it pass.")
    add("- Do not add a dependency without a line in `brain/DECISIONS.md`.")
    add("- Do not build anything in the cut list (`.agents/rules/00-project.md`).")
    add("")
    return "\n".join(lines)


GATE_NAMES = {
    0: "contracts", 1: "world", 2: "features", 3: "blue",
    4: "red", 5: "loop", 6: "artifacts", 7: "submission",
}
FAILURE_MEANING = {
    0: "Contracts have drifted. Reconcile before anything else.",
    1: "Simulator bug. Downstream numbers are meaningless.",
    2: "Leakage. The bug that looks like success.",
    3: "Circular evaluation.",
    4: "Attacks are cheating; ASR is indefensible.",
    5: "Measuring memorisation, not hardening.",
    6: "Numbers are not defensible. Do not publish.",
    7: "Submission not ready.",
}


def main() -> int:
    out = REPO_ROOT / "brain" / "PROJECT_CONTEXT.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print(f"brain updated: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
