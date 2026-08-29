---
title: Mastercard AI Defense Lab
emoji: 🛡️
colorFrom: indigo
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Mastercard AI Defense Lab

An adversarial payment-security laboratory. A stateful synthetic payment world
generates realistic transactions; a Red engine mutates **constrained** attacks
against a Blue detector; every successful evasion is analysed, replayed, and used
to harden a challenger model. We then measure whether the hardening actually
**generalises** rather than memorises.

> The YAML block above configures the Hugging Face Space. GitHub renders it as a
> table; that is expected.

## Quickstart

```bash
git clone <repo> && cd mastercard-ai-defense-lab
make setup
make gate 0          # contracts, fixtures, unit tests
make api             # http://localhost:8000/api/health
```

`make gate 0` writes a fixture artifact set, so the API and UI work before the
simulator exists. Anything served from fixtures is flagged `is_fixture: true` and
the UI shows a banner — fixture numbers never reach the report.

## What makes this more than a fraud classifier

Six things we measure that a standard detection project does not:

| | |
|---|---|
| **Behavioural fidelity** | Inter-event timing, burst structure, multi-account graph motifs and velocity-rule trigger rates, each normalised to real-data variability so `1.0` means indistinguishable from real. Published generators score 17×–99× on the same axes. |
| **Minimum Evasion Distance** | The smallest change to attacker-controllable fields that flips BLOCK to ALLOW. More honest than attack success rate, because it does not move when the threshold moves. |
| **ASR at a query budget** | Success rate for an attacker allowed 1, 5, 20 or 100 probes. Unlimited-query success describes an adversary that does not exist. |
| **Label-delay realism** | Chargebacks are slow, so any feature reading a neighbour's label is gated behind a 7-day availability lag. |
| **Held-out-variant hardening** | Blue hardens on variants 0–4 of an attack family; we report success on variants 5–9. Anything else measures memorisation. |
| **External reality anchor** | We also evaluate on a real public dataset, so the numbers mean something outside our own simulator. |

## Architecture

```
LOCAL (laptop)          KAGGLE CPU NOTEBOOK         HUGGING FACE
code, tests, gates  ->  scale: full, no GPU     ->  Dataset repo = artifacts
scale: tiny|small       generate/train/attack       Space = FastAPI + React
                        writes artifacts/<run_id>   serves, never computes
```

The laptop never trains at scale and the Space never computes. That makes the demo
structurally unable to fail the way live training fails, and it makes the latency
number from `/api/score` an honest end-to-end measurement over a real HTTP path.

No GPU is used anywhere — the whole pipeline is CPU tabular work.

## Gate ladder

Each gate asserts one invariant. When a number looks wrong, walk up the ladder;
the first failing gate names the layer that broke.

```bash
make gate 0   # contracts    schemas, fixtures, unit tests
make gate 1   # world        zero physics violations, FK integrity
make gate 2   # features     batch == stream, no future reads   <- the critical one
make gate 3   # blue         out-of-time split, beats rule baseline, ECE
make gate 4   # red          zero mask violations, ASR@budget, MED
make gate 5   # loop         held-out-variant ASR separate, no regression
make gate 6   # artifacts    every number traces to a run_id and reproduces
make gate 7   # submission   repo, docs, demo, no secrets
```

An unimplemented gate reports `PENDING` and exits 2. It never reports `PASS`.

## Layout

| Path | |
|---|---|
| `src/mcdl/` | the library — world, features, blue, red, loop, evaluation |
| `api/` | FastAPI: reads artifacts, returns schemas |
| `frontend/` | React + Vite; `dist/` is built locally and committed |
| `tools/` | `gates.py`, `brain_update.py` |
| `brain/` | live project state for humans and coding agents |
| `docs/` | shareable design and deployment notes |
| `notebooks/kaggle/` | the full run |

`AGENTS.md` and `.agents/rules/` are the contract for coding agents
(Antigravity, Cursor). `brain/PROJECT_CONTEXT.md` is generated — read it, do not
edit it.

## Data

The external anchor is the Sparkov-generated **Credit Card Transactions Fraud
Detection Dataset** (`kartik2112/fraud-detection` on Kaggle), which is **CC0
public domain**. It is downloaded, not committed. See `docs/DATA_PROFILE.md`.

## Safety

Everything runs on synthetic or public data in a controlled simulation. No real
cardholder data, no PII, no production payment systems, no attacks against live
services or third parties. This is a security research prototype, not an attack
platform. See `docs/LIMITATIONS.md`.
