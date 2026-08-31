# docs/ — index

Every file here is standalone. You can send one to a teammate or paste one into an
agentic coder without the others and it still makes sense.

## Read in this order

| # | File | Read it when |
|---|---|---|
| 1 | [PROJECT.md](PROJECT.md) | You are new. Mission, thesis, scope, what "done" means. |
| 2 | [ARCHITECTURE.md](ARCHITECTURE.md) | Before touching any module. Three tiers, module map, data flow. |
| 3 | [DRAWBACKS.md](DRAWBACKS.md) | Before defending any design decision. The 15 real defects in the original idea and the fix for each. |
| 4 | [RESEARCH.md](RESEARCH.md) | Before citing anything. Every external claim, its source, and whether it was verified. |

## Building a specific layer

| File | Owner | Covers |
|---|---|---|
| [AI.md](AI.md) | B | Simulator, feature store, Blue detector, Red engine, closed loop, intent engine |
| [BACKEND.md](BACKEND.md) | A | FastAPI contract, artifact loading, latency measurement |
| [FRONTEND.md](FRONTEND.md) | A | The five views, controls, honest empty states |
| [EVALUATION.md](EVALUATION.md) | A | The five-layer realism filter, gate ladder, measurement protocols |
| [DATA_PROFILE.md](DATA_PROFILE.md) | B | **Template.** Fill it after profiling the reference dataset. |

## Operating

| File | Covers |
|---|---|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Hugging Face Space and Kaggle, click by click, assuming no prior knowledge |
| [ERRORS_PLAYBOOK.md](ERRORS_PLAYBOOK.md) | Failures we expect at each step, and the fix for each |
| [COMPETITION.md](COMPETITION.md) | **Template.** Fill it in the first 30 minutes. Everything inherits from it. |
| [LIMITATIONS.md](LIMITATIONS.md) | What we cut, why, and what we would do with more time. Goes into the report. |

## Where else the project state lives

- `../AGENTS.md` and `../.agents/rules/` — the contract every coding agent reads first
- `../brain/PROJECT_CONTEXT.md` — **generated**, current block and live metrics
- `../brain/HANDOFF.md` · `DECISIONS.md` · `CLAIMS.md` · `ERRORS.md` · `TASKS.md`

## One rule that applies to every file here

If a number appears in any document, it must trace to a `run_id` under
`artifacts/`. Documents describe **design and protocol**. Measurements live in
`brain/CLAIMS.md` and in run artifacts. A number typed into a doc by hand is not
a measurement.
