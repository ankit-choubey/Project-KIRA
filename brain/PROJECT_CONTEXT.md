# PROJECT CONTEXT

Read this before touching anything. See `AGENTS.md` for the rules and
`.agents/rules/` for per-area detail.

<!-- AUTO-GENERATED BELOW - DO NOT HAND-EDIT -->

_Generated 2026-08-30 03:23 from artifacts and git. Do not edit below._

## Current state

- **Last gate passed:** 2
- **Git:** `f6e7277` on `main`
- **Latest run:** `run_fixture_0000` — FIXTURE (not real), scale `fixture`

## Gate ladder

| Gate | Name | Status | Last run |
|---|---|---|---|
| 0 | contracts | PASS | 2026-08-30T03:23:35 |
| 1 | world | PASS | 2026-08-30T03:23:40 |
| 2 | features | PASS | 2026-08-30T03:23:44 |
| 3 | blue | pending (block not built) | 2026-08-30T03:23:44 |
| 4 | red | pending (block not built) | 2026-08-30T03:23:44 |
| 5 | loop | pending (block not built) | 2026-08-30T03:23:44 |
| 6 | artifacts | **FAIL** | 2026-08-30T03:23:44 |
| 7 | submission | not run | — |

## Live metrics

_Latest run is FIXTURE data. These are not measurements and must never_
_be cited in the report, the UI, or a commit message._

## What exists

- **BLOCK 0 — Foundation & unblock:** done
- **BLOCK 1 — Synthetic world + API/UI shell:** done
- **BLOCK 2 — Causal features + filter L1/L2/L4:** done
- **BLOCK 3 — Blue baseline + anchor:** not started
- **BLOCK 4 — Red engine + filter L3:** not started
- **BLOCK 5 — Closed loop + intent engine:** not started
- **BLOCK 6 — Full cloud run:** not started
- **BLOCK 7 — Evidence & docs:** done

## Open blockers

- **GATE 6 is failing.** Numbers are not defensible. Do not publish.

## Forbidden changes

- Do not hand-edit this file below the marker.
- Do not edit anything under `artifacts/` — it is generated.
- Do not weaken a gate assertion to make it pass.
- Do not add a dependency without a line in `brain/DECISIONS.md`.
- Do not build anything in the cut list (`.agents/rules/00-project.md`).
