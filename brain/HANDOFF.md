# HANDOFF

Append-only. Newest entry at the top. One entry per block handoff.

Never write "done". Write what changed, what you ran, and what the gate said.

---

## 2026-08-29 · BLOCK 0 · Claude -> A & B

**BLOCK:** 0 — Foundation & unblock

**DONE:** Repo skeleton, agent contract (`AGENTS.md`, `GEMINI.md`, `.agents/rules/`),
`brain/`, pydantic contracts, config loader with validation, fixture generator,
gate runner (0..7), brain updater, FastAPI with all endpoints on fixtures,
Dockerfile for HF Spaces, Makefile, 26 unit tests.

**FILES:** `src/mcdl/{schemas,config,fixtures,artifacts}.py` · `tools/{gates,brain_update}.py`
· `api/main.py` · `tests/unit/*` · `Dockerfile` · `Makefile` · `configs/base.yaml`

**COMMANDS RUN:**

```
python -m pip install pytest ruff polars lightgbm httpx
python -m tools.gates 0
python -m tools.brain_update
```

**GATE RESULT:** GATE 0 PASSED — 10/10 checks, `pytest tests/unit` 26 passed.
API smoke-tested: every endpoint returns 200, or an honest 501/404. The fixture
flag is surfaced on every response and unmeasured fields return `null`, not `0`.

**BLOCKERS:**

- `docs/COMPETITION.md` is a stub. Someone must open the actual competition page
  and confirm deliverables, deadline **and timezone**, and whether a leaderboard
  exists. Everything downstream inherits from that page.
- Reference dataset not yet downloaded (`kartik2112/fraud-detection`, CC0).

**NEXT:**

- **B** -> BLOCK 1: download and profile Sparkov into `docs/DATA_PROFILE.md`, then
  build the stateful world in `src/mcdl/world/`. Target: gate 1.
- **A** -> BLOCK 1: build the five React views against the fixture API, run
  `make frontend`, deploy the Space. Target: `/api/health` 200 from the public URL.
