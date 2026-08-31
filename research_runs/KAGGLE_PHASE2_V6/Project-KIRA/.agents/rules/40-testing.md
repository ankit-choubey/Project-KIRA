# 40 — Testing and gates

## The idea

Tests here are not for coverage. They are a **failure-localisation ladder**: each
gate asserts one invariant, so when a downstream number looks wrong you walk up
the ladder and the first failing gate names the layer that broke.

```bash
make gate 0    # contracts   - schemas import, fixtures valid, unit tests, /api/health
make gate 1    # world       - zero physics violations, FK integrity
make gate 2    # features    - batch == stream, no future reads    <-- the critical one
make gate 3    # blue        - out-of-time split enforced, beats rule baseline, ECE
make gate 4    # red         - zero mask violations, attacks valid, ASR@budget, MED
make gate 5    # loop        - held-out-variant ASR separate, no regression
make gate 6    # artifacts   - every UI number traces to a run_id and reproduces
make gate 7    # submission  - repo public, no secrets, demo live, writeup submitted
```

Each gate prints one line per check, writes `artifacts/gates.json`, exits non-zero
on failure, and then runs `make brain`.

## What a failing gate means

| Gate | Failure means |
|---|---|
| 0 | The two developers have drifted apart. Reconcile before anything else. |
| 1 | Simulator bug. Every number downstream is meaningless until fixed. |
| 2 | **Leakage.** This is the bug that looks like success. |
| 3 | Circular evaluation. The headline result is fiction. |
| 4 | Attacks are cheating. ASR is inflated and indefensible. |
| 5 | You are measuring memorisation, not hardening. |
| 6 | You cannot defend the number in the report. Do not publish it. |

## Directory meaning

- `tests/unit/` — pure functions, no I/O, milliseconds. Run on every save.
- `tests/invariants/` — the properties gates assert. **Written before the code
  they check.** `test_batch_stream_parity.py` and `test_no_future_reads.py` are the
  two that matter most in this repo.
- `tests/integration/` — module pairs against a `scale: tiny` world.
- `tests/e2e/` — the API via `httpx`, and the pipeline end to end.

Anything needing a generated world is marked `@pytest.mark.slow`.

## Assertions over test files

In a 3-day build, an `assert` that runs on every pipeline execution beats a pytest
file nobody runs twice. Put invariants **inside** the pipeline where they are
cheap — validity checks, ordering, FK integrity — and reserve test files for
things that need fixtures or comparison.

## Rules

1. **Never report a gate as passing that you did not run.** Paste the real output.
2. A gate that fails is information. Do not weaken the assertion to make it pass —
   fix the cause, or write in `brain/ERRORS.md` why the assertion was wrong.
3. New feature, new invariant. If you add something to `features/spec.py`, the
   parity test picks it up automatically — verify it actually did.
4. Fixtures (`src/mcdl/fixtures.py`) must stay schema-valid. If a schema changes
   and fixtures do not, gate 0 catches it — that is the point.

## CI

One GitHub Actions job: `ruff check` + `pytest -m "not slow"`. Nothing heavy runs
on push. The real verification is the gate ladder run locally and on Kaggle.
