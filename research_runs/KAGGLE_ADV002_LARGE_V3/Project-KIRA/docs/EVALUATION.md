# EVALUATION — the realism filter and the gate ladder

Owner: **A**. Lives in `src/mcdl/evaluation/`.

This is the part that makes every other number in the project believable. It is
also the part the original design was weakest on — see [DRAWBACKS.md](DRAWBACKS.md)
F-06, F-07, F-09.

---

## Part 1 — The five-layer realism filter

The question "is our synthetic data good?" needs five different answers. The
original design had only layer 2 and called it a fidelity harness.

### Layer 1 — Validity · `evaluation/validity.py`

**Physics, not statistics. A hard boolean gate.**

A row either is or is not possible. This is not scored — a violating row is
rejected and counted.

| Check | Condition |
|---|---|
| negative balance | never, unless overdraft is explicitly configured |
| timestamp monotonicity | strictly increasing per entity |
| device registration | no transaction from a device before it is registered |
| MCC validity | 4 digits, in the valid set |
| geography feasibility | transitions respect minimum travel time |
| token lifecycle | no use after revocation |
| referential integrity | every foreign key resolves |

**Gate 1 condition: zero violations.** Cheap to run, and it catches an entire class
of bug that otherwise surfaces as mysterious model behaviour three days later.

### Layer 2 — Marginals and dependency · `evaluation/marginals.py`

**Necessary, not sufficient. Report it, do not headline it.**

KS statistic per column, Wasserstein where appropriate, categorical divergence,
correlation-matrix distance.

Understand what it cannot see: marginals are per-column, and correlation captures
linear pairwise structure only. Fraud lives in conditional, sequential and graph
structure. A generator sampling every column independently from the correct
marginal passes this layer completely.

### Layer 3 — Behavioural fidelity · `evaluation/behavioral.py`

**The axes that actually matter for fraud, with published baselines to beat.**

| Axis | Measure |
|---|---|
| **P1** inter-event timing | per-entity inter-arrival distribution vs real. KS on log inter-arrival, computed **per archetype** — pooling hides the failure |
| **P2** burst structure | burstiness coefficient `B = (σ−μ)/(σ+μ)`, Fano factor, autocorrelation of per-entity event counts |
| **P3** multi-account graph motifs | shared-device fan-out distribution, k-core sizes, triangle counts on the account–device–merchant tripartite graph |
| **P4** velocity-rule trigger rates | define a fixed set of classic velocity rules; compare trigger rates real vs synthetic |

P4 is the most interpretable to a payments audience because it is literally what
rule engines do today.

#### The normalisation — do not skip this

Split the real reference data in half. Compute each metric between the two halves:
that is the **natural variability floor**. Then report:

```
degradation ratio = metric(real, synthetic) / metric(real_a, real_b)
```

**1.0 means our synthetic data differs from real data by no more than one sample of
real data differs from another.** Without this normalisation every fidelity number
is uninterpretable, because you cannot separate generator error from sampling noise.

#### Published baselines (context, not our results)

| Generator | Dataset | Ratio |
|---|---|---|
| TVAE | IEEE-CIS | 24.4× |
| CTGAN | IEEE-CIS | ~30× |
| GaussianCopula | IEEE-CIS | 39.0× |
| row-independent | Amazon Fraud | 81.6–99.7× |
| TabularARGN | Amazon Fraud | 17.2× |

Source in [RESEARCH.md](RESEARCH.md) §2. These are **published numbers on published
datasets**, shown alongside ours for context — never presented as our results, and
never as a like-for-like comparison unless we run on the same dataset.

### Layer 4 — Detectability · `evaluation/c2st.py`

**The classifier two-sample test. This is the direct answer to "is our data good?"**

Label real rows 0 and synthetic rows 1. Train a LightGBM discriminator. Report
cross-validated AUC.

- **AUC ≈ 0.50** — indistinguishable from real. The honest pass.
- **AUC ≈ 1.00** — trivially fake.

**Then read the discriminator's SHAP.** The top features are exactly the artefacts
giving us away — a rounded amount distribution, an impossible timestamp
granularity, a categorical that never takes its rare values. Fix, regenerate,
re-run, watch the AUC fall. This is a debugging loop, not a score.

Run at **two levels**:

- **row level** — weak, easy to pass
- **entity level** — aggregate per account into a behavioural profile, then
  discriminate. Much harder and far more meaningful for fraud.

An entity-level AUC near 0.5 means we genuinely built a realistic world and can say
so with a straight face.

### Layer 5 — Utility · `evaluation/tstr.py`

**Train on synthetic, test on real.**

Train a detector purely on our world, evaluate on held-out Sparkov. Compare to
train-real / test-real (TRTR). The ratio is the utility score, and it is the
strongest possible answer to "so what?" — it shows the synthetic world carries
transferable signal, not just plausible-looking numbers.

---

## Part 2 — Attack realism

Attacks need a **different** filter from benign data. Attacks are supposed to be
rare and different; measuring them against the full transaction distribution
correctly tells you they are unusual, which is not the question. The question is
whether they are plausible **as fraud**.

### Test 1 — Constraint validity

Did the attacker only mutate attacker-controllable fields? The mutability mask is
enforced inside the sampler and asserted afterwards; every attack must also pass
layer 1. An "evasion" that violates physics is a bug in the mask, not a discovery.

**Gate 4 condition: zero mask violations, zero invalid attacks.**

### Test 2 — Conditional plausibility

C2ST against **real fraud rows only** (`is_fraud = 1`). Sample sizes are small, so
use cross-validated AUC with confidence intervals and resist over-claiming. An AUC
of 0.62 with a wide interval is an honest result; reporting it as though it were
0.50 is not.

### Test 3 — Attacker cost and capability

| Metric | Why |
|---|---|
| **ASR at budgets {1, 5, 20, 100}** | An attack needing 10,000 queries is a gradient, not a fraud strategy |
| **Resource cost** | accounts burned, devices needed, time elapsed |
| **Minimum Evasion Distance** | the smallest change to mutable fields that flips BLOCK to ALLOW |

**Make MED the headline, not ASR.** ASR moves when the threshold moves; MED does
not. And it is the most intuitive robustness number a payments audience will see:
*"before hardening an attacker needed to change the amount by 340; after hardening,
2,900."* MED should increase across rounds.

---

## Part 3 — Protocols that keep results honest

### Out-of-time splitting

`train.max_ts < valid.min_ts` and `valid.max_ts < test.min_ts`. **Asserted, not
assumed.** No random splits anywhere.

Resampling or reweighting happens after the split, inside training folds only.

### Anti-circularity

- `train_attack_ids ∩ test_attack_ids = ∅`
- generation seeds for training ≠ evaluation seeds
- families in `red.hidden_from_blue` never appear in Blue's training data

### The held-out-variant protocol — the central result

Red generates variants 0–9 of each family. Blue hardens on variants **0–4 only**.

| Reported separately | Measures |
|---|---|
| ASR on variants 5–9, same family | **generalisation — the headline** |
| ASR on an unseen family (R4, R8) | transfer / zero-day |
| ASR on variants 0–4 | memorisation — shown only for comparison |
| PR-AUC on the original benign+fraud test set | no regression |

Collapsing the first and third rows is exactly how a project reports memorisation as
hardening. `configs/base.yaml` asserts `harden_on_variants < variants_per_family` at
load time.

### External reality anchor

Train on our world, evaluate on Sparkov. **Tier-1, not an enhancement.** It is the
only thing that makes any number credible outside our own simulator. Gate 6 fails if
`anchor` is null.

### Label delay

Any feature reading another entity's label sees only labels confirmed at least
`label_availability_lag_days` (7) before `t`. Report performance under realistic lag
**and** with oracle labels — the gap is a result, not something to hide.

---

## Part 4 — Metrics

| Group | Metrics |
|---|---|
| Classification | PR-AUC (primary), ROC-AUC, precision, recall |
| Operational | FPR, FNR, decision distribution, latency P50/P95/P99 |
| Calibration | **ECE**, Brier |
| Cost | expected loss vs friction across the threshold sweep |
| Red | ASR by budget, ASR seen / held-out / unseen family, MED, mask violations, invalid attacks |
| Fidelity | L1 violations, L2 KS + correlation distance, L3 P1–P4 ratios, L4 C2ST row + entity, L5 TSTR / TRTR |
| Loop | per-round deltas, promotion decisions and reasons |

**Accuracy is not a metric here.** Neither is F1 as a headline — report the
cost/friction curve instead. Payments audiences think in loss and friction.

---

## Part 5 — The gate ladder

Each gate asserts one invariant, so when a downstream number looks wrong you walk
**up** and the first failing gate names the layer.

```
make gate 0    contracts     schemas, fixtures, unit + e2e tests, frontend built
make gate 1    world         zero physics violations, FK integrity
make gate 2    features      batch == stream, no future reads       <- CRITICAL
make gate 3    blue          out-of-time split, beats rule baseline, ECE, anchor
make gate 4    red           zero mask violations, ASR@budget, MED, L3 ratios
make gate 5    loop          held-out-variant ASR separate, no regression
make gate 6    artifacts     every number traces to a run_id, not a fixture
make gate 7    submission    repo, docs, demo, no secrets
```

| Gate | A failure means |
|---|---|
| 0 | A and B have drifted apart. Reconcile contracts before anything else. |
| 1 | Simulator bug. Every number downstream is meaningless. |
| 2 | **Leakage. This is the bug that looks like success.** |
| 3 | Circular evaluation. The headline result is fiction. |
| 4 | Attacks are cheating. ASR is inflated and indefensible. |
| 5 | You are measuring memorisation, not hardening. |
| 6 | You cannot defend these numbers. Do not publish them. |
| 7 | Not ready to submit. |

### Rules

1. An unimplemented gate reports **PENDING** and exits 2. It never reports PASS.
   "The gate passed" must always mean the check actually ran.
2. **Never weaken an assertion to make a gate pass.** Fix the cause, or record in
   `brain/ERRORS.md` why the assertion itself was wrong.
3. Do not start a block on top of a failing gate.
4. Each gate writes `artifacts/gates.json` and then runs `make brain`, so
   `brain/PROJECT_CONTEXT.md` always reflects reality.

### The two tests worth more than the other twenty

**Gate 2 batch-equals-streaming** and **gate 3 no-temporal-overlap.** Almost every
way this project produces a confidently wrong result runs through one of those two.
Write both before writing a model.

In a 3-day build, an `assert` that runs on every pipeline execution beats a pytest
file nobody runs twice. Put cheap invariants inside the pipeline; reserve test files
for things needing fixtures or comparison.

---

## Part 6 — Experiments

| ID | Question |
|---|---|
| EXP-01 | Does the simulator produce valid transactions? (gate 1) |
| EXP-02 | Do batch and streaming features agree? (gate 2) |
| EXP-03 | Does LightGBM beat a rule baseline on held-out time? |
| EXP-04 | Does the ensemble beat the best single model? |
| EXP-05 | Do behavioural and temporal features help? |
| EXP-06 | Do cheap graph features help? |
| EXP-07 | Does intent drift help, on R8 specifically? |
| EXP-08 | `scale_pos_weight` vs SMOTE — on ECE and FPR |
| EXP-09 | Oracle labels vs 7-day label delay |
| EXP-10 | How realistic is the synthetic world? (L1–L5) |
| EXP-11 | ASR as a function of query budget |
| EXP-12 | Does hardening reduce ASR on **held-out variants**? |
| EXP-13 | Does hardening transfer to an **unseen family**? |
| EXP-14 | Does hardening preserve old-family and legitimate performance? |
| EXP-15 | Does Minimum Evasion Distance increase across rounds? |
| EXP-16 | Does the anchor result support the simulator's realism? |
| EXP-17 | End-to-end latency over HTTP |

Each result lands in `artifacts/<run_id>/evaluation.json` and gets a row in
`brain/CLAIMS.md` naming its `run_id`. **An experiment not run is reported as not
run** — that is worth more than a half-tuned result.
