# HANDOFF

Append-only. Newest entry at the top. One entry per block handoff.

Never write "done". Write what changed, what you ran, and what the gate said.

---

## 2026-08-30 · BLOCK 2 Independent Batch Rebuild & Gate 2 Pass · Antigravity

**BLOCK:** 2 — Causal Feature Store Independent Batch Vectorisation & Invariant Parity.

**DONE:** Rebuilt `src/mcdl/features/batch.py` completely independently using Polars expressions, vectorised epoch arithmetic, and prefix sums, completely removing any dependency on `StreamingFeatureExtractor`. Updated `src/mcdl/features/stream.py` to preserve exact IEEE-754 precision without artificial rounding. Expanded `tests/invariants/test_batch_stream_parity.py` with 9 targeted tests covering exact parity across 1,000+ world transactions, same-timestamp ordering, exact 1h/6h/24h window boundaries, first-transaction defaults, 7-day label lag cutoffs, future transaction perturbations, future unconfirmed fraud-label perturbations, hand-computed fixtures, and intentional corruption failure proofs.

**FILES:** `src/mcdl/features/batch.py`, `src/mcdl/features/stream.py`, `tests/invariants/test_batch_stream_parity.py`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit
python3 -m pytest tests/invariants -v
python3 -m pytest tests/
python3 -m tools.gates 2
python3 -m tools.gates all
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 2 PASSED (Independent Polars batch and dict stream agree <= 1e-9 across all 25 features, all 72 tests pass, causality and label lag verified).

## 2026-08-30 · BLOCK 2 Pre-Implementation Contract · Antigravity

**NEXT:** BLOCK 3 — Blue team baseline & calibration (`src/mcdl/blue/`). Target: Gate 3.

## 2026-08-30 · BLOCK 2 Pre-Implementation Contract · Antigravity

**BLOCK:** 2 — Causal Feature Store Mathematical Specification & Contract Freezing.

**DONE:** Created single source of truth `src/mcdl/features/spec.py` defining 20 canonical features across 7 feature groups. Formally specified:
- Deterministic lexicographic causal ordering: $(timestamp, txn\_id)$ ascending.
- Historical temporal window bounds: $W_\Delta(T_i) = \{ T_j \mid T_j \prec T_i \land t_i - \Delta \le t_j \le t_i \}$.
- Strict exclusion of current transaction $T_i$ from all historical aggregations (no self-leakage).
- Exact 7-day chargeback label availability cutoff ($t_j \le t_i - 604,800\text{s}$).
- Explicit first-history/default non-null values for all stateful/relational features.
Added unit test suite `tests/unit/test_feature_spec.py` verifying exact boundary edge cases. Did not implement `batch.py` or `stream.py` (pre-implementation phase).

**FILES:** `src/mcdl/features/spec.py`, `tests/unit/test_feature_spec.py`, `brain/HANDOFF.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit
python3 -m tools.gates 1
```

**GATE RESULT:** Gate 2 not claimed (pre-implementation phase). All 44 unit tests passing. Gate 1 remains PASS (14/14).

## 2026-08-30 · BLOCK 1 Sequential Balance Audit · Antigravity

**BLOCK:** 1 — Implementation of sequential inter-transaction balance consistency verification.

**DONE:** Updated `src/mcdl/evaluation/validity.py` to independently audit sequential balance transitions across consecutive customer transactions $(T_k, T_{k+1})$, verifying that $T_{k+1}.\text{balance\_before}$ matches either unsettled transition $\text{round}(B_k + A_k, 2)$ or periodic settlement $\text{round}(\text{round}(B_k + A_k, 2) \times 0.35, 2)$. Enhanced regression tests in `tests/unit/test_world.py` to test both intra-transaction identity and inter-transaction sequential mismatch detection. Updated `D-008` in `brain/DECISIONS.md`.

**FILES:** `src/mcdl/evaluation/validity.py`, `tests/unit/test_world.py`, `brain/DECISIONS.md`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit
python3 -m tools.gates 1
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 1 PASSED — 14/14 checks passed (39/39 unit tests green).

## 2026-08-30 · BLOCK 1 Audit & Invariant Regression Suite · Antigravity

**BLOCK:** 1 — Focused audit of Layer-1 validity and invariant regression suite.

**DONE:** Expanded `src/mcdl/evaluation/validity.py` with balance transition consistency checking (`balance_before + available_credit == credit_limit` and `balance_before <= credit_limit`). Added 9 targeted regression tests in `tests/unit/test_world.py` verifying detection of inconsistent balance transitions, negative/invalid transaction amounts, credit-limit boundary breaches, timestamp non-monotonicity, device registration ordering anomalies, invalid MCC formats, impossible travel speeds, foreign-key referential errors, and mandate amount violations. Documented architectural decision `D-008` in `brain/DECISIONS.md`.

**FILES:** `src/mcdl/evaluation/validity.py`, `tests/unit/test_world.py`, `brain/DECISIONS.md`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit
python3 -m tools.gates 1
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 1 PASSED — 14/14 checks passed (13/13 in test_world.py, 39/39 total unit tests green).

## 2026-08-30 · BLOCK 1 · Antigravity

**BLOCK:** 1 — Synthetic payment world + Layer 1 physical validity

**DONE:** Implemented stateful payment world simulator in `src/mcdl/world/` (`archetypes.py`, `entities.py`, `ledger.py`, `hard_negatives.py`, `generator.py`), Layer 1 validity assertions in `src/mcdl/evaluation/validity.py`, unit test suite in `tests/unit/test_world.py`, and Gate 1 verification in `tools/gates.py`. All 14/14 checks pass with zero physical or invariant violations.

**FILES:** `src/mcdl/world/{__init__,archetypes,entities,ledger,hard_negatives,generator}.py`, `src/mcdl/evaluation/validity.py`, `tests/unit/test_world.py`, `tools/gates.py`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit
python3 -m tools.gates 1
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 1 PASSED — 14/14 checks passed (9346 transactions generated, 0 balance violations, 0 timestamp violations, 0 device registration violations, 0 MCC violations, 0 geo speed violations, 0 FK violations, 0 mandate violations, hard negatives and base fraud present, 30 unit tests green).

**NEXT:** BLOCK 2 — Causal feature store (`batch.py`, `stream.py`, `spec.py`) and batch/stream parity tests. Target: Gate 2.

## 2026-08-30 · Project-KIRA GitHub Setup & Gate 0 Full Pass · Antigravity

**BLOCK:** Project-KIRA repo creation, frontend build, and Gate 0 verification.

**DONE:** Created new public GitHub repository `Project-KIRA` under `ankit-choubey`, updated git remote to `https://github.com/ankit-choubey/Project-KIRA.git`, built frontend distribution (`frontend/dist`), and verified Gate 0 (12/12 checks passing).

**FILES:** `frontend/dist/*`, `frontend/package-lock.json`, `brain/PROJECT_CONTEXT.md`, `brain/HANDOFF.md`.

**COMMANDS RUN:**
```bash
# Created GitHub repo Project-KIRA via GitHub API / MCP
git remote set-url origin https://github.com/ankit-choubey/Project-KIRA.git
cd frontend && npm install && npm run build
python3 -m tools.gates 0
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 0 PASSED (12/12 checks, pytest 26 unit passed, 19 e2e passed, frontend built).

## 2026-08-29 · Git Push · Antigravity

**BLOCK:** Git repository setup and push to GitHub.

**DONE:** Initialized local Git repository, created `main` branch, added remote `origin` pointing to `https://github.com/Devrajsahani/MasterCard-AI.git`, added and committed all files, and successfully pushed the codebase.

**FILES:** All codebase files.

**COMMANDS RUN:**
```bash
git init
git checkout -b main
git remote add origin https://github.com/Devrajsahani/MasterCard-AI.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

**GATE RESULT:** No block gates changed. `git push` succeeded with exit code 0.

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
