# ARCHITECTURE

Read this before touching any module.

---

## 1. Three tiers

```
+-- LOCAL (laptop) ------------+  +-- KAGGLE CPU NOTEBOOK -------+  +-- HUGGING FACE ---------+
|  Antigravity / Cursor        |  |  4 cores | ~30 GB | 12 h     |  |                         |
|  code, unit tests, gates     |  |  NO GPU QUOTA CONSUMED       |  |  Dataset repo           |
|  scale: tiny | small         |--|> scale: full                 |--|>  = artifact store      |
|  Vite dev server             |g |  generate / train / attack   |hf|        |                |
|  full pipeline smoke run     |it|  closed loop / full eval     |  |        v                |
+------------------------------+  |  writes artifacts/<run_id>/  |  |  Space (Docker)         |
                                  +------------------------------+  |   FastAPI + React       |
                                                                    |   2 vCPU | 16 GB | free |
                                                                    |   -> public demo URL    |
                                                                    +-------------------------+
```

### The rule

> **The laptop never trains at scale. The Space never computes.**

The Space reads artifacts and serves them. Two consequences, both deliberate:

1. The demo cannot fail the way live training fails. There is no model to load
   badly, no dataset to run out of memory on, no run to time out mid-presentation.
2. The latency number from `POST /api/score` is an honest end-to-end measurement
   over a real HTTP path, not a `predict()` call timed in a notebook.

### Why no GPU

The entire P0 path is CPU work: a stateful Python simulator, gradient-boosted
trees on tabular data, genetic search, and statistics. Kaggle CPU sessions
(4 cores, ~30 GB RAM, 12 h) **do not draw down the weekly GPU quota**, which is a
separate allocation. So the team's GPU hours stay intact for other projects.

The six-profile compute system in the original spec was designed around a
constraint that does not apply here. One config file with a `scale` flag replaces it.

## 2. Artifact flow

```
git push
   |
   v
Kaggle notebook clones the public GitHub repo
   |
   v
runs the pipeline at scale: full  ->  artifacts/<run_id>/
   |
   v
huggingface_hub upload_folder()  ->  HF Dataset repo
   |
   v
Space downloads at startup (snapshot_download)
   |
   v
FastAPI serves it; React renders it
```

Nothing is passed by hand. A number reaches the UI only by travelling this path.

## 3. Module map

```
src/mcdl/                     the library. Knows nothing about FastAPI. Never prints.
  schemas.py                  pydantic contracts. THE file that keeps A and B in sync.
  config.py                   loads configs/base.yaml, resolves scale, validates
  fixtures.py                 schema-valid FAKE artifacts. Unblocks parallel work.
  artifacts.py               run ids, manifests, typed loaders, HF push/pull

  world/                      the simulator          [BLOCK 1, owner B]
  features/
    spec.py                   ONE list of feature definitions
    batch.py                  polars, vectorised, for training
    stream.py                 dict state, one row, for serving
                              batch and stream MUST agree - see EVALUATION.md L3
  blue/                       model, calibration, decision router, shap, intent
  red/                        grammar, mutability mask, mutation search, ASR, MED
  loop/                       failure store, replay, challenger, promotion gate
  evaluation/
    validity.py               filter L1
    marginals.py              filter L2
    behavioral.py             filter L3  (P1-P4 + degradation ratio)
    c2st.py                   filter L4  (+ discriminator SHAP)
    tstr.py                   filter L5
    metrics.py                PR-AUC, ECE, FPR, ASR@budget, MED, cost curve

api/                          thin adapter: read artifact, call mcdl, return schema
frontend/                     React + Vite. dist/ is built locally and committed.
tools/                        gates.py, brain_update.py - things humans run
brain/                        live project state, for humans and coding agents
notebooks/kaggle/             the full run
artifacts/                    generated. Never hand-edited. Only demo/ is committed.
```

### Dependency direction

```
tools/  ->  mcdl/           (allowed)
api/    ->  mcdl/           (allowed)
mcdl/   ->  api/            FORBIDDEN
mcdl/   ->  fastapi         FORBIDDEN
```

`src/mcdl/` must remain importable and testable with no web server present.

## 4. Build order and what depends on what

```
schemas + config + fixtures        BLOCK 0
        |
        +----------------------------------+
        |                                  |
     world                            api + frontend
     BLOCK 1, B                       BLOCK 1, A  (built on FIXTURES)
        |                                  |
     features                              |
     BLOCK 2, B                            |
        |                                  |
     +--+--+                               |
     |     |                               |
   blue  evaluation                        |
   BLK 3 BLK 2-3, A                        |
     |     |                               |
     +--+--+                               |
        |                                  |
      red  BLOCK 4                         |
        |                                  |
      loop BLOCK 5                         |
        |                                  |
        +----------------+-----------------+
                         |
              full cloud run  BLOCK 6
                         |
              evidence + docs  BLOCK 7
```

The right-hand branch is the whole point of `fixtures.py`. A does not wait for B.

## 5. Contracts

Everything crossing a module boundary is a pydantic model in `src/mcdl/schemas.py`.
Two modules passing a raw dict is a bug waiting for day 3.

| Model | Crosses |
|---|---|
| `Transaction` | world -> features -> blue -> api -> ui |
| `Customer` `Merchant` `Device` `Mandate` | world -> everything |
| `MutabilityMask` | red internal, asserted in gate 4 |
| `AttackCandidate` | red -> blue -> loop |
| `BlueDecision` | blue -> api -> ui |
| `Counterfactual` | red -> api -> ui (Minimum Evasion Distance) |
| `FidelityReport` | evaluation -> api -> ui |
| `BlueMetrics` `RedMetrics` `RoundResult` | evaluation -> loop -> api -> ui |
| `RunManifest` `EvaluationResult` | the artifact contract |

`frontend/src/api.ts` mirrors these. **Change both in the same commit** so the UI
breaks loudly instead of rendering a wrong number silently.

### The observable / hidden split

`Transaction` separates fields the Blue team may see from hidden evaluation
metadata (`is_fraud`, `attack_family`, `attack_instance_id`, `attack_variant`,
`hard_negative`). Gate 0 asserts the two lists are disjoint and jointly cover every
field. Leaking a hidden field into the feature set is the fastest possible route to
a fake 0.99 PR-AUC.

## 6. The artifact contract

Every run writes:

```
artifacts/<run_id>/
  manifest.json               git commit, config hash, seed, scale, timings, is_fixture
  evaluation.json             FidelityReport + rounds + anchor + ablations
  transactions.json           the replay stream the UI reads
  decisions.json              one BlueDecision per transaction
  counterfactual_sample.json  Minimum Evasion Distance examples
artifacts/LATEST              pointer to the active run_id
artifacts/gates.json          which gates ran, when, and what they found
```

`manifest.is_fixture` is load-bearing. When true the API surfaces it, the UI shows
a FIXTURE banner, and gate 6 fails. Fixture numbers can never reach the report.

## 7. Config

One file: `configs/base.yaml`. One knob: `scale` ∈ `tiny | small | full`.

| scale | customers | merchants | days | events | runs on |
|---|---|---|---|---|---|
| tiny | 200 | 80 | 30 | 10k | laptop, ~2 min |
| small | 1,000 | 300 | 90 | 50k | laptop, gate runs |
| full | 10,000 | 800 | 365 | 1M | Kaggle CPU |

Resolution order: explicit argument > `MCDL_SCALE` env var > file value.

Config validation fails at load time rather than three modules later. It asserts:
archetype shares sum to 1.0, split fractions sum to 1.0, hidden families are a
non-empty subset of all families, and `harden_on_variants < variants_per_family`
(otherwise there are no held-out variants and the closed loop can only measure
memorisation).

## 8. Scalability — honest numbers

| Component | Reality at 1M rows | Verdict |
|---|---|---|
| Stateful simulator | 5k–50k events/sec in Python; 1M is 20–200 s | fine |
| polars analysis / joins | comfortable past 1M on a laptop | fine |
| LightGBM training | minutes on CPU at 1M x 100 | fine |
| Causal feature build | fine **if** expressed as polars rolling/group-by windows; fatal as a Python row loop | watch |
| Graph features via networkx | too slow at 1M. Use group-by aggregations; reserve networkx for the small subgraphs the UI draws | watch |
| Attack search | **the actual wall.** Score the whole population in one call | blocker if naive |
| SHAP | TreeSHAP is fast per row but not free. On demand only, never batch | watch |
| The Space at 1M rows | do not. Pre-aggregate; downsample the replay stream to ~20k rows | watch |

On the 1M target: it buys one sentence in the report and costs generation time,
iteration time, and a class of memory bugs during the days you most need fast
iteration. **Develop the whole pipeline at 50k. Generate 1M once, late, and only
if everything already works at 50k.**

## 9. Failure localisation

Each gate asserts one invariant. When a downstream number looks wrong, walk **up**
the ladder — the first failing gate names the layer that broke.

| Gate | Invariant | A failure means |
|---|---|---|
| 0 | Schemas validate; fixtures generate; contracts disjoint | A and B have drifted apart |
| 1 | Zero physics violations; FK integrity | Simulator bug; everything downstream is meaningless |
| 2 | **batch == stream; no feature reads after `t`** | **Leakage — the bug that looks like success** |
| 3 | Out-of-time split enforced; beats rule baseline; ECE recorded | Circular evaluation; the headline is fiction |
| 4 | Zero mask violations; attacks pass L1; query budget logged | Attacks are cheating; ASR is indefensible |
| 5 | Held-out-variant ASR separate; no regression | Measuring memorisation, not hardening |
| 6 | Every number traces to a run_id and reproduces; not a fixture | Cannot defend it in the report |
| 7 | Submission audit | Not ready to submit |

An unimplemented gate reports `PENDING` and exits 2. It never reports `PASS`.

Full detail in [EVALUATION.md](EVALUATION.md).
