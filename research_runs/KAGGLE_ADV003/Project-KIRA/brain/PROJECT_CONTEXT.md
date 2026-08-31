# PROJECT CONTEXT

Read this before touching anything. See `AGENTS.md` for the rules and
`.agents/rules/` for per-area detail.

<!-- AUTO-GENERATED BELOW - DO NOT HAND-EDIT -->

_Generated 2026-08-31 03:37 from artifacts and git. Do not edit below._

## Current state

- **Last gate passed:** 7
- **Git:** `e00a47e` on `main`
- **Latest run:** `run_fixture_0000` — FIXTURE (not real), scale `fixture`

## Gate ladder

| Gate | Name | Status | Last run |
|---|---|---|---|
| 0 | contracts | PASS | 2026-08-31T01:08:28 |
| 1 | world | PASS | 2026-08-31T01:08:34 |
| 2 | features | PASS | 2026-08-31T01:11:36 |
| 3 | blue | PASS | 2026-08-31T01:11:41 |
| 4 | red | PASS | 2026-08-31T01:11:54 |
| 5 | loop | PASS | 2026-08-31T01:12:36 |
| 6 | artifacts | PASS | 2026-08-31T01:26:16 |
| 7 | submission | PASS | 2026-08-31T01:16:45 |

## Live metrics

_Latest run is FIXTURE data. These are not measurements and must never_
_be cited in the report, the UI, or a commit message._

## What exists

- **BLOCK 0 — Foundation & unblock:** done
- **BLOCK 1 — Synthetic world + API/UI shell:** done
- **BLOCK 2 — Causal features + filter L1/L2/L4:** done
- **BLOCK 3 — Blue baseline + anchor:** partial (1/2)
- **BLOCK 4 — Red engine + filter L3:** partial (1/2)
- **BLOCK 5 — Closed loop + intent engine:** done
- **BLOCK 6 — Full cloud run:** done
- **BLOCK 7 — Evidence & docs:** done

## Open blockers

- None recorded. Check `brain/ERRORS.md` for anything not yet gated.

## Forbidden changes

- Do not hand-edit this file below the marker.
- Do not edit anything under `artifacts/` — it is generated.
- Do not weaken a gate assertion to make it pass.
- Do not add a dependency without a line in `brain/DECISIONS.md`.
- Do not build anything in the cut list (`.agents/rules/00-project.md`).
