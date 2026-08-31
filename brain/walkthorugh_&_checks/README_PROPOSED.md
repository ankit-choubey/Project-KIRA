---
title: Project KIRA — AI Defense Lab
emoji: 🛡️
colorFrom: indigo
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Project KIRA — Adversarial Co-Evolution Laboratory for Payment Security

**Mastercard Innovation Challenge 2026 · Track: AI Defense Lab for Payment Security**

A closed-loop payment-security laboratory. A stateful synthetic payment world generates
realistic transactions. A budgeted Red engine mutates **constrained** attacks against a
Blue detector. Every successful evasion is classified into a 12-class failure taxonomy,
replayed into a prioritised buffer, and used to train a challenger — which a
multi-objective promotion gate then accepts or **rejects**.

We measure whether that hardening **generalises** rather than **memorises**, and we
report the boundary where it stops working.

> The YAML block above configures the Hugging Face Space. GitHub renders it as a table;
> that is expected.

---

## Headline results

**Authoritative run:** `run_tiny_s20260827_193f7897_40997ab` · commit `40997ab` · seed `20260827`

| | | |
|---|---|---|
| **Attacker beats unhardened detector** | 96.67% @ 20 probes | EXP-007-A |
| **After hardening, held-out variants** | 14.55% → **0.00%** | `promotion_history.json` |
| **Challengers promoted** | **0 of 4** — all rejected on detection collapse | `promotion_history.json` |
| **Zero-day transfer (withheld families)** | **100.00% ASR** — measured failure | EXP-007-E |
| **Real-world anchor** (284,807 real txns) | PR-AUC **0.8640** | `external_anchor.json` |
| **Scoring latency** (HTTP loopback) | P50 2.287 / P95 2.406 / P99 2.503 ms | `latency_benchmark.json` |
| **Mask violations · invalid attacks** | **0 · 0** | `red_metrics.json` |
| **Verification** | Gates 0–7 PASS · 152/152 tests · 22/22 SHA-256 | — |

⚠️ `tiny`-scale PR-AUC is **1.0000** and is a **small-sample artifact** — only 5 positives
in the validation slice. The statistically meaningful figure is **0.9375** at `small`
scale. See [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md).

---

## Quickstart

```bash
git clone https://github.com/ankit-choubey/Project-KIRA.git
cd Project-KIRA
make setup
make gate 0            # contracts, fixtures, unit tests
make api               # http://localhost:8000/api/health
```

Full pipeline at laptop scale (~20 s on CPU):

```bash
PYTHONPATH=src python -m mcdl.pipeline --scale tiny --rounds 4
```

Frontend + API together:

```bash
make dev               # FastAPI :8000 + Vite :5173, /api proxied
```

**No GPU is used anywhere in this project.** The entire path is CPU tabular work.

---

## What makes this more than a fraud classifier

Seven things we measure that a standard detection project does not:

| | |
|---|---|
| **ASR at a query budget** | Success rate for an attacker allowed 1, 5, 20 or 100 probes. Unlimited-query success describes an adversary nobody faces. |
| **Minimum Evasion Distance** | The smallest normalised perturbation that flips a protected decision to ALLOW. Does not move when the threshold moves. |
| **Lineage-grouped held-out variants** | Variants grouped by `(source_txn_id, family)` *before* the challenger trains. Anything else measures memorisation. |
| **12-class failure taxonomy** | W1–W12. Converts "the attack worked" into "the defense has this specific blind spot". |
| **Multi-objective promotion gate** | Detection, robustness, anti-forgetting, calibration, FPR, approval rate, latency — all simultaneously, or rollback. |
| **Three-world isolation** | World C holds back entire attack families. Family-set disjointness asserted at runtime. |
| **External reality anchor** | 284,807 real transactions, never used for training. |

---

## Architecture

```
LOCAL (laptop)              KAGGLE CPU NOTEBOOK           SERVING
code, tests, gates    -->   scale: full, no GPU     -->   Dataset repo = artifacts
scale: tiny | small         generate/train/attack         FastAPI + React
                            writes artifacts/<run_id>     serves, never computes
```

**The laptop never trains at scale. The serving layer never computes.**

Two consequences, both deliberate: the demo cannot fail the way live training fails, and
the latency number is an honest end-to-end HTTP measurement rather than a `predict()` call
timed in a notebook.

### The loop

```
Synthetic payment world
        |
        v
   causal features  --->  Blue champion  --->  policy router (ALLOW/STEP_UP/BLOCK)
        ^                                            |
        |                                            v
   challenger  <---  prioritised replay  <---  failure analysis (W1..W12)
        |                                            ^
        v                                            |
  promotion gate --> PROMOTE or ROLLBACK --> Red attacks the current champion again
```

Full detail: [`docs/architecture/COEVOLUTION_ENGINE.md`](docs/architecture/COEVOLUTION_ENGINE.md)

---

## Project structure

```
src/mcdl/                 the library. Knows nothing about FastAPI. Never prints.
  schemas.py              pydantic contracts — keeps every module in sync
  config.py               loads configs/base.yaml, resolves scale, validates at load time
  fixtures.py             schema-valid FAKE artifacts, flagged is_fixture
  artifacts.py            run ids, manifests, typed loaders, SHA-256 provenance
  pipeline.py             the end-to-end orchestrator

  world/                  stateful simulator — archetypes, merchants, devices, ledger
  features/
    spec.py               ONE list of 25 causal feature definitions
    batch.py              polars, vectorised, for training
    stream.py             dict state, one row, for serving
                          batch and stream MUST agree — Gate 2
  blue/                   model · isotonic calibration · cost router · TreeSHAP · intent
  red/
    mask.py               declarative mutability mask
    search.py             budgeted black-box search with provenance
    adaptive.py           weakness-driven adaptive Red engine
    distance.py           Minimum Evasion Distance
  loop/
    failure.py            12-class taxonomy, weakness profiling
    replay.py             prioritised replay buffer, zero metadata leakage
    split.py              lineage-grouped seen/held-out split
    promotion.py          multi-objective gate with deterministic rollback
    worlds.py             three-world suite with runtime isolation assertion
    coevolution.py        the round loop
  evaluation/
    validity.py           filter L1 — physics
    anchor.py             external real-world benchmark
    experiments.py        EXP-007-A .. EXP-007-H
  research/               Phase-1/2 validation — C2ST, TSTR, L3 fidelity, graph audit

api/                      thin adapter: read artifact, return schema
frontend/                 React + Vite + TypeScript
tools/                    gates.py · brain_update.py · benchmark_latency.py · run_*.py
brain/                    live project state — CLAIMS.md is the claim register
docs/                     architecture, evaluation, limitations, deployment
notebooks/kaggle/         cloud runs
artifacts/<run_id>/       generated. Never hand-edited.
research_runs/            independent validation tracks S-00 .. S-05
tests/                    unit · invariants · e2e — 152 tests
```

---

## The gate ladder

Each gate asserts one invariant. When a downstream number looks wrong, walk **up** the
ladder — the first failing gate names the layer that broke.

```bash
make gate 0   # contracts    schemas, fixtures, disjoint observable/hidden fields
make gate 1   # world        zero physics violations, FK integrity
make gate 2   # features     batch == stream, no future reads      <- the critical one
make gate 3   # blue         out-of-time split, beats rule baseline, ECE recorded
make gate 4   # red          zero mask violations, ASR@budget, MED
make gate 5   # loop         held-out ASR reported separately, no regression
make gate 6   # artifacts    every number traces to a run_id and reproduces
make gate 7   # submission   repo, docs, demo, no secrets
```

An unimplemented gate reports `PENDING` and exits 2. **It never reports `PASS`.**

Current status: **Gates 0–7 PASS**.

---

## Pipeline usage

### Run the full pipeline

```bash
PYTHONPATH=src python -m mcdl.pipeline --scale tiny  --rounds 4    # ~20 s
PYTHONPATH=src python -m mcdl.pipeline --scale small --rounds 4    # laptop
MCDL_SCALE=full python -m mcdl.pipeline                            # Kaggle CPU
```

Writes `artifacts/<run_id>/` with 25 artifacts, validates schema and ranges, verifies
SHA-256 integrity, marks the run finalised, and updates `artifacts/LATEST`.

### Run the experiment matrix

```bash
python -m tools.run_experiments        # EXP-007-A .. EXP-007-H
python -m tools.run_coevolution        # co-evolution rounds only
python -m tools.benchmark_latency      # LATENCY-002, /api/score
```

### Scale presets

| scale | customers | merchants | days | events | runs on |
|---|---|---|---|---|---|
| tiny | 200 | 80 | 30 | ~9.3k | laptop, ~20 s |
| small | 1,000 | 300 | 90 | ~50k | laptop |
| full | 10,000 | 800 | 365 | 1M | Kaggle CPU |

Resolution order: explicit argument → `MCDL_SCALE` env var → `configs/base.yaml`.

---

## The artifact contract

Every run writes an immutable, hash-verified directory:

```
artifacts/<run_id>/
  manifest.json               commit, config hash, seed, scale, stage timings
  evaluation.json             fidelity + rounds + anchor + ablations
  scoreboard.json             per-round 15-metric scoreboard
  coevolution_metrics.json    per-round, per-family breakdown
  promotion_history.json      every gate decision and its reasons
  weakness_profile.json       W1..W12 distribution, reseeding weights
  failures.json               every diagnosed evasion
  experiment_register.json    EXP-007-A .. H with hypothesis and conclusion
  three_world_evaluation.json World A/B/C isolation proof
  attack_summary.json         representative attack samples
  intent_ablation.json        EXP-007-H controlled counterfactual
  latency_benchmark.json      LATENCY-002
  external_anchor.json        ULB benchmark + citation
  adaptation_cost.json        compute cost per round
  blue_metrics.json  red_metrics.json  policy_metrics.json  calibration.json
  feature_schema.json  world_summary.json
  transactions.json  decisions.json  sample_transactions.json
  evidence_pack.md            human-readable audit report
  provenance.json             SHA-256 for every file above
artifacts/LATEST              pointer to the active run_id
```

`manifest.is_fixture` is load-bearing. When true, the API surfaces it, the UI shows a
FIXTURE banner, and Gate 6 fails. **Fixture numbers can never reach the report.**

---

## API

```
GET  /api/health                 run_id, is_fixture, artifacts_loaded
GET  /api/config                 scale, families, hidden families, query budgets
GET  /api/runs                   available run ids
GET  /api/stream?offset&limit    replayed transactions + decisions
GET  /api/transaction/{txn_id}   one transaction, decision, counterfactual
POST /api/score                  score one transaction — the timed endpoint
GET  /api/coevolution            per-round results incl. promotion decisions
GET  /api/evidence               full EvaluationResult
```

The API is a thin adapter. It reads artifacts and returns pydantic schemas. It never
trains, never computes a metric, and never derives a number the artifacts do not contain.

---

## Honesty rules

These are not style preferences. They are what makes the submission defensible.

1. **A number that is not in an artifact file does not exist.** Not in a docstring, not in
   a comment, not in the report, not in the UI.
2. **"Not measured" is a valid value everywhere**, including the UI. A zero standing in for
   an unmeasured value is a lie that will be found.
3. **If a result looks too good, treat it as a bug report.** This is why `tiny`-scale
   PR-AUC 1.0 is labelled a small-sample artifact rather than celebrated.
4. **We state what we cut and why.** Silence about limitations reads as ignorance; stated
   reasoning reads as judgement.
5. **A gate that has not been run is never described as passing.**

---

## Limitations

We report three negative results as first-class findings:

- **Zero-day transfer failed completely** — 100% ASR against withheld attack families.
- **Every challenger was rejected** by the promotion gate on detection collapse.
- **The Verifiable-Intent ablation was neutral** — ΔASR 0.00%.

Plus: synthetic data is distinguishable from real (C2ST AUC 0.7780 against a 0.5025
self-split sanity baseline), synthetic-to-real transfer is weak (TSTR 0.0271 vs TRTR
0.4060), L3/L4 filter layers are partially unmeasured, and the latency figure is an
in-process loopback benchmark rather than internet latency.

Full detail: [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) · claim register:
[`brain/CLAIMS.md`](brain/CLAIMS.md)

---

## Data

External anchor: **ULB European Credit Card Fraud benchmark** — Dal Pozzolo et al., 2015,
DOI [`10.1109/SSCI.2015.33`](https://doi.org/10.1109/SSCI.2015.33). 284,807 transactions,
492 frauds. Never used for training.

Research validation: **Sparkov Credit Card Fraud benchmark**
(`kartik2112/fraud-detection`), **CC0 1.0 Public Domain**, SHA-256 `12d553ab…545f0`.
Downloaded, not committed.

---

## Safety

Everything runs on synthetic data and open-access public benchmarks. No real cardholder
data, no PII, no production payment systems, no attacks against live services or third
parties. This is a security research prototype, not an attack platform.

KIRA is **not** an official implementation of Mastercard Verifiable Intent, Agent Pay,
AP2, or EMV 3DS. The `Mandate` object is our own prototype mechanism, informed by the
publicly described problem those frameworks address.

---

## License

Code released under MIT. Reference datasets retain their original licences (ULB benchmark:
see publication; Sparkov: CC0 1.0).
