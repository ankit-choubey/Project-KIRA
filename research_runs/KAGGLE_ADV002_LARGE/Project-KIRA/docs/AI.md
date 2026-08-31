# AI — the ML design

Owner: **B**. Everything under `src/mcdl/{world,features,blue,red,loop}`.

This is a specification, not a tutorial. It says what must exist, what each piece
must satisfy, and where the traps are. Implementation choices inside those
constraints are yours.

Read [ARCHITECTURE.md](ARCHITECTURE.md) first, and `.agents/rules/20-ml-rules.md`
before writing a line.

---

## 1. The synthetic world — `src/mcdl/world/` · BLOCK 1

### First principle

> **Legitimate behaviour is generated first. Fraud is an intervention into that world.**

This is what separates the project from "random rows plus fraud labels plus a
classifier". Every attack must be expressible as a modification to an existing,
valid world state.

### Entities

| Entity | Carries |
|---|---|
| Customer | archetype, home lat/lon, account-open date, credit limit, per-customer behavioural parameters (mean/std of log amount, daily transaction rate), `has_agent` |
| Merchant | MCC (4 digits), category, lat/lon, risk tier |
| Device | first-seen timestamp, `shared` flag (hidden metadata, never a feature) |
| Mandate | the agent authorisation object — see §6 |

Behavioural parameters are drawn **per customer** at world creation. The detector
never sees them; they are exactly what it has to infer from history. If two
customers with the same archetype behave identically, the world is too easy and
the detector will look better than it is.

### Archetypes — 4, not 10

`salaried_urban` (0.45) · `student` (0.25) · `small_business` (0.20) ·
`high_net_worth` (0.10). Shares live in `configs/base.yaml` and must sum to 1.0.

Each archetype needs a distribution, parameters, a stated reason, and a test.
Do not hard-code plausible-looking constants — fit them to
[DATA_PROFILE.md](DATA_PROFILE.md), which B produces from the reference dataset.

### The stateful ledger

The simulator maintains, per entity: balance, available credit, rolling velocity,
failed-authentication count, known devices, active tokens, merchant relationships,
agent permissions.

**The ledger must reject impossible events.** A transaction of 10,000 against
available credit of 1,000 is invalid unless an overdraft scenario is explicitly
configured. Log the first 20 rejections with reasons — if everything is being
rejected it is almost always an off-by-one on credit limits.

### Hard negatives — mandatory

Legitimate behaviour that looks fraudulent. Without these the detector learns
"unusual equals fraud" and the reported false-positive rate is meaningless.

| Family | Share | Shape |
|---|---|---|
| `traveller` | 0.03 | sudden geography change, new device, higher amounts, all legitimate |
| `flash_sale` | 0.04 | burst of transactions at one merchant across many customers |
| `shared_family_device` | 0.03 | one device, several customer ids, stable over time |

### Preventing shortcut learning

The detector must not be able to learn the generator's rule. Deliberately:

- Some fraud looks entirely normal (camouflage)
- Not every fraud uses a new device, a large amount, and high velocity
- Different attack families perturb **different** signals
- Legitimate anomalies exist (the hard negatives above)

If gate 3 produces a PR-AUC around 0.99, this section failed. Treat it as a bug
report, not a success.

### Physical validity — the L1 gate

Every generated row must satisfy, and the check must count violations:

- balance never negative unless overdraft is configured
- per-entity timestamps strictly increasing
- no transaction from a device before that device is registered
- MCC is 4 digits and in the valid set
- geography transitions are feasible given elapsed time
- no token used after revocation
- referential integrity on every foreign key

Zero violations is the gate-1 condition. A row that violates physics is deleted
and counted, never scored.

---

## 2. Feature store — `src/mcdl/features/` · BLOCK 2

**This is the hardest engineering in the project and the most likely source of a
confidently wrong result.**

### One spec, two implementations

`features/spec.py` holds a single list of feature definitions. `batch.py` (polars,
vectorised, for training) and `stream.py` (dict state, one row at a time, for
serving) are both driven by it. **Never add a feature to one path only.**

### The causality rule

```
feature(t) = f(events <= t)          never   f(events > t)
```

Sort order is `(timestamp, txn_id)` **everywhere**, defined once. Ties on equal
timestamps are the classic cause of batch/stream disagreement.

### Feature groups

| Group | Examples |
|---|---|
| Transaction | amount, log amount, hour of day, day of week, MCC, channel |
| Behavioural | amount z-score against the customer's own history, deviation from personal merchant mix, time-since-last-transaction |
| Velocity | transaction count and amount sum over 1 h / 6 h / 24 h windows |
| Transition | merchant changed, geography changed, device changed, new device flag |
| Entity | account age, distinct devices per account, distinct accounts per device |
| Relational | account degree, merchant degree, shared-device account count, `recent_neighbor_fraud_rate` |

### Two traps that produce silent wrongness

1. **polars `.rolling(window_size=n)` is a row-count window**, not a time window.
   Time-based velocity needs `rolling(index_column=..., period="1h")` or
   `group_by_dynamic`. Using the row-count form gives wrong velocity with no error.

2. **Label delay.** `recent_neighbor_fraud_rate` reads other entities' *labels*.
   In production you do not know a transaction was fraud for days or weeks —
   chargebacks are slow. Gate it behind `features.label_availability_lag_days`
   (default 7). Then report performance **under realistic lag and with oracle
   labels**; the gap is a result worth having, not something to hide.

### The gate-2 invariant

For a sample of at least 1,000 rows, batch features must equal streaming features
to 1e-9. Write `tests/invariants/test_batch_stream_parity.py` **before** the
features it checks. A second test asserts no feature reads an event after `t`.

If this test is failing, nothing downstream is trustworthy. Do not proceed.

---

## 3. Blue team — `src/mcdl/blue/` · BLOCK 3

### Model

LightGBM as champion. XGBoost **only** to make the ensemble ablation honest.
CatBoost is cut — install friction, marginal signal on engineered numeric features.

### Class imbalance — `scale_pos_weight`, never SMOTE

This is a research-backed decision, not a preference. SMOTE preserves ranking but
distorts posterior probabilities; a published comparison saw false alarms rise from
35 to 5,775 while ROC-AUC barely moved (0.9806). Our decision policy is
cost-sensitive and therefore depends on calibrated probabilities, so a method that
wrecks calibration while flattering AUC is precisely wrong for us.
See [RESEARCH.md](RESEARCH.md) §4.

We still **run** the comparison as an ablation — reported on **ECE and FPR**, not
AUC, because AUC is the metric that hides the damage.

Any resampling or reweighting happens **after** the split, inside training folds only.

### Calibration

Isotonic, fitted on a held-out slice, never on the training data. Report Brier and
ECE. With few positives isotonic overfits easily — use a cross-validated wrapper.

### Decision router

```
calibrated score -> cost-sensitive policy -> ALLOW | STEP_UP | BLOCK
```

Optimise expected cost using the weights in `configs/base.yaml`:

```
utility = -(fraud_loss * P(fraud) * amount)
          - (step_up_friction * P(step_up))
          - (review * P(review))
```

**Report a cost/friction curve across the threshold sweep, not F1.** Payments
audiences think in loss and friction, not F1. Thresholds in the config are starting
values to be tuned on that curve, not fixed truths.

### Explanation

TreeSHAP, computed **on demand for inspected transactions only**. Never batch it
across the dataset — it is fast per row but not free, and it is not on the latency
path for a normal decision.

### Decision audit record

Every decision should carry: `txn_id`, risk score, calibrated score, decision,
`model_version`, `feature_version`, `policy_version`, top reason codes, intent
drift score, latency. This gives the prototype an auditable answer to "why did the
system block this transaction?".

### Latency — measure honestly

Measure `feature build (warm state) + inference + policy`, end to end, over the
real HTTP path. Report P50/P95/P99. **Name the state store.** An in-process dict is
not production — saying so earns more credibility than hiding it. Reporting
`model.predict()` time alone as end-to-end latency is misleading and a domain judge
will catch it.

---

## 4. Red team — `src/mcdl/red/` · BLOCK 4

### The threat model — state it or ASR means nothing

The original design never said what the attacker knows. An optimiser that queries
the model's score without limit is white-box; real fraudsters are black-box with a
small probe budget before the account is burned.

**Report ASR at query budgets {1, 5, 20, 100}.** Record `queries_used` on every
`AttackCandidate`. Two hours of work; it is what makes the entire Red team credible.

### Attack grammar

Each family declares: target entity, mutable fields, constraints, objective,
budget. Five families (R1 ATO, R2 velocity burst, R3 low-and-slow, R4 mule ring,
R8 intent drift), 10 variants each.

### Mutability mask

| Mutable — the attacker controls | Immutable — the attacker cannot change |
|---|---|
| amount | victim account age |
| timing / inter-arrival | historical spending distribution |
| merchant choice within a category | past transactions already in the ledger |
| device | merchant's own history |
| channel | anything already written to the ledger |
| session ordering | |

**Enforce the mask inside the sampler, not as a check afterwards.** Every generated
attack must also pass filter L1. An "evasion" that violates physics is a bug in the
mask, not a discovery. Gate 4 requires zero mask violations.

### Search — the schedule risk

A naive genetic search is the single most likely thing to blow the timeline.
Population 64 x 20 generations x per-candidate feature recomputation, at 10 ms per
candidate, is roughly 13 seconds **per attack instance**; hundreds of instances
becomes hours. The literature already flags multi-objective evolutionary attacks on
tabular data as computationally expensive.

Mitigations, in order:

1. **Score the entire population in one `predict()` call.** This is a 10–50× win
   and is the first thing to build.
2. Reduce to population 40 x 15 generations.
3. Run the full search on two families and constrained random mutation on the rest —
   and say so in the report.

`pymoo` NSGA-II is a **stretch only**. Batched hill-climbing with the same
objectives ships first. Objectives: evasion, fidelity (L1 + L3), perturbation cost.

Note: CAA / CAPGD from the literature are gradient-based and will not work against
LightGBM. The genetic path is the only option for a tree model. See
[RESEARCH.md](RESEARCH.md) §5.

### Minimum Evasion Distance — the headline metric

For a detected attack, find the smallest change to mutable fields that flips BLOCK
to ALLOW. Report the field, original value, evading value, and distance.

Make this the money chart rather than ASR. It is more honest — ASR moves when you
move the threshold, MED does not — and it is the most intuitive robustness number a
payments audience will ever see:

> "Before hardening an attacker needed to change the amount by 340. After
> hardening, 2,900."

MED should **increase** across hardening rounds. That is the result.

---

## 5. Closed loop — `src/mcdl/loop/` · BLOCK 5

### The pipeline

```
successful evasion -> failure store -> replay buffer -> challenger training
                                                              |
                                                              v
                                                       promotion gate
                                                       |            |
                                                  promote        rollback
```

The failure store records, per evasion: attack family, features, why it was missed,
model version, attack cost, query budget consumed.

Replay is capped at `loop.replay_max_fraction` (0.15) of the training set. An
uncapped fraud-heavy replay mix is how hardening blows up the false-positive rate.

### The protocol that makes the result honest

Red generates variants 0–9 of a family. Blue hardens on variants **0–4 only**.

| Reported | What it measures |
|---|---|
| ASR on variants 5–9 (same family) | **generalisation — the headline** |
| ASR on a family never seen (R4, R8) | transfer / zero-day |
| ASR on variants 0–4 | memorisation — shown only for comparison |
| PR-AUC on the original benign+fraud test set | no regression |

Reporting ASR on the variants you trained on is not a result. `configs/base.yaml`
asserts `harden_on_variants < variants_per_family` at load time so this cannot be
accidentally disabled.

### Promotion gate — five dimensions

A challenger is promoted only if **all** hold:

1. new-threat performance improves
2. old-family performance is materially maintained
3. legitimate-traffic performance is maintained
4. calibration is acceptable
5. latency is acceptable

If the challenger wins on new attacks but wrecks old ones, that is catastrophic
forgetting — and it is a **result**. Report it.

Three rounds. `RoundResult` records champion, challenger, promoted y/n, reasons,
and both metric blocks.

---

## 6. Intent engine — `src/mcdl/blue/intent.py` · BLOCK 5

The flagship differentiator, and the piece the original design left as ten signal
names with no algorithm.

### The mandate object

A user's authorisation to an AI payment agent:

```
Mandate: mandate_id, customer_id, agent_id,
         max_amount, max_txn_count,
         allowed_mcc[], merchant_allowlist[],
         valid_from, valid_until,
         allowed_geo_radius_km
```

Modelled after the problem Mastercard's **Verifiable Intent** framework addresses —
linking what the user authorised to what the agent actually did. This is our
prototype mechanism. We do **not** claim it is Mastercard's production scoring.

### Scoring — no LLM

```
declared mandate  ->  violation vector  ->  weighted sum  ->  intent_drift_score
                   +  MCC-hierarchy category distance
```

Signals: amount over limit, MCC outside the allowed set, merchant outside the
allowlist, geography beyond radius, outside the validity window, transaction count
exceeded, category distance from the authorised intent.

**An LLM in the scoring path destroys latency and reproducibility, and cannot be
ablated honestly.** Use the MCC hierarchy for semantic distance instead. Half a
day of work, fully explainable, fully ablatable.

### The ablation that matters

Transaction-only versus transaction+intent, on controlled intent-drift attacks.
R8 is hidden from Blue's training data, so if the intent feature catches it the
signal is structural rather than learned. That is the demo.

---

## 7. Evaluation

Owned by A and specified in [EVALUATION.md](EVALUATION.md). B must produce the
inputs it needs: valid worlds, causal features, decisions with latency, attack
candidates with query budgets, and round results.

---

## 8. Reproducibility

Seeds threaded explicitly — `rng = np.random.default_rng(seed)`, no global
`np.random.seed`. Every entry point takes a seed and records it in the manifest.
Every run writes `artifacts/<run_id>/manifest.json` with git commit, config hash,
seed, scale, timings and metrics.

**A metric with no run_id does not go in the report or the UI.**
