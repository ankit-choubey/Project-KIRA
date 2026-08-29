# PROJECT CONTEXT

Read this before touching anything. See `AGENTS.md` for the rules and
`.agents/rules/` for per-area detail.

<!-- AUTO-GENERATED BELOW - DO NOT HAND-EDIT -->

_Generated 2026-08-30 03:17 from artifacts and git. Do not edit below._

## Current state

- **Last gate passed:** 1
- **Git:** `202f0f1` on `main`
- **Latest run:** `run_fixture_0000` — FIXTURE (not real), scale `fixture`

## Gate ladder

| Gate | Name | Status | Last run |
|---|---|---|---|
| 0 | contracts | PASS | 2026-08-30T03:09:19 |
| 1 | world | PASS | 2026-08-30T03:17:46 |
| 2 | features | not run | — |
| 3 | blue | not run | — |
| 4 | red | not run | — |
| 5 | loop | not run | — |
| 6 | artifacts | not run | — |
| 7 | submission | not run | — |

## Live metrics

_Latest run is FIXTURE data. These are not measurements and must never_
_be cited in the report, the UI, or a commit message._

## What exists

- **BLOCK 0 — Foundation & unblock:** done
- **BLOCK 1 — Synthetic world + API/UI shell:** done
- **BLOCK 2 — Causal features + filter L1/L2/L4:** not started
- **BLOCK 3 — Blue baseline + anchor:** not started
- **BLOCK 4 — Red engine + filter L3:** not started
- **BLOCK 5 — Closed loop + intent engine:** not started
- **BLOCK 6 — Full cloud run:** not started
- **BLOCK 7 — Evidence & docs:** done

## Open blockers

- None recorded. Check `brain/ERRORS.md` for anything not yet gated.

## Forbidden changes

- Do not hand-edit this file below the marker.
- Do not edit anything under `artifacts/` — it is generated.
- Do not weaken a gate assertion to make it pass.
- Do not add a dependency without a line in `brain/DECISIONS.md`.
- Do not build anything in the cut list (`.agents/rules/00-project.md`).
