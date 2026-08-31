# PROJECT — Mastercard AI Defense Lab

The single entry point. If you read one file before working on this project,
read this one.

---

## 1. What we are building

An **adversarial payment-security laboratory**.

A stateful synthetic payment world generates realistic transactions. A Red engine
mutates constrained attacks against a Blue detector. Every successful evasion is
analysed, stored, and replayed to harden a challenger model. We then measure
whether that hardening actually **generalises** rather than memorises.

The deliverable is not a model. It is **evidence**, plus a live web app a judge
can click through and see the loop working.

## 2. The thesis

Traditional fraud detection asks:

> "Does this transaction look fraudulent?"

We ask:

> "What would an adaptive attacker do against **this specific detector**, and does
> hardening against those attacks transfer to attacks we have never seen?"

That second question is the whole project. Everything that does not serve it is
out of scope.

## 3. The loop

```
Synthetic payment world
        |
        v
   causal features  ---->  Blue detector  ---->  decision policy (ALLOW/STEP_UP/BLOCK)
        ^                                              |
        |                                              v
   challenger model  <---  replay buffer  <---  successful evasions
        |                                              ^
        v                                              |
  promotion gate ---> new champion ---> Red attacks again
```

## 4. What makes this defensible rather than another fraud classifier

Six things we measure that a standard detection project does not. These are the
project. If you are ever choosing what to cut, cut anything else first.

| | What | Why it matters |
|---|---|---|
| 1 | **Behavioural fidelity (P1–P4)** with a degradation ratio normalised to real-data variability | 1.0 means indistinguishable from real. Published generators score 17×–99× on the same axes, so there is a baseline to beat rather than a vibe to assert |
| 2 | **Minimum Evasion Distance** | The smallest change to attacker-controllable fields that flips BLOCK to ALLOW. More honest than attack success rate because it does not move when the threshold moves |
| 3 | **ASR at a query budget** | Success rate for an attacker allowed 1, 5, 20 or 100 probes. Unlimited-query success describes an adversary nobody actually faces |
| 4 | **Label-delay realism** | Chargebacks are slow. Any feature reading a neighbour's label is gated behind a 7-day availability lag |
| 5 | **Held-out-variant hardening** | Blue hardens on variants 0–4 of a family; we report success on variants 5–9. Anything else measures memorisation |
| 6 | **External reality anchor** | We also evaluate on a real public dataset, so the numbers mean something outside our own simulator |

See [DRAWBACKS.md](DRAWBACKS.md) for why each of these exists — every one is a fix
for a specific defect found in the original project design.

## 5. Scope — locked

### In

- Stateful synthetic world: 4 customer archetypes, merchants with MCC and geo,
  devices, tokens, a ledger that rejects impossible events, 3 hard-negative
  families, agents carrying structured mandates
- Causal feature store with two implementations (batch + streaming) that must agree
- Blue: LightGBM, isotonic calibration, cost-sensitive decision router, SHAP
- Intent-drift engine for agent-initiated payments (no LLM)
- Red: 5 attack families, declarative mutability mask, batch-vectorised mutation
  search, ASR@budget, Minimum Evasion Distance
- Closed loop: failure store, replay, challenger, promotion gate, 3 rounds
- The five-layer realism filter (see [EVALUATION.md](EVALUATION.md))
- FastAPI + React app on a Hugging Face Space
- Full documentation, claim register, technical report

### Out — do not build these

GNN of any kind · RL (PPO/DQN) · diffusion / TabDDPM · STG-DGR · generative replay ·
EWC · knowledge distillation · conformal prediction · ADWIN · PSRO · RAG
investigator · Weights & Biases · CatBoost · per-machine compute profiles.

Every one is Tier-2/3 in the original spec's own scheme. In a 3-day build none
produces a defensible measured result, and **a half-working one is a liability in
the report** — it invites exactly the question we cannot answer.

If you believe one of these is necessary, write the argument in
`brain/DECISIONS.md` first. Do not just build it.

## 6. Attack families

Five, chosen so that all four "intelligence layers" the design claims are still
demonstrated with half the families.

| ID | Family | Layer it exercises | Visible to Blue in training? |
|---|---|---|---|
| R1 | Account takeover | tabular / behavioural | yes |
| R2 | Velocity burst | temporal | yes |
| R3 | Low and slow | temporal | yes |
| R4 | Mule ring | relational / graph | **no — hidden** |
| R8 | Agentic intent drift | agentic / mandate | **no — hidden** |

The two hidden families are the zero-day transfer test. Success against them
measures generalisation, not recall.

### The headline demo narrative

Blue trains on R1, R2, R3 only. R8 never appears in its training data — and the
**intent engine catches it anyway**, because intent drift is a structural signal
rather than a learned pattern. That is a genuine, honest, payments-specific story,
and it ties directly to Mastercard's Verifiable Intent direction (verified real,
March 2026 — see [RESEARCH.md](RESEARCH.md)).

## 7. Constraints

| | |
|---|---|
| Time | 3 days, 2 people, roughly 60 person-hours |
| Compute | **No GPU anywhere.** Kaggle CPU notebooks for the full run |
| Cost | Free tiers only — Kaggle, Hugging Face, GitHub |
| APIs | None. No paid API keys. No LLM in any scoring path |
| Data | No real cardholder data, no PII, no production systems |

## 8. Ownership

| | Owns |
|---|---|
| **A** | Infrastructure, contracts, evaluation, API, frontend, deployment, docs, submission |
| **B** | Simulator, feature store, Blue models, Red engine, closed loop, Kaggle runs |

Neither waits for the other. `src/mcdl/fixtures.py` emits schema-valid fake
artifacts so the API, UI, evaluation harness and report are all built on day 1
against fixtures. Swapping to real artifacts is a path change.

At the end of day 1, **both** people run the full pipeline from a clean clone. A
two-person team where only one person can debug the ML has a single point of failure.

## 9. Blocks and gates

| Block | What | Gate |
|---|---|---|
| 0 | Foundation, contracts, fixtures, deploy a hello-world Space | 0 contracts |
| 1 | Synthetic world + API/UI shell | 1 world |
| 2 | Causal features + filter L1/L2/L4 | 2 features |
| 3 | Blue baseline + external anchor | 3 blue |
| 4 | Red engine + filter L3 | 4 red |
| 5 | Closed loop + intent engine | 5 loop |
| 6 | Full cloud run, real artifacts in the live app | 6 artifacts |
| 7 | Evidence, docs, submission | 7 submission |
| 8 | Buffer — do not plan work here | — |

Live status is in `brain/TASKS.md` and `brain/PROJECT_CONTEXT.md`.

## 10. Deliverables

1. Public GitHub repository
2. Live web prototype (Hugging Face Space URL)
3. Technical report / solution walkthrough
4. `TeamName.docx`
5. Kaggle writeup — **submitted, not saved as draft**

`docs/COMPETITION.md` is the source of truth for these. **It is currently a
template.** Somebody must open the real competition page and fill it in before
anything else is built on assumptions.

## 11. Honesty rules

These are not style preferences. They are what makes the submission defensible.

1. A number that is not in an artifact file **does not exist**. Not in a docstring,
   not in a comment, not in the report, not in the UI.
2. **"Not measured" is a valid value everywhere**, including the UI. A zero
   standing in for an unmeasured value is a lie that will be found.
3. If a result looks too good (PR-AUC around 0.99), treat it as a **bug report**.
   It almost always means leakage or the detector learning a generator rule.
4. We state what we cut and why. Silence about limitations reads as ignorance;
   stated reasoning reads as judgement.
5. A gate that has not been run is never described as passing.

## 12. Safety boundary

Everything runs on synthetic or public data inside a controlled simulation. No
real cardholder data, no PII, no production payment systems, no attacks against
live services or third parties. This is a security research prototype, not an
attack platform.
