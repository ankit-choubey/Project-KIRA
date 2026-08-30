# TASKS

Status vocabulary: `todo` · `wip` · `blocked` · `done`.
A block is `done` only when its gate has actually been run and passed.

| Block | Owner | Task | Gate | Status |
|---|---|---|---|---|
| 0 | A | Repo, contracts, fixtures, gates, brain, Dockerfile | 0 | **done** |
| 0 | A | Deploy hello-world HF Space, confirm `/api/health` 200 from the public URL | 0 | todo |
| 0 | B | Download Sparkov, write `docs/DATA_PROFILE.md` | 0 | todo |
| 0 | any | **Verify the competition page** -> `docs/COMPETITION.md` (deliverables, deadline + timezone, leaderboard?) | 0 | todo |
| 1 | B | Stateful world: 4 archetypes, merchants, devices, ledger, 3 hard negatives, agents | 1 | todo |
| 1 | A | Five React views on the fixture API; `make frontend`; redeploy | 1 | todo |
| 2 | B | `features/spec.py` -> batch + stream, both generated from one spec | 2 | todo |
| 2 | A | Filter L1 validity, L2 marginals, L4 C2ST + discriminator SHAP | 2 | todo |
| 3 | B | LightGBM + isotonic calibration + cost router + TreeSHAP | 3 | todo |
| 3 | A | Temporal split assertions, metrics, external anchor, TSTR, ablation runner | 3 | todo |
| 4 | B | Attack grammar, mutability mask, batch-vectorised search, ASR@budget, MED | 4 | todo |
| 4 | A | Filter L3 (P1–P4 + degradation ratio); Red Console live | 4 | todo |
| 5 | B | Failure store -> replay -> challenger -> promotion gate, 3 rounds | 5 | todo |
| 5 | A | Intent engine (mandate object, violation vector, MCC distance, no LLM) | 5 | todo |
| 6 | B | Kaggle full run -> artifacts -> HF Dataset | 6 | **done** |
| 6 | A | Space pulls real artifacts; latency measured over HTTP | 6 | **done** |
| 7 | B | Adaptive Red/Blue Co-Evolution Engine, Failure Analysis, EXP-007-A..H | 7 | **wip** |
| 7 | A | Report, DOCX, writeup, README, claim register, limitations, demo video | 7 | todo |
| 8 | both | Prototype & Evidence Integration (UI Mission Control) | — | todo |

## Standing rules

1. If a gate fails, fix the cause. Do not weaken the assertion, and do not start the
   next block on top of a failing gate.
2. At the end of day 1, **both** people run the full pipeline from a clean clone.
   A two-person team with one person who can debug the ML has a single point of failure.
3. A starts writing the report on day 2 with placeholders wired to `CLAIMS.md`.
   Writing on day 3 on top of debugging on day 3 is how submissions get missed.
