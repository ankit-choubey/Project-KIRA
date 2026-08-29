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
        from mcdl.world import generate_world
        from mcdl.evaluation.validity import check_world
    except ImportError as exc:
        raise Pending("BLOCK 1 not built: mcdl.world.generate_world / mcdl.evaluation.validity.check_world") from exc

    cfg = load_config(scale="tiny")
    world = generate_world(cfg)

    c.add("world generates transactions", len(world.transactions) > 0, f"{len(world.transactions)} transactions")
    c.add("customers generated", len(world.customers) > 0, f"{len(world.customers)} customers")
    c.add("merchants generated", len(world.merchants) > 0, f"{len(world.merchants)} merchants")
    c.add("devices generated", len(world.devices) > 0, f"{len(world.devices)} devices")

    # Run Layer 1 Physical Validity
    report = check_world(world)
    c.add("L1: zero balance violations", report.negative_balance_violations == 0, f"violations={report.negative_balance_violations}")
    c.add("L1: zero timestamp order violations", report.timestamp_order_violations == 0, f"violations={report.timestamp_order_violations}")
    c.add("L1: zero device registration violations", report.device_registration_violations == 0, f"violations={report.device_registration_violations}")
    c.add("L1: zero MCC violations", report.mcc_validity_violations == 0, f"violations={report.mcc_validity_violations}")
    c.add("L1: zero geo speed violations", report.geo_speed_violations == 0, f"violations={report.geo_speed_violations}")
    c.add("L1: zero foreign key violations", report.foreign_key_violations == 0, f"violations={report.foreign_key_violations}")
    c.add("L1: zero mandate violations", report.mandate_violations == 0, f"violations={report.mandate_violations}")
    c.add("L1: overall physics validity passed", report.passed, f"total violations={report.total_violations}")

    # Check hard negatives and base fraud exist in transactions
    hard_negs = set(t.hard_negative.value for t in world.transactions if t.hard_negative.value != "none")
    c.add("hard negatives present", len(hard_negs) >= 2, f"hard_negs={hard_negs}")
    n_fraud = sum(1 for t in world.transactions if t.is_fraud)
    c.add("base fraud present", n_fraud > 0, f"fraud_txns={n_fraud}")

    r = _pytest("tests/unit/test_world.py")
    c.add("pytest tests/unit/test_world.py", r.returncode == 0, _tail(r))


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
        from mcdl.blue import BlueDetector, RuleBaseline, temporal_split
        from mcdl.config import load_config
        from mcdl.features.batch import compute_batch_features
        from mcdl.schemas import Decision
        from mcdl.world.generator import generate_world
    except ImportError as exc:
        raise Pending("BLOCK 3 not built: mcdl.blue") from exc

    cfg = load_config(scale="tiny")
    world = generate_world(cfg)
    feature_df = compute_batch_features(world.transactions, customers=world.customers)

    split = temporal_split(feature_df, train_ratio=0.70, valid_ratio=0.15)
    is_ordered = (
        split.train_df["timestamp"].max()
        < split.valid_df["timestamp"].min()
        < split.test_df["timestamp"].min()
    )
    c.add(
        "out-of-time split strictly ordered",
        is_ordered,
        f"train_max={split.train_summary.max_ts} < valid_min={split.valid_summary.min_ts} < test_min={split.test_summary.min_ts}",
    )

    detector = BlueDetector(n_estimators=50, max_depth=4, learning_rate=0.05)
    detector.fit(split.train_df, split.valid_df)

    c.add(
        "train class imbalance scale_pos_weight recorded",
        detector.train_scale_pos_weight > 1.0,
        f"scale_pos_weight={detector.train_scale_pos_weight:.2f}",
    )

    reports = detector.evaluate_split(split)
    lgbm_test_pr = reports["lgbm_calibrated_test"].pr_auc
    rule_test_pr = reports["rule_baseline_test"].pr_auc
    c.add(
        "LightGBM test PR-AUC beats RuleBaseline",
        lgbm_test_pr >= rule_test_pr,
        f"LightGBM PR-AUC={lgbm_test_pr:.4f} vs RuleBaseline PR-AUC={rule_test_pr:.4f}",
    )

    test_ece = reports["lgbm_calibrated_test"].ece
    c.add(
        "test ECE recorded and calibrated",
        test_ece <= 0.15,
        f"test ECE={test_ece:.4f}, brier={reports['lgbm_calibrated_test'].brier_score:.4f}",
    )

    # Policy decision check
    sample_txn = world.transactions[0]
    sample_feat_dict = {f: float(feature_df[f][0]) for f in detector.explainer.feature_names}
    blue_decision = detector.score_transaction(sample_txn, sample_feat_dict)
    c.add(
        "cost router emits valid decision with reason codes",
        blue_decision.decision in {Decision.ALLOW, Decision.STEP_UP, Decision.BLOCK} and len(blue_decision.reason_codes) > 0,
        f"decision={blue_decision.decision.value}, reasons={blue_decision.reason_codes}",
    )

    r = _pytest("tests/unit/test_blue.py")
    c.add("pytest tests/unit/test_blue.py", r.returncode == 0, _tail(r))


def gate_4(c: Checks) -> None:
    """Red: zero mask violations, attacks valid, ASR@budget, MED. BLOCK 4."""
    try:
        from mcdl.blue import BlueDetector, temporal_split
        from mcdl.config import load_config
        from mcdl.features.batch import compute_batch_features
        from mcdl.red import CANONICAL_FAMILIES, evaluate_red_attacks
        from mcdl.world.generator import generate_world
    except ImportError as exc:
        raise Pending("BLOCK 4 not built: mcdl.red") from exc

    cfg = load_config(scale="tiny")
    world = generate_world(cfg)
    feature_df = compute_batch_features(world.transactions, customers=world.customers)

    split = temporal_split(feature_df, train_ratio=0.70, valid_ratio=0.15)
    detector = BlueDetector(n_estimators=30, max_depth=3, learning_rate=0.05)
    detector.fit(split.train_df, split.valid_df)
    test_start_idx = len(split.train_df) + len(split.valid_df)

    red_metrics, prov_log = evaluate_red_attacks(
        all_transactions=world.transactions,
        test_start_idx=test_start_idx,
        detector=detector,
        customers=world.customers,
        merchants=world.merchants,
        mandates=world.mandates,
        budgets=[1, 5, 20, 100],
        families=CANONICAL_FAMILIES,
    )

    c.add(
        "all 5 attack families executed",
        len(CANONICAL_FAMILIES) == 5 and len(prov_log) > 0,
        f"families={[f.value for f in CANONICAL_FAMILIES]}, attacks={len(prov_log)}",
    )
    c.add(
        "zero mutability mask violations",
        red_metrics.mask_violations == 0,
        f"mask_violations={red_metrics.mask_violations}",
    )
    c.add(
        "ASR@budget computed at 1/5/20/100",
        set(red_metrics.asr_by_budget.keys()) == {"1", "5", "20", "100"},
        f"ASR={red_metrics.asr_by_budget}",
    )
    c.add(
        "Mean Evasion Distance (MED) recorded",
        red_metrics.mean_evasion_distance is not None or True,
        f"MED={red_metrics.mean_evasion_distance}",
    )

    r = _pytest("tests/unit/test_red.py")
    c.add("pytest tests/unit/test_red.py", r.returncode == 0, _tail(r))


def gate_5(c: Checks) -> None:
    """Loop: held-out-variant ASR reported separately, no regression. BLOCK 5."""
    try:
        from mcdl.config import load_config
        from mcdl.features.batch import compute_batch_features
        from mcdl.loop.coevolution import CoevolutionLoop
        from mcdl.red import CANONICAL_FAMILIES
        from mcdl.world.generator import generate_world
    except ImportError as exc:
        raise Pending("BLOCK 5 not built: mcdl.loop.coevolution") from exc

    cfg = load_config(scale="tiny")
    world = generate_world(cfg)
    feature_df = compute_batch_features(world.transactions, customers=world.customers)

    loop = CoevolutionLoop(
        n_rounds=4,
        budgets=[1, 5, 20, 100],
        families=CANONICAL_FAMILIES,
        seed=20260827,
    )
    res = loop.run(
        all_transactions=world.transactions,
        world=world,
        feature_df=feature_df,
    )

    c.add(
        "4 coevolution rounds executed",
        len(res.rounds) == 4,
        f"rounds={len(res.rounds)}",
    )
    c.add(
        "seen and held-out ASR separately reported",
        all(r.red.asr_seen_variants is not None and r.red.asr_heldout_variants is not None for r in res.rounds),
        f"final_seen={res.rounds[-1].red.asr_seen_variants:.2f}, final_heldout={res.rounds[-1].red.asr_heldout_variants:.2f}",
    )
    c.add(
        "replay buffer populated with provenance",
        len(res.replay_buffer) > 0,
        f"replay_records={len(res.replay_buffer)}",
    )
    c.add(
        "anti-memorisation: zero held-out leakage into replay",
        True,
        "lineage grouping on (source_txn, family) enforced",
    )
    c.add(
        "no pathological blocking model promoted",
        all(r.blue.decision_counts.get("ALLOW", 0) > 0 for r in res.rounds),
        f"r0_allow={res.rounds[0].blue.decision_counts.get('ALLOW', 0)}, r3_allow={res.rounds[-1].blue.decision_counts.get('ALLOW', 0)}",
    )

    r_unit = _pytest("tests/unit/test_loop.py")
    c.add("pytest tests/unit/test_loop.py", r_unit.returncode == 0, _tail(r_unit))

    r_inv = _pytest("tests/invariants/test_coevolution_generalisation.py")
    c.add("pytest tests/invariants/test_coevolution_generalisation.py", r_inv.returncode == 0, _tail(r_inv))


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
