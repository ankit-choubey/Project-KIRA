# DRAWBACKS — what was wrong with the original idea, and the fix

The project began as a 13,763-line specification (`mastercard.md`) with everything
marked FROZEN. It was audited before any code was written. This file records the
defects found, why each one matters, and the fix that is now built into the design.

Read this before defending a design decision. Most of what looks arbitrary in
[AI.md](AI.md) and [EVALUATION.md](EVALUATION.md) is a fix for something here.

---

## The two structural problems

### S-1 · The spec was never costed

In 13,763 lines it **never once estimates hours for a task**. It allocates *days to
steps*, top-down, and calls that time-budget governance. Nothing was estimated
bottom-up. That is exactly how a 300–500 hour plan gets labelled "96 hours" and then
frozen.

**Fix:** every block in [PROJECT.md](PROJECT.md) §9 has an owner and a gate. Scope
was cut to roughly a third — 5 attack families instead of 10, 4 archetypes instead
of 10, 3 rounds, no Tier-3 models at all.

### S-2 · "FROZEN" made cutting feel like failure

Forty uses of FROZEN/LOCKED in a document handed to a three-day build. Under time
pressure you need to cut ruthlessly, and language like that turns every cut into an
argument.

**Fix:** the tier system is explicitly unfrozen in `.agents/rules/00-project.md`.
The cut list is a decision with reasoning, recorded in `brain/DECISIONS.md`, not a
retreat.

---

## Blocking defects

### F-01 · Scope was ~3.5× the available time

Covered above. The P0 list alone — simulator, hard negatives, fidelity harness,
feature store, three GBDTs, calibration, router, SHAP, attack grammar, ten
families, mutation engine, NSGA-II, counterfactual search, failure analyser, replay,
champion/challenger, five-dimension gate, fifteen experiments, four-view UI, CI,
schemas, manifests, DOCX, writeup — is 300–500 engineering hours against roughly 60.

**Fix:** the cut list in [LIMITATIONS.md](LIMITATIONS.md), with reasoning stated
rather than hidden.

### F-02 · No fixture strategy — the two-person split would deadlock

A owns evaluation, API, frontend and docs. All four depend on artifacts B produces.
B owns a serial chain: data → features → blue → red → loop. So A is idle-blocked
for two days, then panic-builds the UI on day 3 against artifacts never seen before.

**The spec has no mock or fixture layer anywhere in 13,763 lines.** This is its
single biggest omission for parallel work.

**Fix:** `src/mcdl/fixtures.py` emits schema-valid fake artifacts in hour two.
Everything downstream is built and deployed against them on day 1. Fixtures set
`manifest.is_fixture = true`, the API surfaces it, the UI banners it, and gate 6
fails if a fixture reaches the report.

### F-03 · The feature store is the real bottleneck and had one task

Every velocity and deviation feature must be causal, and that needs **two
implementations that must agree**: a vectorised batch path for training and a
stateful streaming path for serving. This is where nearly all leakage bugs live and
where the latency claim is actually decided. The spec gave it one task (BLUE-001)
with six bullet points.

**Fix:** one spec (`features/spec.py`) driving both paths, and the parity test is
**written before the features**. Gate 2 runs it. See [AI.md](AI.md) §2.

### F-04 · The attack search would blow the compute budget

Population 100 × 50 generations × five objectives with per-candidate feature
recomputation is ~50 seconds *per attack instance*; 500 instances is seven hours.
The literature already flags multi-objective evolutionary attacks on tabular data
as computationally expensive, and gradient alternatives (CAA/CAPGD) do not work on
tree models.

**Fix:** batch-vectorised population scoring first — a 10–50× win. Fallbacks in
order: population 40 × 15 generations, then full search on two families only, with
the reduction stated in the report. NSGA-II is a stretch goal, not the baseline.

### F-05 · The threat model was never stated, making ASR unfalsifiable

Nowhere does the spec say what the attacker knows. The search as designed queries
the model's score freely and without limit — a white-box optimiser. Real fraudsters
are black-box with a small probe budget before the account is burned.

Without a query budget, "ASR = 31%" is the success rate of an adversary who does
not exist.

**Fix:** ASR reported at budgets {1, 5, 20, 100}. `queries_used` is a field on
`AttackCandidate`. Two hours of work; it makes the entire Red team credible and
almost no competing team will have it.

---

## Major defects

### F-06 · The closed loop could succeed trivially and mean nothing

Red generates attack A → Blue retrains on A → Blue catches A. That is memorisation,
and it produces a beautiful descending ASR curve that a sharp judge dismantles in
one question. The spec knows about hidden families but does not make the honest
version the *primary* result.

**Fix:** the held-out-variant protocol. Blue hardens on variants 0–4; the headline
is ASR on variants 5–9 of the same family, plus transfer to an unseen family, plus
a no-regression check on the original test set. `configs/base.yaml` asserts
`harden_on_variants < variants_per_family` at load time so it cannot be silently
disabled.

### F-07 · The external reality anchor was Tier-2

We train on our simulator and evaluate on our simulator. The spec's own §3.42
identifies the failure mode — the detector learns the generator's rule and reports a
meaningless 0.99. The tri-split addresses circularity *within* the simulator; it
does nothing about the simulator being wrong in the first place.

**Fix:** promoted to Tier-1. Evaluating on Sparkov costs about four hours and is
the only thing that makes any number credible to an outside reader. Gate 6 fails if
`anchor` is null.

### F-08 · `recent_neighbor_fraud_rate` is a leakage landmine

BLUE-008's cheap graph features are the smartest single call in the original spec.
But this one reads *labels* of connected entities, and the spec never mentions label
delay. In production you do not know a transaction was fraud for days or weeks —
chargebacks are slow.

**Fix:** gated behind `features.label_availability_lag_days` (7). Report performance
under realistic lag **and** with oracle labels. This turns a bug into one of the
best production-realism talking points in the project.

### F-09 · The fidelity harness is a smoke test, not a filter

Marginal KS plus correlation distance plus degree distribution. A generator that
samples every column independently from the correct marginal passes all three and
has zero behavioural structure.

**Fix:** the five-layer filter in [EVALUATION.md](EVALUATION.md). Layers 1, 3, 4
and 5 were entirely absent from the spec; only layer 2 existed.

### F-10 · Latency would be measured dishonestly by default

LightGBM inference on ~100 features is 50–200 µs. That is not where the time goes,
and reporting it as end-to-end latency is misleading. The cost is feature
construction with state lookups.

**Fix:** measure feature build + inference + policy over the real HTTP path, report
P50/P95/P99, and name the state store. "In-process state; production would need
Redis, which adds a network hop" earns credibility rather than losing it.

### F-11 · The intent-drift engine — the flagship differentiator — had no algorithm

Ten signal names and an arrow. No representation, no aggregation, no scoring
function. This is the Mastercard-specific hook and the thing tying the project to
Verifiable Intent.

**Fix:** a structured `Mandate` object, drift as a weighted violation vector plus
MCC-hierarchy category distance. **No LLM** — an LLM in the scoring path destroys
latency and reproducibility and cannot be ablated honestly. Half a day, fully
explainable. See [AI.md](AI.md) §6.

---

## Process and correction

### F-12 · The process was heavier than the code

Feature branches, PR review between two people, `HANDOFF.md`, `PROJECT_STATUS.md`,
per-person progress directories, a six-stage CI pipeline. For a two-person
three-day sprint that is 5–8 hours of pure tax out of ~60.

**Fix:** kept — schemas, a manifest per run, the claim register, one CI job.
Dropped — PR ceremony, per-person progress directories, mypy. Small commits
straight to `main`; discipline is reconstructible from git history.

### F-13 · The compute constraint being designed around is mostly imaginary

Six compute profiles, Kaggle/Colab orchestration, resumable cloud execution, a
dedicated "Cloud Compute Lead" role — for a P0 that is gradient-boosted trees on
tabular data.

**Fix:** one config with a `scale` flag. **Zero GPU needed anywhere.** Kaggle CPU
sessions do not consume the GPU quota, so other projects keep their hours. The
reclaimed time goes to the feature store.

### F-14 · Three GBDTs is one and a half too many

CatBoost adds install friction and marginal signal over LightGBM + XGBoost on
engineered numeric features.

**Fix:** LightGBM champion, XGBoost only to make the ensemble ablation honest. If
time is tight, report the single-model baseline and state that the ensemble was not
evaluated — an unrun experiment declared is worth more than three models half-tuned.

### F-15 · Single points of failure in a two-person team

Only B can debug the ML, and the split puts B on the critical path for most of the
build.

**Fix:** both people run the full pipeline end to end from a clean clone at the end
of day 1. The daily artifact is committed even when broken. A starts writing on day
2 so day 3 is not a writing sprint stacked on a debugging sprint.

---

## Factual corrections to the original document

| Issue | Correction |
|---|---|
| A citation dated **January 2027** — a future date | Purge it. It cannot appear in a submitted report. |
| P16 says "the private leaderboard determines final Kaggle standing"; Step 8 describes a Writeup submission | Contradictory. A writeup hackathon has no leaderboard. Resolve against the real competition page before writing model code — see [COMPETITION.md](COMPETITION.md). |
| BAF proposed as a dataset | CC BY-NC-**ND**. Excluded. See [RESEARCH.md](RESEARCH.md) §1. |
| "31 August EOD" with no timezone | Kaggle deadlines are typically 23:59 UTC. Confirm and record it. |
| Novelty framed as "adaptive red team hardens blue team" | Substantial prior art exists (USENIX RAID 2020; evolutionary tabular attacks; 2025–26 LLM red/blue co-evolution). Narrow the claim to the payment-specific world, the mutability mask, the agentic mandate layer, and the measurement protocol. |
| SMOTE treated as a default option | Distorts posteriors and breaks the calibration our cost policy needs. See [RESEARCH.md](RESEARCH.md) §4. |

---

## Things absent from the original spec entirely

Not under-specified — simply not present anywhere in 13,763 lines:

- Any time estimate for any task
- A fixture or mock layer
- The threat model (what the attacker knows and can query)
- Detectability testing (C2ST in any form)
- Utility testing (TSTR in any form)
- Label delay
- Licence review of the external datasets destined for a public repo
- The deadline timezone
- Who writes the report while the other person codes on the final day
- **Independent verification of the brief itself** — every requirement traces back
  to competition material pasted into a conversation, and it could not be located
  from outside. See [COMPETITION.md](COMPETITION.md).
