"""The failure-localisation ladder.

Each gate asserts one invariant. When a downstream number looks wrong, walk UP the
ladder - the first failing gate names the layer that broke.

    python -m tools.gates 0        run one gate
    python -m tools.gates all      run every implemented gate, stop at first failure

Exit codes:  0 = passed   1 = failed   2 = not implemented yet

A gate that is not implemented reports PENDING and exits 2. It never reports PASS.
This is deliberate: "the gate passed" must always mean the check actually ran.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mcdl.config import artifacts_dir, load_config  # noqa: E402

# This repo is developed on Windows and runs on Linux. The Windows console
# defaults to cp1252, which cannot encode box-drawing characters, so output here
# stays ASCII-only and stdout is coerced to UTF-8 where the runtime allows it.
if hasattr(sys.stdout, "reconfigure"):  # pragma: no cover - platform dependent
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        pass

_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
GREEN = "\033[32m" if _COLOR else ""
RED = "\033[31m" if _COLOR else ""
YELLOW = "\033[33m" if _COLOR else ""
DIM = "\033[2m" if _COLOR else ""
RESET = "\033[0m" if _COLOR else ""
RULE = "-" * 66


class Pending(Exception):
    """Raised by a gate whose block has not been built yet."""


class Checks:
    """Collects named boolean checks so a gate reports every failure, not just
    the first one. Debugging six failures one run at a time wastes a day."""

    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, name: str, passed: bool, detail: str = "") -> bool:
        self.items.append({"name": name, "passed": bool(passed), "detail": detail})
        return bool(passed)

    def expect(self, name: str, value, expected, detail: str = "") -> bool:
        ok = value == expected
        return self.add(name, ok, detail or f"got {value!r}, expected {expected!r}")

    @property
    def passed(self) -> bool:
        return all(i["passed"] for i in self.items)


# --------------------------------------------------------------------------- #
# GATE 0 - contracts
# --------------------------------------------------------------------------- #


def gate_0(c: Checks) -> None:
    """Schemas import, config validates, fixtures write, unit tests green."""
    from mcdl import fixtures, schemas

    c.add("schemas import", hasattr(schemas, "Transaction"))

    cfg = load_config()
    c.add("config loads and validates", cfg["scale"] in ("tiny", "small", "full"),
          f"scale={cfg['scale']} hash={cfg.hash}")

    # Observable / hidden split must be exhaustive and disjoint - a hidden field
    # leaking into the observable list is the fastest route to a fake 0.99.
    obs = set(schemas.Transaction.observable_fields())
    hid = set(schemas.Transaction.hidden_fields())
    all_fields = set(schemas.Transaction.model_fields)
    c.add("observable/hidden are disjoint", not (obs & hid), f"overlap={obs & hid}")
    c.add("observable+hidden cover all fields", obs | hid == all_fields,
          f"missing={all_fields - (obs | hid)}")

    run_dir = fixtures.make_fixtures(artifacts_dir(cfg))
    c.add("fixtures written", run_dir.is_dir(), str(run_dir))

    from mcdl.artifacts import load_evaluation, load_transactions, resolve_run

    d = resolve_run()
    ev = load_evaluation(d)
    txns = load_transactions(d, limit=50)
    c.add("fixture evaluation validates", ev.manifest.run_id == fixtures.FIXTURE_RUN_ID)
    c.add("fixture marked is_fixture", ev.manifest.is_fixture is True,
          "the UI must show a FIXTURE banner for these")
    c.add("fixture transactions validate", len(txns) == 50)

    # Fixtures must leave unmeasured things unmeasured. A fixture that invents a
    # C2ST number teaches the UI to render fake precision.
    c.add("fixture leaves L3/L4 unmeasured",
          ev.fidelity.l4_c2st_auc_row is None and ev.fidelity.l3_p1_interarrival_ratio is None,
          "unmeasured must be null, never 0.0")

    r = _pytest("tests/unit")
    c.add("pytest tests/unit", r.returncode == 0, _tail(r))

    # The API runs against fixtures, so its contract is testable from a clean
    # clone before the simulator or any model exists.
    r = _pytest("tests/e2e")
    c.add("pytest tests/e2e (API on fixtures)", r.returncode == 0, _tail(r))

    dist = REPO_ROOT / "frontend" / "dist" / "index.html"
    c.add("frontend built (frontend/dist)", dist.exists(),
          "run `make frontend` - the Dockerfile copies dist, it does not build it")

    # Optional: only checked when a deployment URL is configured, so local runs
    # do not fail merely because nothing is deployed yet.
    space_url = os.environ.get("MCDL_SPACE_URL")
    if space_url:
        check_health(c, space_url)


# --------------------------------------------------------------------------- #
# GATE 1..7
# --------------------------------------------------------------------------- #


def gate_1(c: Checks) -> None:
    """World: zero physics violations, FK integrity. BLOCK 1."""
    try:
        from mcdl.evaluation.validity import check_world  # noqa: F401
    except ImportError as exc:
        raise Pending("BLOCK 1 not built: mcdl.evaluation.validity.check_world") from exc
    raise Pending("gate 1 body pending BLOCK 1")


def gate_2(c: Checks) -> None:
    """Features: batch == stream, no future reads. BLOCK 2. THE CRITICAL GATE."""
    try:
        from mcdl.features import batch, stream  # noqa: F401
    except ImportError as exc:
        raise Pending("BLOCK 2 not built: mcdl.features.batch / mcdl.features.stream") from exc
    r = _pytest("tests/invariants")
    c.add("batch/stream parity + no-future-reads", r.returncode == 0, _tail(r))


def gate_3(c: Checks) -> None:
    """Blue: out-of-time split enforced, beats rule baseline, ECE recorded. BLOCK 3."""
    try:
        from mcdl.blue import model  # noqa: F401
    except ImportError as exc:
        raise Pending("BLOCK 3 not built: mcdl.blue.model") from exc
    raise Pending("gate 3 body pending BLOCK 3")


def gate_4(c: Checks) -> None:
    """Red: zero mask violations, attacks valid, ASR@budget, MED. BLOCK 4."""
    try:
        from mcdl.red import search  # noqa: F401
    except ImportError as exc:
        raise Pending("BLOCK 4 not built: mcdl.red.search") from exc
    raise Pending("gate 4 body pending BLOCK 4")


def gate_5(c: Checks) -> None:
    """Loop: held-out-variant ASR reported separately, no regression. BLOCK 5."""
    try:
        from mcdl.loop import coevolution  # noqa: F401
    except ImportError as exc:
        raise Pending("BLOCK 5 not built: mcdl.loop.coevolution") from exc
    raise Pending("gate 5 body pending BLOCK 5")


def gate_6(c: Checks) -> None:
    """Artifacts: every UI number traces to a run_id, and it is not a fixture."""
    from mcdl.artifacts import load_evaluation, resolve_run

    d = resolve_run()
    ev = load_evaluation(d)
    c.add("a run exists", d.is_dir(), str(d))
    c.add("run is NOT a fixture", ev.manifest.is_fixture is False,
          "fixture numbers must never reach the report or the live demo")
    c.add("git commit recorded", ev.manifest.git_commit != "unknown", ev.manifest.git_commit)
    c.add("rounds present", len(ev.rounds) > 0, f"{len(ev.rounds)} rounds")
    c.add("external anchor measured", ev.anchor is not None,
          "the anchor is what makes every other number credible (audit F-07)")


def gate_7(c: Checks) -> None:
    """Submission audit. BLOCK 7 - largely manual, checked here where possible."""
    c.add("README exists", (REPO_ROOT / "README.md").exists())
    c.add("LIMITATIONS.md exists", (REPO_ROOT / "docs" / "LIMITATIONS.md").exists())
    c.add("COMPETITION.md exists (deadline + timezone verified)",
          (REPO_ROOT / "docs" / "COMPETITION.md").exists())
    c.add("no .env committed", not (REPO_ROOT / ".env").exists(), "secrets must not be in git")
    r = _pytest("tests", extra=["-m", "not slow"])
    c.add("full test suite (fast) green", r.returncode == 0, _tail(r))


# --------------------------------------------------------------------------- #
# Optional live-service check, shared by several gates
# --------------------------------------------------------------------------- #


def check_health(c: Checks, url: str) -> None:
    """Hit /api/health on a running service. Skipped unless MCDL_SPACE_URL is set,
    so local gate runs do not fail just because nothing is deployed yet."""
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}/api/health", timeout=10) as resp:
            body = json.loads(resp.read().decode())
        c.add("live /api/health returns 200", resp.status == 200, json.dumps(body))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        c.add("live /api/health returns 200", False, f"{type(exc).__name__}: {exc}")


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #

GATES: dict[int, tuple[str, Callable[[Checks], None]]] = {
    0: ("contracts", gate_0),
    1: ("world", gate_1),
    2: ("features", gate_2),
    3: ("blue", gate_3),
    4: ("red", gate_4),
    5: ("loop", gate_5),
    6: ("artifacts", gate_6),
    7: ("submission", gate_7),
}

FAILURE_MEANING = {
    0: "The two developers have drifted apart. Reconcile contracts before anything else.",
    1: "Simulator bug. Every number downstream is meaningless until this is fixed.",
    2: "LEAKAGE. This is the bug that looks like success. Do not proceed.",
    3: "Circular evaluation. The headline result would be fiction.",
    4: "Attacks are cheating. ASR is inflated and indefensible.",
    5: "You are measuring memorisation, not hardening.",
    6: "You cannot defend these numbers in the report. Do not publish them.",
    7: "Submission is not ready.",
}


def _pytest(target: str, extra: list[str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pytest", target, *(extra or [])],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _tail(r: subprocess.CompletedProcess, n: int = 3) -> str:
    lines = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()]
    return " | ".join(lines[-n:]) if lines else ""


def run_gate(n: int) -> int:
    name, fn = GATES[n]
    print(f"\n{DIM}{'-' * 66}{RESET}")
    print(f"GATE {n} — {name}")
    print(f"{DIM}{RULE}{RESET}")

    c = Checks()
    status = "passed"
    try:
        fn(c)
    except Pending as exc:
        print(f"{YELLOW}  PENDING{RESET}  {exc}")
        print(f"{DIM}  Not implemented yet. This is not a pass.{RESET}")
        _record(n, name, False, c, status="pending")
        return 2
    except Exception as exc:  # a crashing gate is a failing gate
        c.add(f"gate raised {type(exc).__name__}", False, str(exc))
        status = "error"

    for item in c.items:
        mark = f"{GREEN}  PASS{RESET}" if item["passed"] else f"{RED}  FAIL{RESET}"
        detail = f"  {DIM}{item['detail']}{RESET}" if item["detail"] else ""
        print(f"{mark}  {item['name']}{detail}")

    ok = c.passed and status == "passed"
    print(f"\n  {'GATE ' + str(n) + ' PASSED' if ok else RED + 'GATE ' + str(n) + ' FAILED' + RESET}")
    if not ok:
        print(f"  {DIM}{FAILURE_MEANING[n]}{RESET}")

    _record(n, name, ok, c)
    return 0 if ok else 1


def _record(n: int, name: str, passed: bool, c: Checks, status: str = "ran") -> None:
    path = artifacts_dir() / "gates.json"
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    data[str(n)] = {
        "gate": n,
        "name": name,
        "passed": passed,
        "status": status,
        "checks": c.items,
        "ran_at": datetime.now().isoformat(timespec="seconds"),
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 1

    arg = argv[1]
    if arg == "all":
        worst = 0
        for n in sorted(GATES):
            rc = run_gate(n)
            if rc == 1:
                return 1  # a real failure stops the ladder
            worst = max(worst, rc)
        return worst

    try:
        n = int(arg)
    except ValueError:
        print(f"unknown gate {arg!r}. Use 0..7 or 'all'.")
        return 1
    if n not in GATES:
        print(f"unknown gate {n}. Use 0..7 or 'all'.")
        return 1
    return run_gate(n)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
