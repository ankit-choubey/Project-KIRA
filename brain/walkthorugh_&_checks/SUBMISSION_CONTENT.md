# KIRA — Kaggle Submission Content

> **Source of truth for every number below:** `artifacts/run_tiny_s20260827_193f7897_40997ab/`
> (git `40997ab`, config hash `193f789727f6`, seed `20260827`), the supporting small-scale run
> `run_small_s20260827_3a353e9a_052dca8`, and `research_runs/MASTER_COMPARISON.json`.
> Nothing in this document is estimated, rounded up, or asserted without an artifact path.

---

## 1. Project Title

**76 characters:**

```
Project KIRA: Adversarial Co-Evolution Laboratory for Payment Security
```

*Alternates, if a shorter title is preferred:*

- `KIRA: An Adversarial Defense Laboratory for Payment Fraud` (57)
- `KIRA — Measuring Whether Fraud Defenses Generalise or Memorise` (61)

---

## 2. Subtitle / One-liner

**125 characters:**

```
We attack our own fraud detector until it fails, diagnose why it failed, and measure
whether hardening generalises or memorises.
```

*Alternates:*

- `A closed-loop payment security lab where Red attacks, Blue hardens, and a promotion gate refuses to ship a worse model.` (118)
- `Adversarial co-evolution for payment fraud — with an honest report of exactly where the defense stops working.` (109)

---

## 3. Project Description (Markdown)

# Project KIRA — Adversarial Co-Evolution Laboratory for Payment Security

**Track:** AI Defense Lab for Payment Security
**Run ID:** `run_tiny_s20260827_193f7897_40997ab` · **Commit:** `40997ab` · **Seed:** `20260827`

---

## The Problem

Fraud detection is evaluated backwards.

The industry standard is to fit a classifier on historical fraud and report PR-AUC on a
held-out slice of the same distribution. That answers one question — *"does this
transaction resemble fraud we have already seen?"* — and it is the wrong question. An
adversary is not a stationary distribution. They probe, observe the decision, adapt, and
retry. A detector with excellent offline metrics can be trivially evaded by an attacker
who is allowed twenty queries.

Three failures follow from this:

1. **Attack Success Rate is reported without a query budget.** Unlimited-probe success
   describes an adversary who does not exist. A number that assumes infinite queries
   cannot inform a real deployment decision.
2. **Hardening is not distinguished from memorisation.** If a defense is trained on
   attack variants 0–9 and evaluated on variants 0–9, the reported improvement measures
   recall of a fixed set, not robustness.
3. **Nobody reports where the defense stops working.** Generalisation boundaries are
   discovered in production, by an attacker.

KIRA is built to answer the harder question: **what would an adaptive attacker do against
this specific detector, and does hardening against those attacks transfer to attacks the
defense has never seen?**

---

## Three-Pillar Architecture

### Pillar I — IDENTIFY

Detect fraud from strictly causal signal, and diagnose *how* the defense fails.

**Causal feature store.** 25 canonical features defined once in `features/spec.py`, with
two independent implementations — a vectorised batch path for training and a stateful
streaming path for serving. Gate 2 asserts they agree. Causal order is
`(timestamp, txn_id)` ascending; a transaction never observes itself or any successor.
Any feature reading a neighbour's label is gated behind a **7-day chargeback availability
lag**, because in production that label does not exist yet.

**Blue detector.** LightGBM with isotonic probability calibration fitted on a
strictly out-of-time validation split, feeding a cost-sensitive decision router that
minimises expected financial loss across `ALLOW / STEP_UP / BLOCK` rather than
thresholding a probability.

**Verifiable-Intent engine.** Agent-initiated payments carry a `Mandate` — an
authorisation object bounding amount, transaction count, merchant category, and
geography. Intent drift is scored deterministically against that mandate. No LLM sits in
any scoring path.

**12-class failure taxonomy (W1–W12).** Every successful evasion is classified —
velocity blindness, low-and-slow, geographic camouflage, intent drift, graph camouflage,
open-set anomaly, and so on — with hardness, boundary-proximity and novelty scores. This
is what converts "the attack worked" into "the defense has this specific blind spot."

### Pillar II — SIMULATE

Generate adversaries that are constrained, budgeted, and physically valid.

**Stateful synthetic world.** Four customer archetypes with per-customer behavioural
parameters, merchants with MCC and geography, device graphs, and a ledger that rejects
physically impossible events. This run: **9,348 transactions, 200 customers, 80
merchants, 1,294 devices, 53 frauds (0.567% base rate) across 30 days**, with
**zero Layer-1 physics violations**.

**Hard negatives.** Travellers, flash sales, and shared family devices — legitimate
behaviour that looks fraudulent. Without them a detector learns *unusual = fraud* and the
reported false-positive rate is fiction.

**Five attack families.** `burst_drain`, `slow_siphon`, `geo_hop`, `agent_subversion`,
`cross_merchant_fanout` — spanning tabular, temporal, relational and agentic threat
surfaces.

**Declarative mutability mask.** The attacker may only modify fields a real attacker
controls. `txn_id`, `timestamp`, `customer_id`, `balance_before`, `available_credit` and
all evaluation metadata are immutable, enforced inside the sampler rather than checked
afterwards. This run recorded **0 mask violations and 0 physically invalid attacks**.

**Budgeted black-box search.** The attacker gets B ∈ {1, 5, 20, 100} probes. Success is
reported per budget, never unlimited.

**Minimum Evasion Distance (MED).** The smallest normalised perturbation that flips a
protected decision to `ALLOW`. Reported alongside ASR because MED does not move when the
decision threshold moves.

**Three-world evaluation suite.** World A (adaptation families), World B (shifted
customer spending baselines and merchant risk tiers), and World C — **withheld
zero-day families the defense never trains on**. Family-set disjointness is asserted at
runtime; this run recorded **0 zero-day leakage violations**.

### Pillar III — DEFEND

Harden against diagnosed failures, and refuse to ship a regression.

**Prioritised replay buffer.** Successful evasions are converted into strictly observable
feature rows with zero metadata leakage, weighted by the failure analyser's priority
score.

**Lineage-grouped splitting.** Attack variants are grouped by `(source_txn_id,
attack_family)` *before* the challenger sees them, so sibling variants cannot leak between
the hardening set and the held-out set. Without this, generalisation numbers are
meaningless.

**Weakness-driven adaptive Red.** Each round, Red re-seeds its mutation distribution from
the previous round's `WeaknessProfile` and searches against the *current* champion — not a
frozen snapshot. This is genuine co-evolution, not replayed attacks.

**Multi-objective promotion gate.** A challenger is promoted only if it simultaneously
satisfies detection retention (PR-AUC ≥ 0.90 of champion), robustness, anti-memorisation,
anti-forgetting (retention ≥ 0.95), calibration (ECE ≤ 0.08), false-positive rate
(≤ 0.05), approval rate (≥ 70%), and latency (P95 ≤ 25 ms). Failure triggers deterministic
**rollback**.

---

## Technical Stack & ML Models

| Layer | Choice | Rationale |
|---|---|---|
| Detector | LightGBM, 30 estimators, `max_depth=3`, `scale_pos_weight=171.21` | Tabular gradient boosting is the honest baseline for payment fraud. Class imbalance handled by reweighting, **never SMOTE** — synthetic minority oversampling distorts posterior probabilities and destroys calibration |
| Calibration | Isotonic regression, out-of-time validation split, 10-bin ECE | A risk score that is not a probability cannot drive a cost-sensitive policy |
| Policy | Cost-sensitive expected-loss router | Minimises `E[cost]` across three actions rather than thresholding |
| Explainability | TreeSHAP, on demand | Per-decision attribution without batch cost |
| Attack search | Constrained heuristic mutation under a declarative mask | Reproducible, falsifiable, bounded. RL and diffusion were cut — see Limitations |
| Data | polars | Lazy, vectorised, comfortable past 1M rows on CPU |
| API | FastAPI | Thin adapter: reads artifacts, returns pydantic schemas. **Never computes** |
| Frontend | React 18 + Vite + TypeScript | Renders evidence. Never derives a metric |
| Compute | **CPU only** — Kaggle 4-core sessions | The entire path is tabular. No GPU is used anywhere in this project |

**Contracts.** Every value crossing a module boundary is a pydantic model in
`src/mcdl/schemas.py`. `Transaction` explicitly separates observable fields from hidden
evaluation metadata (`is_fraud`, `attack_family`, `attack_variant`, `hard_negative`), and
Gate 0 asserts the two sets are disjoint and jointly total. Leaking one hidden field into
the feature set is the fastest route to a fraudulent 0.99 PR-AUC.

**Reproducibility.** Deterministic run IDs derived from config hash, seed and git commit.
Canonical JSON serialisation. **SHA-256 provenance for every artifact** — this run
verified **22 of 22**. Double execution at identical seed is bit-for-bit identical.

---

## Evaluation & Results

### Detection

| Metric | Value | Scope |
|---|---|---|
| PR-AUC | **0.9375** | `small` scale — the statistically meaningful figure |
| PR-AUC | 1.0000 ⚠️ | `tiny` scale — **small-sample artifact**, only 5 positives in the validation slice. Not a performance claim |
| False positive rate | **0.0000** | 0 false blocks across 1,398 legitimate transactions |
| ECE / Brier | **0.0000 / 0.0000** | 10-bin, out-of-time validation |
| Decision distribution | 1,398 ALLOW · 0 STEP_UP · 5 BLOCK | — |

### External reality anchor

Evaluated on the **ULB European cardholder benchmark** (Dal Pozzolo et al., 2015,
DOI `10.1109/SSCI.2015.33`) — **284,807 genuine transactions, 492 frauds**. Never used for
training.

| PR-AUC | ROC-AUC | Precision | Recall | FPR | ECE |
|---|---|---|---|---|---|
| **0.8640** | 0.9820 | 0.8910 | 0.7930 | 0.0003 | 0.0042 |

### Adversarial results

| Metric | Value | Scope |
|---|---|---|
| ASR @ 1 / 5 / 20 / 100 probes | **33.33% / 76.67% / 96.67% / 96.67%** | Static Red vs **unhardened** baseline (EXP-007-A) |
| Minimum Evasion Distance | **2.8488** | Same, over successful baseline evasions |
| Held-out variant ASR | **14.55–15.45% → 0.00%** | Baseline champion → hardened challenger, lineage-isolated |
| Generalisation retention | **1.3071** | EXP-007-D |
| Mask violations / invalid attacks | **0 / 0** | Every attack was legal and physically valid |
| Diagnosed failures | **120**, W1/W5/W7 at 33.33% each | `weakness_profile.json` |
| Adaptation cost | ~**4.21 s/round**, 30 retraining steps, 128 MB | `adaptation_cost.json` |

### Latency

**P50 2.287 ms · P95 2.406 ms · P99 2.503 ms** over 200 requests, 0 failures.
Measured via in-process ASGI TestClient against `/api/score`. This is an **HTTP loopback
benchmark**, not internet latency, and is labelled as such everywhere it appears.

### The three findings we are choosing to report

Most submissions report only what worked. These three are the reason this one is
defensible.

**1. Hardening works — but the promotion gate rejected it, four times out of four.**
Every challenger drove held-out ASR to 0.00%, and every challenger was **REJECTED** with
`REJECT_DETECTION_COLLAPSE` — PR-AUC fell to 0.7560–0.8417 against a 0.90 retention
threshold, so the champion was never replaced. The system correctly refused to trade
detection quality for robustness. **A defense that ships a regression is worse than one
that ships nothing**, and the gate is what enforces that.

**2. Zero-day transfer failed, completely.** Against World C — the withheld
`agent_subversion` and `cross_merchant_fanout` families — the attacker achieved
**100.00% ASR at budget 20** with MED 3.7706. Hardening against velocity-based families
does **not** transfer to novel multi-merchant fanout or agent credential-drift topologies.
This is a real, measured generalisation boundary, and it is the single most useful number
in the submission.

**3. The Verifiable-Intent ablation was neutral.** A controlled two-arm counterfactual
(EXP-007-H) removing `is_agent_initiated` and disabling mandate verification produced
**ΔASR = 0.00%, ΔPR-AUC = 0.0000**. The intent engine is functional but demonstrated no
measurable evasion reduction against unadapted agent subversion at tiny scale. We report
it as inconclusive rather than claiming a win.

### Independent research validation (Sparkov, CC0)

Executed against 50,000 real transactions from the Sparkov benchmark
(SHA-256 `12d553ab…545f0`):

| Track | Result | Reading |
|---|---|---|
| **C2ST discriminator** | AUC **0.7780** (95% CI 0.7641–0.7918); synthetic self-split sanity **0.5025** | Our synthetic data *is* distinguishable from real. The 0.5025 self-split confirms the test itself is correctly calibrated |
| **TSTR vs TRTR** | 0.0271 vs 0.4060, gap **−0.3789** | Training on synthetic transfers poorly to real data. Stated plainly |
| **L3 behavioural fidelity** | Interarrival ratio 9.74×, velocity ratio 20.13× | Measured against real-data variability |
| **Graph causal leakage audit** | **0 violations across 28,044 edges** | No temporal or label leakage in the entity graph |

**Verification status:** Gates 0–7 all PASS · **152/152 tests green** · 22/22 artifacts
SHA-256 verified.

---

## Scalability

**Architectural separation.** The laptop never trains at scale, and the serving layer
never computes. Kaggle CPU sessions run the pipeline and write immutable artifacts; the
API reads them. Two consequences, both deliberate: the demo cannot fail the way live
training fails, and the latency figure is a genuine end-to-end HTTP measurement rather
than a `predict()` call timed in a notebook.

**Measured throughput.** End-to-end execution at `tiny` scale completes in **20.57 s**
on CPU — world generation 1.63 s, feature extraction 0.046 s, Blue training 0.042 s,
four co-evolution rounds 16.83 s.

**Path to 1M events.** The stateful simulator sustains 5k–50k events/sec in Python, so 1M
events is 20–200 s. polars joins and rolling windows are comfortable past 1M rows on a
laptop. LightGBM training at 1M × 25 features is minutes on CPU. The known wall is attack
search, addressed by scoring the whole candidate population in a single vectorised call
rather than per-candidate. Graph features use group-by aggregations rather than networkx
traversal, which does not survive 1M rows.

**Cost profile.** Zero GPU hours. Zero paid APIs. No LLM in any scoring path. The entire
system reproduces from a public repository on free-tier CPU compute.

---

## Safety & Responsible Disclosure

Everything runs on synthetic data and open-access public benchmarks. No real cardholder
data, no PII, no production payment systems, and no attacks against live services or
third parties. This is a security research prototype, not an attack platform. KIRA is not
an official implementation of Mastercard Verifiable Intent, Agent Pay, AP2, or EMV 3DS.

---

## 4. Reproducibility Notes — internal metric conflicts

In the interest of the honesty standard this project holds itself to, three metrics have
disagreeing values across artifacts in the current run. **Each figure quoted above names
its scope and source artifact so the reader can see which measurement is being cited.**

| Metric | Values observed | Artifacts | Scope distinction |
|---|---|---|---|
| Held-out ASR (baseline) | `0.0` / `0.1455–0.1545` | EXP-007-D · `promotion_history.json` | Above we cite `promotion_history.json`, which reports per-round baseline vs challenger |
| ASR by budget | all `0.0` / `33/77/97/97%` | `red_metrics.json` · EXP-007-A | `red_metrics.json` reflects the **final hardened** state; EXP-007-A the **unhardened baseline** sweep. Above we cite EXP-007-A and label it |
| MED | `2.8488` / `0.0` / `null` | EXP-007-A · EXP-007-G · `red_metrics.json` | Above we cite EXP-007-A. `null` is correct where zero evasions occurred — MED is undefined, never 0 |

**Action before final submission:** confirm the authoritative source for each with the
pipeline owner and update this table to a single ruling.
