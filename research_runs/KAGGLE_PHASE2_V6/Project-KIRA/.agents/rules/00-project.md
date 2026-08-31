# 00 — What this project is

## The thesis

Traditional fraud detection asks *"does this transaction look fraudulent?"*.
This project asks *"what would an adaptive attacker do against **this specific
detector**, and does hardening against those attacks generalise?"*

The deliverable is not a model. It is **evidence**: a set of measured results
where each number traces to a reproducible run, plus a live web app a judge can
click through to see the loop working.

## The loop

```
Synthetic payment world  →  causal features  →  Blue detector  →  decision policy
        ↑                                                              │
        │                                                              ▼
   Red mutates attacks under constraints  ←  failure store  ←  successful evasions
        │
        └→ harden a challenger → promotion gate → new champion → Red attacks again
```

## What makes this defensible rather than another fraud classifier

Six measured things most teams will not have:

1. **Behavioural fidelity (P1–P4)** with a degradation ratio normalised to
   real-data variability. 1.0 = indistinguishable from real. Published generators
   score 17×–99× on the same axes, so we have a baseline to beat.
2. **Minimum Evasion Distance** — the smallest change to attacker-controllable
   fields that flips BLOCK → ALLOW. More honest than ASR because it does not move
   when you move the threshold.
3. **ASR at a query budget** — success rate for an attacker allowed 1, 5, 20 or
   100 probes. Unlimited-query ASR describes an adversary that does not exist.
4. **Label-delay realism** — chargebacks are slow, so any feature reading a
   neighbour's label is gated behind a 7-day lag.
5. **Held-out-variant hardening** — Blue hardens on variants 0–4 of a family and
   we report ASR on variants 5–9. Anything else measures memorisation.
6. **External reality anchor** — we also evaluate on a real public dataset, so
   the numbers mean something outside our own simulator.

## Scope — locked

**In:** stateful world (4 archetypes, 3 hard negatives, agents with mandates),
causal feature store, LightGBM + calibration + cost router, intent-drift engine,
5 attack families, constrained mutation search, 3-round closed loop, 5-layer
realism filter, FastAPI + React app on a Hugging Face Space, full docs.

**Out — do not build these, they were cut deliberately:** GNN of any kind, RL
(PPO/DQN), diffusion/TabDDPM, STG-DGR, generative replay, EWC, distillation,
conformal prediction, ADWIN, PSRO, RAG investigator, Weights & Biases, CatBoost,
per-machine compute profiles. In a 3-day build none of these produces a
defensible measured result, and a half-working one is a liability in the report.

If you think one of these is needed, write the argument in `brain/DECISIONS.md`.
Do not just build it.

## Honesty rules — these are not style preferences

- A number that is not in an artifact file does not exist. Do not put it in a
  docstring, a comment, a report, or the UI.
- "Not measured" is an acceptable value everywhere, including the UI. A zero
  standing in for an unmeasured value is a lie that will be found.
- If a result looks too good (PR-AUC ≈ 0.99), treat it as a **bug report**, not a
  success. It almost always means leakage or the detector learning a generator
  rule. Go back to gate 2.
- We state what we cut and why. Silence about limitations reads as ignorance.

## Two people

- **A** — infra, contracts, evaluation, API, frontend, deploy, docs.
- **B** — simulator, features, models, red engine, closed loop, Kaggle runs.

Neither waits for the other: `src/mcdl/fixtures.py` emits schema-valid fake
artifacts so the API, UI, evaluation harness and report can all be built before
the real pipeline exists. Swapping to real artifacts is a path change.
