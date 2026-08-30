# PROJECT CONTEXT

Read this before touching anything. See `AGENTS.md` for the rules and
`.agents/rules/` for per-area detail.

<!-- AUTO-GENERATED BELOW - DO NOT HAND-EDIT -->

_Generated 2026-08-30 17:07 from artifacts and git. Do not edit below._

## Current state

- **Last gate passed:** 6
- **Git:** `4e838d6` on `main`
- **Latest run:** `run_tiny_s20260827_193f7897_4e838d6` — real run, scale `tiny`

## Gate ladder

| Gate | Name | Status | Last run |
|---|---|---|---|
| 0 | contracts | PASS | 2026-08-30T03:45:13 |
| 1 | world | PASS | 2026-08-30T03:45:18 |
| 2 | features | PASS | 2026-08-30T03:45:21 |
| 3 | blue | PASS | 2026-08-30T03:45:26 |
| 4 | red | PASS | 2026-08-30T03:50:19 |
| 5 | loop | PASS | 2026-08-30T04:02:05 |
| 6 | artifacts | PASS | 2026-08-30T17:07:06 |
| 7 | submission | not run | — |

## Live metrics

- PR-AUC `0.640716` · ECE `0.0` · FPR `0.000715`
- ASR held-out variants `0.0162` · unseen family `not measured`
- Minimum Evasion Distance `1.3291`
- Latency P50/P95/P99 `not measured` / `not measured` / `not measured` ms
- Filter L1 violations `0` · L4 C2ST row `not measured` entity `not measured`
- Filter L3 ratios — P1 `not measured` · P2 `not measured` · P3 `not measured` · P4 `not measured` (1.0 = real)
- External anchor: measured

## What exists

- **BLOCK 0 — Foundation & unblock:** done
- **BLOCK 1 — Synthetic world + API/UI shell:** done
- **BLOCK 2 — Causal features + filter L1/L2/L4:** done
- **BLOCK 3 — Blue baseline + anchor:** partial (1/2)
- **BLOCK 4 — Red engine + filter L3:** partial (1/2)
- **BLOCK 5 — Closed loop + intent engine:** done
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
