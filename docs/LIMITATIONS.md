# LIMITATIONS

Draft for the technical report. Written before the build, updated as things land.

Stating what we cut and why reads as judgement. Silence about it reads as
ignorance. This file is an asset, not an apology.

---

## 1. What this system is

A controlled adversarial payment-security laboratory. It identifies attack
families, generates constrained synthetic attacks, evaluates their fidelity and
evasion, detects them with a multi-signal defence, stores the failures, and
evaluates whether subsequent challenger models become measurably harder to defeat.

## 2. What this system is not

- Not a production fraud system, and not benchmarked against one
- Not connected to any real payment rail
- Not trained on real cardholder data or PII
- Not an implementation of Mastercard's Verifiable Intent, Agent Pay, AP2, or EMV 3DS
- Not a privacy guarantee — we report anti-memorisation evidence, not a proof

---

## 3. Data limitations

**The world is synthetic.** Our simulator is calibrated against a public reference
dataset, but it is our own model of payment behaviour. Behaviour it does not model
is behaviour our detector was never asked to handle.

**The reference dataset is itself synthetic.** Sparkov is rule-generated, not real
transactions. It is a reasonable behavioural reference, not ground truth. Anyone
who knows the dataset will notice this, so we say it first.

**No device or IP columns in the reference data.** Device-level graph structure
(P3 of the fidelity filter) is a modelling assumption, not a fitted one. The
customer–merchant structure is calibrated; the device fan-out is not.

**Scale.** Development ran at 50k events; the final artifacts were generated at
[TBD]. Behaviour at production scale (billions of transactions) is not demonstrated
and we make no claim about it.

---

## 4. Modelling limitations

**Single detector family.** LightGBM champion, XGBoost only for the ensemble
ablation. No deep learning. Justified by the evidence-before-architecture rule, but
it does mean we have not tested whether a sequence model would find something the
tree ensemble misses.

**Cheap graph features, no GNN.** Degree, shared-device counts and neighbour fraud
rate capture much of the relational story at a fraction of the cost. Whether a
graph neural network would add measurable lift **is untested** — we cut it rather
than half-build it. That is a stated gap, not a claim that it would not help.

**Label delay is modelled, not learned.** We gate label-reading features behind a
fixed 7-day lag. Real chargeback latency is a distribution, not a constant.

**Calibration on limited positives.** Fraud is rare, so isotonic calibration is
fitted on relatively few positive examples. ECE is reported with that caveat.

---

## 5. Red team limitations

**The threat model is explicit and narrow.** The attacker probes the deployed
scorer within a fixed query budget and mutates only fields the mutability mask
marks as attacker-controllable. We do not model insider access, model theft,
supply-chain compromise, or social engineering of the victim.

**Search is heuristic.** Batch-vectorised constrained mutation, not a proof of the
minimal adversarial perturbation. Minimum Evasion Distance is an **upper bound** on
the true minimum — a better search might find a smaller one.

**No gradient attacks.** CAA and CAPGD from the literature require gradients and do
not apply to a tree ensemble. This is a property of the model class, not an
oversight.

**Five attack families, not ten.** R1 ATO, R2 velocity burst, R3 low-and-slow,
R4 mule ring, R8 agentic intent drift. Chosen to span tabular, temporal, graph and
agentic surfaces. Coverage of the full attack surface matrix is partial and we
report the fraction covered rather than implying completeness.

---

## 6. Evaluation limitations

**Circularity is mitigated, not eliminated.** We train on our simulator and test on
our simulator, with out-of-time splits, disjoint attack ids, separate seeds, hidden
families, and an external anchor. The anchor is what makes the numbers mean
anything outside our own world, and it is the single most important caveat on
every internal metric.

**The held-out-variant protocol tests generalisation within a family**, and
unseen-family transfer tests across families. Neither proves robustness against an
attack type nobody has thought of.

**C2ST sample sizes for attacks are small.** Conditional plausibility is measured
against real fraud rows only, of which there are few. We report cross-validated AUC
with confidence intervals and do not over-claim from a wide interval.

**Latency is measured on free-tier hardware** (2 vCPU) with **in-process state**.
A production deployment would need an external state store, adding a network hop
we have not measured. The reported figures are honest for this configuration and
should not be read as a production SLA.

**Three co-evolution rounds.** Enough to show a trend, not enough to characterise
convergence or to claim the loop reaches an equilibrium.

---

## 7. Components deliberately not built

Every item was Tier-2 or Tier-3 in our own priority scheme. In a three-day build
none would produce a defensible measured result, and a half-working one is a
liability in a report because it invites a question we cannot answer.

| Cut | Reason |
|---|---|
| GNN (CARE-GNN, PC-GNN, HOT-GNN, GraphSAGE) | Cheap graph features first; GNN only if they showed lift. No time to test. |
| Reinforcement learning (PPO, DQN) | Would not beat the search baseline within the time available, and could not be ablated fairly |
| Diffusion / TabDDPM generation | Our stateful simulator is the differentiator; a second generator adds no measurable value |
| STG-DGR, generative replay, EWC, distillation | Continual-learning research beyond a three-day scope |
| Conformal prediction | Requires assumptions we cannot validate in the time |
| ADWIN drift detection | Meaningful only over a longer horizon than we simulate |
| PSRO / Stackelberg co-play | Multi-round game theory needs far more rounds than three |
| RAG evidence investigator | No API budget, and no measurable contribution to the thesis |
| CatBoost | Install friction, marginal signal over LightGBM + XGBoost |
| Weights & Biases | Run manifests already give reproducibility with no external dependency |

**What we would do with more time**, in priority order: (1) test whether a GNN adds
lift over the cheap graph features; (2) extend to 10+ co-evolution rounds to look
for convergence; (3) replace the fixed label delay with a fitted distribution;
(4) run the fidelity filter against a second, non-synthetic reference dataset;
(5) measure latency with an external state store.

---

## 8. Novelty — what we do and do not claim

**We do not claim** to have invented adversarial fraud generation, red/blue
co-evolution, or graph-based fraud detection. Prior art exists: evasion attacks
against banking fraud systems (USENIX RAID 2020), multi-objective evolutionary
attacks on tabular data, and LLM-driven red/blue co-evolution frameworks published
in 2025–26 with results shaped much like ours.

**We do claim** a specific combination and, more importantly, a **measurement
protocol**: a payment-specific stateful world with hard negatives; a declarative
mutability mask that keeps attacks feasible; an agentic mandate layer; and
evaluation that reports attack success at a realistic query budget, minimum evasion
distance, held-out-variant generalisation, and behavioural fidelity normalised to
real-data variability.

The contribution is that the numbers are falsifiable, not that the architecture is
unprecedented.

---

## 9. Reproducibility

Every reported number carries a `run_id`, a git commit, a config hash and a seed.
Re-running the same config reproduces the metrics. Anything we could not measure is
reported as **not measured** rather than omitted or filled with a zero.

Free-tier compute means some experiments were run once rather than across multiple
seeds. Where that is the case it is stated, and single-run results are not
presented as if they carried error bars.

---

## 10. Responsible use

Everything operates on synthetic or public data inside a controlled simulation. No
real cardholder data, no PII, no production systems, no attacks against live
services or third parties.

The attack engine is a research instrument scoped to our own simulated world and
our own detector. It is not a general-purpose fraud toolkit, and it is not useful
against any real payment system.
