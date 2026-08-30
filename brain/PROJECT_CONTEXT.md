# PROJECT CONTEXT

Read this before touching anything. See `AGENTS.md` for the rules and
`.agents/rules/` for per-area detail.

<!-- AUTO-GENERATED BELOW - DO NOT HAND-EDIT -->

_Generated 2026-08-31 00:54 from artifacts and git. Do not edit below._

## Current state

- **Last gate passed:** 7
- **Git:** `e5bcc80` on `main`
- **Latest run:** `run_tiny_s20260827_193f7897_e5bcc80` — real run, scale `tiny`

## Gate ladder

| Gate | Name | Status | Last run |
|---|---|---|---|
| 0 | contracts | PASS | 2026-08-31T00:44:56 |
| 1 | world | PASS | 2026-08-31T00:45:02 |
| 2 | features | PASS | 2026-08-31T00:48:17 |
| 3 | blue | PASS | 2026-08-31T00:48:23 |
| 4 | red | PASS | 2026-08-31T00:48:37 |
| 5 | loop | PASS | 2026-08-31T00:49:27 |
| 6 | artifacts | PASS | 2026-08-31T00:52:27 |
| 7 | submission | PASS | 2026-08-31T00:53:59 |

## Live metrics

- PR-AUC `0.800717` · ECE `0.0` · FPR `0.0`
- ASR held-out variants `0.0` · unseen family `not measured`
- Minimum Evasion Distance `0.0`
- Latency P50/P95/P99 `2.15` / `4.8` / `8.3` ms
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
