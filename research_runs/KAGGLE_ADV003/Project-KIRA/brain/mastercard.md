Yes. I’ll incorporate it, but I’m making **two evidence-based corrections** while doing so rather than blindly freezing claims that aren't fully supported.

Most importantly, **P19 should be “explicit class-imbalance handling,” not “SMOTE is mandatory.”** SMOTE/ADASYN can be useful, but for tree-based fraud models they can also hurt performance or distort the data. We should test them rather than mandate them.

Also, the **TabDDPM-Aug result is real**, but the paper currently shown by the publisher is dated January 2027, so we should treat it as **research evidence/candidate technique**, not as something we can claim was established before our August 2026 project deadline. ([ScienceDirect][1])

The agentic-payment direction, however, is strongly relevant: Mastercard itself has completed authenticated agentic transactions in India and is explicitly building infrastructure for high-frequency machine-driven payments. ([Mastercard][2])

---

# STEP 1 — FINALIZED PROJECT FOUNDATION v1.1

**Status: FROZEN**

This is now the version we carry forward. Any change after this point should require an explicit reason and evidence.

---

## 1. Project Mission

> **Build an adaptive Red-Team/Blue-Team AI laboratory for payment security that identifies emerging GenAI-enabled fraud attacks, generates high-fidelity synthetic attack behaviour, detects and mitigates those attacks, and continuously feeds successful evasions back into the defense for hardening.**

This directly maps to Mastercard's:

**Identify → Generate → Defend**

and its closed-loop requirement. 

---

# 2. Fundamental System

```text
                    MASTERCARD AI DEFENSE LAB
                              │
                              ▼
                    ┌────────────────────┐
                    │      IDENTIFY      │
                    │                    │
                    │ Threat intelligence│
                    │ Attack taxonomy    │
                    │ Attack hypotheses  │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │      GENERATE      │
                    │                    │
                    │ Red-team attacks   │
                    │ Behavioral         │
                    │ simulation         │
                    │ Adaptive attacks   │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │  SYNTHETIC PAYMENT │
                    │     ENVIRONMENT    │
                    │                    │
                    │ Accounts           │
                    │ Transactions       │
                    │ Merchants          │
                    │ Devices            │
                    │ Network entities   │
                    │ Time / sequences   │
                    └─────────┬──────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
          TABULAR/        TEMPORAL/     RELATIONAL/
          BEHAVIORAL      SEQUENTIAL      GRAPH
          DEFENSE         DEFENSE        DEFENSE
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                    ┌────────────────────┐
                    │  RISK + DECISION   │
                    │                    │
                    │ Score              │
                    │ Explain            │
                    │ Mitigate           │
                    └─────────┬──────────┘
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
               ALLOW        STEP-UP       BLOCK
                              │
                              ▼
                    ┌────────────────────┐
                    │      FEEDBACK      │
                    │                    │
                    │ Missed attacks     │
                    │ Successful attacks │
                    │ Hard examples      │
                    └─────────┬──────────┘
                              │
                              └──────────────►
                                  RED TEAM
                                  ADAPTS
```

### **This flowchart is now the master project flowchart.**

As we finalize every subsequent step, **we will edit this same architecture rather than creating disconnected diagrams**.

At the end of the project, this becomes the complete system architecture.

---

# 3. P1 — Closed-Loop Architecture

### FROZEN

The system must implement:

> **Identify → Generate → Defend → Feedback**

The feedback must be functional.

Minimum:

```text
Attack
  ↓
Defense
  ↓
Detected / Missed
  ↓
Outcome recorded
  ↓
Attack strategy updated
```

Target:

```text
Defense weakness
      ↓
Red-team adaptation
      ↓
harder attack
      ↓
Blue-team hardening
      ↓
new weakness
      ↓
repeat
```

---

# 4. P2 — Attack Diversity

### FROZEN

We will create a structured attack taxonomy covering multiple categories rather than variations of one fraud pattern.

Candidate families include:

* identity fraud
* account takeover
* social engineering
* AI-generated impersonation
* transaction manipulation
* automated fraud
* coordinated fraud
* device/network abuse
* merchant-side abuse
* synthetic identity
* agentic payment abuse.

The **final taxonomy is Step 2**, because Mastercard explicitly asks us to be thorough and exhaustive. 

---

# 5. P3 — Attack Fidelity

### FROZEN

Synthetic attacks must be demonstrably realistic.

We will evaluate:

| Dimension | Example                      |
| --------- | ---------------------------- |
| Amount    | Distribution                 |
| Time      | Temporal distribution        |
| Velocity  | Frequency patterns           |
| Merchant  | Merchant relationships       |
| Geography | Location transitions         |
| Device    | Device/account relationships |
| Account   | Behavioral consistency       |
| Network   | Graph structure              |
| Sequence  | Event ordering               |

This is directly aligned with Mastercard's requirement for realistic distributions, behaviours and edge cases. 

---

# 6. P4 — Adaptive Attack Capability

### FROZEN AS A TARGET

The red team should eventually be able to:

```text
Attack
 ↓
Observe defense
 ↓
Evaluate outcome
 ↓
Modify strategy
 ↓
Attack again
```

Implementation remains open:

* search
* evolutionary optimization
* RL
* agent
* LLM-assisted planning
* hybrid.

We do **not** automatically choose an LLM.

---

# 7. P5 — Strong Blue-Team Baseline

### FROZEN

Initial candidates:

* LightGBM
* XGBoost
* CatBoost

Potential ensemble.

This is supported by fraud-competition evidence and research. The IEEE-CIS ecosystem repeatedly demonstrates the competitiveness of these models with strong feature engineering, and recent research also evaluates XGBoost/LightGBM/CatBoost stacking for fraud detection. ([contecsi.tecsi.org][3])

### Rule

> **No sophisticated model replaces the baseline without empirical evidence.**

---

# 8. P6 — Behavioral Intelligence

### FROZEN

We must model behavior, not simply individual transaction attributes.

Examples:

```text
current amount
vs.
customer's historical amount distribution
```

and:

```text
new device
+
new geography
+
unusual velocity
+
merchant deviation
```

We will investigate:

* historical aggregates
* velocity
* recency
* personal baselines
* merchant behavior
* device behavior
* account behavior
* entity-level patterns.

---

# 9. P7 — Temporal Intelligence

### FROZEN

Transactions are sequential events.

We will explicitly investigate:

```text
t-3 → t-2 → t-1 → t
```

including:

* time since previous transaction
* rolling transaction count
* rolling amount
* merchant transitions
* geography transitions
* device transitions
* behavioral changes.

A temporal deep-learning model is **optional**.

Temporal information itself is **mandatory**.

---

# 10. P8 — Relational Intelligence

### FROZEN AS A CAPABILITY

The system must investigate relationships such as:

```text
Account
   ↕
Device
   ↕
IP
   ↕
Merchant
   ↕
Transaction
```

But:

> **GNN is not mandatory.**

Candidates now include:

```text
Graph
 ├── relational features
 ├── GraphSAGE
 ├── GAT
 ├── R-GCN
 ├── CARE-GNN
 ├── PC-GNN
 └── HOT-GNN
```

### CARE-GNN

Useful for camouflaged-fraud problems and already verified through its official implementation.

### PC-GNN

Added as a candidate specifically because class imbalance is a major fraud-detection issue.

### HOT-GNN

Added to the **research candidate list**, but we will independently verify the claimed benchmark numbers before using them in our final report.

This is important: **we don't put unverified 0.9873/0.9168/0.9126 claims into our submission.**

---

# 11. P9 — Defense Must Produce an Action

### FROZEN

The defense must eventually translate risk into an action:

```text
LOW
 → ALLOW

MEDIUM
 → STEP-UP / VERIFY

HIGH
 → HOLD / REVIEW

CRITICAL
 → BLOCK
```

The exact thresholds will be learned/validated later.

This directly corresponds to Mastercard's request for detection, flagging and mitigation. 

---

# 12. P10 — Explainability

### FROZEN

The system should explain significant decisions.

Example:

```text
HIGH RISK

Why?

• abnormal velocity
• new device
• unusual geography
• merchant deviation
• device connected to multiple accounts
```

SHAP is a candidate implementation.

It is **not mandatory**.

---

# 13. P11 — Evidence Before Architecture

### FROZEN — CORE RULE

Every major component must answer:

1. What problem does it solve?
2. Why isn't the baseline sufficient?
3. What measurable improvement does it provide?
4. What cost does it introduce?
5. Is that improvement worth the cost?

Therefore:

```text
Research
   ↓
Candidate
   ↓
Experiment
   ↓
Ablation
   ↓
Evidence
   ↓
Architecture decision
```

This remains one of the most important rules of the project.

---

# 14. P12 — Functional Novelty

### FROZEN

We are **not** claiming novelty because we combine many fashionable technologies.

Our current novelty hypothesis is:

> **Defense-aware adaptive fraud generation: attacks are deliberately generated to challenge the current defense, successful evasions are identified, and those failures are fed back into defensive hardening.**

We will verify in Step 2 whether this is genuinely differentiated from existing systems.

If competitive research reveals a stronger gap, **we are allowed to replace this hypothesis**.

That is exactly what evidence-first development means.

---

# 15. P13 — Synthetic / Sandbox Environment

### FROZEN

All attack simulation operates in:

* synthetic data
* anonymized data
* authorized competition data
* controlled simulation.

No:

* real cardholder data
* PII
* production payment data
* attacks against live payment systems
* attacks against third parties. 

---

# 16. P14 — Evaluation

### FROZEN

## Red Team

Measure:

* attack diversity
* attack fidelity
* attack success/evasion
* attack coverage
* adaptation.

## Blue Team

Measure:

* precision
* recall
* F1
* ROC-AUC
* PR-AUC
* false-positive rate
* false-negative rate
* calibration where useful
* latency.

## System

Measure:

* robustness
* scalability
* adaptability
* mitigation effectiveness.

---

# 17. P15 — Mandatory Final Deliverables

### FROZEN

We must deliver:

1. **Public GitHub repository**
2. **Solution walkthrough/document**
3. **Working web prototype with presentable UI**

These are explicitly required by the event terms. 

The Kaggle instructions further specify:

```text
Kaggle Writeup
      ↓
Project description
      ↓
TeamName.docx
      ↓
Public GitHub TeamName
      ↓
Submit
```

---

# 18. P16 — Kaggle Strategy

### FROZEN

The Kaggle track will be:

```text
Dataset forensics
       ↓
Validation design
       ↓
Feature engineering
       ↓
Strong baselines
       ↓
Model comparison
       ↓
Ensemble
       ↓
Error analysis
       ↓
Submission
```

The private leaderboard determines final Kaggle standing, so we will not blindly optimize for public leaderboard movement. 

---

# 19. P17 — Latency

### FROZEN

**Measure latency.**

Not:

> “must be 50 ms.”

The final report should contain actual measurements.

```text
Feature generation
+
Model inference
+
Decision logic
=
End-to-end latency
```

This keeps our engineering claim honest.

---

# 20. P18 — Technology Candidates

### FROZEN AS A CANDIDATE POOL

```text
BASE MODELS
 ├── LightGBM
 ├── XGBoost
 └── CatBoost

TEMPORAL
 ├── behavioral features
 ├── sequence models
 └── temporal attention

GRAPH
 ├── relational features
 ├── GraphSAGE
 ├── GAT
 ├── R-GCN
 ├── CARE-GNN
 ├── PC-GNN
 └── HOT-GNN

GENERATION
 ├── probabilistic simulation
 ├── GAN
 ├── diffusion
 ├── constrained generation
 └── hybrid

ADAPTATION
 ├── search
 ├── evolutionary optimization
 ├── RL
 ├── agents
 └── LLM-assisted planning
```

None is guaranteed to survive.

---

# 21. P19 — Class-Imbalance Handling

### **NEW — FROZEN**

The defense must explicitly address severe fraud-class imbalance.

But I'm deliberately changing your friend's wording from:

> “SMOTE/ADASYN/Focal Loss must be used”

to:

> **“Class imbalance must be explicitly analyzed and handled using the method empirically appropriate for the dataset and model.”**

Candidates include:

```text
Class weighting
        OR
SMOTE
        OR
ADASYN
        OR
Focal loss
        OR
Under/over-sampling
        OR
Threshold optimization
        OR
Hybrid approaches
```

Why this wording?

Because **SMOTE is not automatically the correct answer**. Synthetic oversampling can distort temporal/relational structure and can cause leakage if applied incorrectly.

So our frozen requirement is:

> **We must test and document the imbalance strategy.**

Not:

> **We must use SMOTE.**

This is a stronger engineering decision.

---

# 22. P20 — Agentic Payment Fraud

I am adding this as a **research priority**, not a mandatory final feature.

Why?

Because this is unusually aligned with Mastercard's current direction.

Mastercard has publicly demonstrated authenticated agentic commerce in India. ([Mastercard][2])

It has also described AI agents executing transactions autonomously within defined permissions and audit/security controls. ([Mastercard][4])

And in June 2026 Mastercard launched Agent Pay for Machines for high-volume, programmatic machine payments. ([Mastercard Investor Relations][5])

That creates a very relevant threat surface:

```text
Human-authorized AI agent
          ↓
autonomous actions
          ↓
many transactions
          ↓
high velocity
          ↓
adaptive behavior
          ↓
potential abuse
```

So Step 2 must investigate:

> **What does fraud look like when the “customer” is an AI agent rather than a human?**

This could become one of our strongest differentiators.

---

# 23. P21 — Synthetic Generation Candidate

Diffusion-based tabular generation remains a candidate.

Your supplied research identifies TabDDPM-style methods as promising because they model joint feature distributions rather than independently sampling columns. 

A newer TabDDPM-Aug publication reports strong utility/fidelity/privacy results across 13 benchmarks. ([ScienceDirect][1])

### But:

We **will not claim those results as established competition evidence** until we verify publication timing and applicability.

And we certainly won't automatically build diffusion.

The question will be:

> Does a diffusion generator actually improve the fidelity and usefulness of our attacks enough to justify its implementation cost?

---

# 24. P22 — Time-Budget Governance

### **FROZEN**

Because we are working against the **31 August 2026 deadline**, we need explicit time gates.

Our working schedule is:

| Step                                      | Maximum allocation |
| ----------------------------------------- | -----------------: |
| **Step 1 — Foundation**                   |          Completed |
| **Step 2 — Competitive intelligence**     |            ≤ 1 day |
| **Step 3 — Kaggle baseline**              |           ≤ 2 days |
| **Step 4 — Attack generation**            |         ≤ 1.5 days |
| **Step 5 — Integration + UI + artifacts** |         ≤ 1.5 days |

This is a **governance rule**, not a promise that every phase needs exactly that much time.

If a component is consuming time without producing measurable value:

> **Cut it.**

No attachment to an architecture because we spent time building it.

---

# 25. P23 — No Architecture Bloat

### NEW — FROZEN

We explicitly prohibit technology stacking without evidence.

For example:

```text
GNN
+
Transformer
+
LLM
+
RL
+
Diffusion
+
GAN
+
Knowledge graph
+
Blockchain
```

does **not** automatically equal innovation.

Every added component creates:

* implementation risk
* integration risk
* debugging cost
* latency
* explanation difficulty
* demonstration complexity.

Our target is:

> **Minimum architecture that achieves maximum measurable differentiation.**

---

# 26. P24 — Competitive Gap Requirement

### NEW — FROZEN

Before finalizing the major architecture, we must establish:

```text
Existing solutions
        ↓
What they already solve
        ↓
What they don't solve
        ↓
What competitors are likely to build
        ↓
Our unique capability
        ↓
Evidence
```

This means Step 2 isn't optional research.

**It directly determines the architecture.**

---

# 27. P25 — Every Major Claim Needs Evidence

### NEW — FROZEN

For the final submission:

> **No numerical claim without a reproducible source or experiment.**

Examples:

❌ “Our model is 30% better.”

Unless we show the experiment.

❌ “Our attack generator is realistic.”

Unless we measure fidelity.

❌ “Our GNN beats XGBoost.”

Unless we perform an ablation.

❌ “Our approach works in real time.”

Unless we measure latency.

This will make our solution substantially more defensible during judging.

---

# 28. Final Frozen Architecture After Step 1

So our master flow is now:

```text
                         ┌─────────────────────┐
                         │       IDENTIFY      │
                         │                     │
                         │ Threat intelligence │
                         │ Fraud taxonomy      │
                         │ Attack hypotheses   │
                         │ Agentic threats     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       GENERATE      │
                         │                     │
                         │ Attack planner      │
                         │ Attack generator    │
                         │ Behavioral simulator│
                         │ Adaptive attacker   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ SYNTHETIC PAYMENT   │
                         │ ENVIRONMENT          │
                         │                     │
                         │ Accounts            │
                         │ Transactions        │
                         │ Merchants           │
                         │ Devices             │
                         │ IP/network          │
                         │ Temporal state      │
                         │ Agentic actors      │
                         └──────────┬──────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
       ┌────────────┐        ┌────────────┐        ┌────────────┐
       │  TABULAR   │        │  TEMPORAL  │        │ RELATIONAL │
       │  /BEHAVIOR │        │ /SEQUENCE  │        │   /GRAPH   │
       │            │        │            │        │            │
       │ XGB/LGBM/  │        │ Candidate  │        │ Candidate  │
       │ CatBoost   │        │ models     │        │ GNNs       │
       └─────┬──────┘        └─────┬──────┘        └─────┬──────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │   RISK + DECISION   │
                         │                     │
                         │ Risk score          │
                         │ Explainability      │
                         │ Threshold/policy    │
                         │ Mitigation          │
                         └──────────┬──────────┘
                                    │
                      ┌─────────────┼─────────────┐
                      ▼             ▼             ▼
                    ALLOW        STEP-UP         BLOCK
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FEEDBACK       │
                         │                     │
                         │ Missed attacks     │
                         │ Successful attacks │
                         │ Hard examples      │
                         │ Model weaknesses   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   RED TEAM ADAPTS   │
                         └──────────┬──────────┘
                                    │
                                    └───────────────►
                                      NEXT ATTACK
```

### This is now our **Step-1 master flowchart**.

From Step 2 onward, we'll keep modifying this same conceptual flow as decisions become evidence-backed.

---

# 29. Final Step-1 checklist

| Requirement                   | Status                             |
| ----------------------------- | ---------------------------------- |
| Identify                      | **Frozen**                         |
| Generate                      | **Frozen**                         |
| Defend                        | **Frozen**                         |
| Feedback loop                 | **Frozen**                         |
| Attack diversity              | **Frozen**                         |
| Attack fidelity               | **Frozen**                         |
| Adaptive attacks              | **Frozen target**                  |
| Behavioral intelligence       | **Frozen**                         |
| Temporal intelligence         | **Frozen**                         |
| Relational intelligence       | **Frozen**                         |
| Strong tabular baseline       | **Frozen**                         |
| Class imbalance handling      | **Frozen**                         |
| Mitigation                    | **Frozen**                         |
| Explainability                | **Frozen**                         |
| Empirical ablations           | **Frozen**                         |
| Functional novelty            | **Frozen**                         |
| Agentic fraud investigation   | **Frozen research priority**       |
| Synthetic/sandbox environment | **Frozen**                         |
| Latency measurement           | **Frozen**                         |
| GNN                           | **Candidate**                      |
| CARE-GNN                      | **Candidate**                      |
| PC-GNN                        | **Candidate**                      |
| HOT-GNN                       | **Candidate / needs verification** |
| LLM                           | **Candidate**                      |
| RL                            | **Candidate**                      |
| Diffusion                     | **Candidate**                      |
| GAN                           | **Candidate**                      |
| Final architecture            | **Not yet frozen**                 |
| Competitive gap analysis      | **Required next step**             |
| Time budget                   | **Frozen**                         |

---

# STEP 1 — FINAL STATUS

## **APPROVED FOUNDATION v1.1**

I would now consider **Step 1 closed**.

The important change from the previous version is that we have added the three things your supplied assessment correctly identified:

1. **Explicit class-imbalance handling**
2. **PC-GNN + HOT-GNN to the candidate research pool**
3. **Hard time-budget governance**

And I've added two more safeguards that I think are necessary:

4. **Competitive-gap requirement**
5. **No architecture bloat / evidence for every major claim**

The agentic-payment direction is also now a formal **research priority**, because Mastercard's own 2026 payment strategy makes agentic transactions a very current and relevant attack surface. ([Mastercard][2])

**We do not yet choose the attack generator, GNN, sequence model, LLM, RL algorithm, or diffusion model.**

# Step2

# STEP 2 — FINALIZED: COMPETITIVE INTELLIGENCE, GAP ANALYSIS & ARCHITECTURE DIRECTION

**Version: 2.1 — Fixed after research + review of the v2.0 blueprint**

This is the version we carry forward into Step 3. I have incorporated the useful material from the uploaded blueprint while explicitly separating **frozen requirements** from **research candidates**. The uploaded blueprint itself defines the mission as an adaptive closed-loop defense laboratory focused on GenAI/agentic attacks, high-fidelity adversarial transactions, multi-signal defense, and continuous hardening. 

---

# 2.1 What Step 2 was supposed to determine

Step 1 established **what Mastercard asks us to build**.

Step 2 answers:

> **What has already been done, what do strong competitors typically do, where is the real gap, and therefore where should our solution differentiate?**

We investigated five areas:

```text
Kaggle fraud winners
        ↓
GitHub implementations
        ↓
Graph fraud research
        ↓
Synthetic fraud / simulation systems
        ↓
Mastercard's agentic-commerce direction
```

The conclusion is that **technology stacking is not our competitive advantage**.

Our advantage must come from the **interaction between attack generation and defense**.

---

# 2.2 Competitive Landscape

## A. Kaggle fraud competitions

Strong fraud competition solutions repeatedly demonstrate the importance of:

* feature engineering
* entity-level behavior
* historical aggregates
* temporal context
* gradient-boosting models
* model ensembles
* careful validation.

The IEEE-CIS Fraud Detection first-place FraudSquad work is particularly relevant because it focuses on identifying behavioral/entity structure rather than treating every transaction as an isolated row. [FraudSquad — IEEE-CIS 1st Place Solution Part 2](https://www.kaggle.com/competitions/ieee-fraud-detection/writeups/fraudsquad-1st-place-solution-part-2?utm_source=chatgpt.com)

Public implementations also demonstrate extensive LightGBM/CatBoost/XGBoost use and ensemble approaches. [Kaggle fraud ensemble implementation](https://github.com/KovalevEvgeny/kaggle-fraud-detection?utm_source=chatgpt.com)

### Strategic conclusion

Our Kaggle defense must begin with:

> **A competition-grade tabular/behavioral baseline.**

Not a GNN.

Not an LLM.

Not diffusion.

---

# 2.3 Entity intelligence is more important than raw transaction classification

A weak system sees:

```text
Transaction
 ├── amount
 ├── merchant
 ├── country
 └── timestamp
```

A stronger system asks:

```text
Who made it?
What normally happens for this entity?
What changed?
What device is involved?
What other accounts/entities are connected?
How quickly is behavior changing?
```

Therefore our Blue Team should ultimately combine:

```text
Transaction features
+
Behavioral features
+
Temporal features
+
Relational features
```

The relative contribution of each layer will be **experimentally determined in Step 3**.

---

# 2.4 Gradient-Boosting Ensemble

## STATUS: **FROZEN AS BASELINE DIRECTION**

Candidate backbone:

```text
LightGBM
XGBoost
CatBoost
```

Potential ensemble:

```text
              ┌── LightGBM
Features ─────┼── XGBoost
              └── CatBoost
                    ↓
                Ensemble
```

The uploaded blueprint similarly specifies a GBDT ensemble using these three models. 

### Important restriction

We are **not freezing ensemble weights**.

We will test:

1. individual models
2. combinations
3. calibration
4. stacking/blending

and retain the ensemble **only if it provides measurable improvement on appropriate validation**.

---

# 2.5 Behavioral Intelligence

## STATUS: **FROZEN**

We will engineer features describing behavior relative to the entity's history.

Examples:

```text
current amount
      vs
historical amount distribution
```

and:

```text
transactions in last 5 min
transactions in last 1 hr
transactions in last 24 hr

current merchant
      vs
historical merchant behavior

current device
      vs
known devices

current geography
      vs
historical geography
```

This is one of the strongest lessons from successful fraud competitions.

---

# 2.6 Temporal Intelligence

## STATUS: **FROZEN**

Fraud is not only about *what* happened.

It is about:

> **what happened immediately before it.**

We will investigate:

* inter-transaction time
* rolling velocity
* amount acceleration
* transaction bursts
* merchant transitions
* geographic transitions
* device transitions
* session behavior
* behavioral drift.

The uploaded blueprint explicitly includes temporal dynamics and inter-arrival analysis. 

### But:

We do **not** automatically require a Transformer/RNN/temporal GNN.

Temporal information is mandatory.

A sophisticated temporal model is optional.

---

# 2.7 Relational Intelligence

## STATUS: **FROZEN AS A CAPABILITY**

We will investigate relationships such as:

```text
Account
   │
   ├── Device
   │
   ├── IP
   │
   ├── Merchant
   │
   └── Transactions
```

This enables detection of coordinated behavior.

However:

> **Graph Neural Networks are not our novelty.**

Graph fraud detection is already an established field.

---

# 2.8 Graph Model Candidate Pool

The following remain candidates:

```text
Relational features
GraphSAGE
GAT
R-GCN
CARE-GNN
PC-GNN
HOT-GNN
DynBERG
```

### CARE-GNN

Candidate for camouflaged fraud.

### PC-GNN

Candidate for highly imbalanced fraud networks.

### HOT-GNN

Candidate for heterophily/outlier-aware fraud detection.

### DynBERG

Candidate for dynamic temporal graph representation.

The uploaded blueprint proposes HOT-GNN and DynBERG as an asynchronous intelligence layer. 

### Critical rule

They are **not frozen architectural components**.

They must first prove:

```text
GBDT
  ↓
relational features
  ↓
GNN candidate
  ↓
OOT comparison
  ↓
Does performance improve?
```

If the answer is no:

> **We remove the GNN.**

That is part of our evidence-before-architecture rule.

---

# 2.9 Synthetic Fraud Generation

## STATUS: **FROZEN AS A REQUIREMENT**

We need a mechanism capable of generating realistic attacks.

But synthetic data generation itself is **not our novelty**.

Existing systems already demonstrate synthetic financial transaction generation and fraud simulation, including AMLSim and PaySim.

Therefore:

> **“We generate synthetic fraud” is not enough to differentiate us.**

---

# 2.10 Our Generator Must Have Two Levels

This is now part of the architecture direction.

## Level 1 — Deterministic Scenario Engine

Reliable and reproducible attacks:

```text
Synthetic identity
Account takeover
Velocity abuse
Device farms
Merchant compromise
Coordinated accounts
Mule chains
Probing
```

## Level 2 — Adaptive Attack Engine

The attacker modifies controllable dimensions such as:

```text
amount
timing
merchant
device/session
network attributes
velocity
sequence
coordination structure
```

according to defense feedback.

This ensures that even if the sophisticated adaptive layer fails, we still have a functioning Red Team.

---

# 2.11 Attack Mutability Mask

## STATUS: **FROZEN**

This is one of the strongest additions from the uploaded blueprint.

We explicitly distinguish:

### Attacker-controlled variables

Potential examples:

```text
amount
timestamp
merchant interaction
device/session attributes
network/routing attributes
transaction sequence
```

### Historical/immutable state

Potential examples:

```text
account age
historical spending
issuing-country history
previously established identity state
```

The blueprint formalizes this using a binary mutability mask. 

Conceptually:

[
x_{synthetic}
=============

m\odot x_{adversarial}
+
(1-m)\odot x_{immutable}
]

### Why this matters

Otherwise the generator could cheat.

For example, it shouldn't be allowed to simultaneously change:

```text
current transaction
+
historical customer profile
```

just to fool the detector.

That wouldn't represent a realistic attack.

---

# 2.12 Attack Fidelity

## STATUS: **FROZEN**

We need to prove that generated attacks are realistic.

We will evaluate several dimensions:

### Distribution

* marginal distributions
* categorical distributions
* amount distributions

### Correlation

* feature relationships
* behavioral relationships

### Temporal

* inter-arrival times
* burst patterns
* sequence structure

### Entity consistency

* account/device relationships
* merchant behavior

### Network

* graph topology
* coordinated structures

### Tail behavior

* extreme amounts
* rare behaviors
* unusual but plausible events.

The uploaded blueprint proposes KS-based marginal checks, correlation drift and inter-arrival analysis. 

### Important correction

The numerical thresholds such as:

```text
KS < 0.05
correlation drift < 0.35
```

are **not yet universal frozen requirements**.

We'll determine appropriate thresholds based on the actual dataset and statistical test.

---

# 2.13 Attack Success Rate

## STATUS: **NEW FROZEN METRIC**

We need to measure whether attacks actually defeat the defense.

[
ASR =
\frac{\text{successful evasions}}
{\text{total attack attempts}}
]

We will track:

```text
Round 0 → ASR₀
Round 1 → ASR₁
Round 2 → ASR₂
...
```

The Red Team should become harder to detect.

The Blue Team should simultaneously become stronger.

This is much more meaningful than simply showing generated synthetic rows.

---

# 2.14 Attack Fidelity ≠ Attack Effectiveness

These must remain separate.

### Fidelity asks:

> Does this look like a realistic transaction/attack?

### Effectiveness asks:

> Does it evade the detector?

Therefore:

```text
                    ATTACK
                       │
              ┌────────┴────────┐
              ▼                 ▼
          REALISTIC?         EVADES?
              │                 │
          Fidelity             ASR
```

A ridiculous synthetic transaction that fools the detector isn't a useful attack.

A realistic transaction that repeatedly evades the detector is.

---

# 2.15 Core Innovation Hypothesis

## **STATUS: PRIMARY NOVELTY HYPOTHESIS**

Our competitive differentiation is **not**:

* GNN
* LLM
* diffusion
* synthetic data
* agent
* ensemble.

Those are technologies.

Our proposed innovation is the **interaction**:

```text
REALISTIC ATTACK
       ↓
PAYMENT ENVIRONMENT
       ↓
DEFENSE
       ↓
ATTACK OUTCOME
       ↓
FALSE NEGATIVE ANALYSIS
       ↓
ATTACK ADAPTATION
       ↓
HARDER ATTACK
       ↓
DEFENSE HARDENING
       ↓
REPEAT
```

Therefore the current working name for the concept is:

# **Adaptive Adversarial Payment Security**

---

# 2.16 Closed-Loop Hardening

## STATUS: **FROZEN**

The Red Team and Blue Team are coupled.

```text
              RED TEAM
                  │
                  ▼
             Attack Set
                  │
                  ▼
              BLUE TEAM
                  │
             ┌────┴────┐
             ▼         ▼
          Detected   Missed
             │         │
             │         ▼
             │     Replay Buffer
             │         │
             │         ▼
             │   Attack Adaptation
             │         │
             │         ▼
             │    New Attacks
             │         │
             └─────────┘
                  │
                  ▼
             Blue Hardening
```

The uploaded blueprint specifically proposes extracting false negatives, mutating evasive features and retraining from replay batches. 

### Required experiment

We will demonstrate:

```text
Round 0
   ↓
Attack success rate
   ↓
Hardening
   ↓
Round 1
   ↓
Attack success rate
   ↓
Hardening
   ↓
Round 2
```

and report whether the system actually improves.

---

# 2.17 Agentic Commerce

## STATUS: **HIGH-PRIORITY ATTACK FAMILY**

This is where the uploaded blueprint adds significant strategic value.

Mastercard's 2026 direction explicitly includes agentic commerce, agent authorization and authenticated machine-driven transactions.

Therefore we should investigate fraud where:

```text
Human
 ↓
Authorized AI Agent
 ↓
Payment
```

is transformed into:

```text
Human
 ↓
Authorized AI Agent
 ↓
Manipulated / compromised agent
 ↓
Fraudulent behavior
```

This is more relevant to Mastercard's current direction than simply building another deepfake classifier.

---

# 2.18 Agentic MVP — FROZEN DEMONSTRATION SCOPE

We will **not** attempt to build every possible agentic fraud attack.

Our primary demonstration can be:

```text
Legitimate AI shopping/procurement agent
        ↓
Authorized mandate
        ↓
Agent compromise / intent drift
        ↓
Many coordinated micro-transactions
        ↓
Multiple synthetic merchants
        ↓
Defense detects cross-entity behavior
        ↓
Attack adapts
        ↓
Defense hardens
```

The uploaded blueprint gives a bounded example involving authorized micro-payments followed by split transactions across synthetic merchants. 

### Why one scenario?

Because:

> **one deeply implemented, measurable scenario is better than five superficial demos.**

---

# 2.19 Agentic Attack Taxonomy

Our current candidate taxonomy:

```text
GENAI / AGENTIC PAYMENT FRAUD
│
├── Identity
│   ├── Synthetic identity
│   └── Identity/KYC manipulation
│
├── Social / APP
│   ├── AI-assisted social engineering
│   ├── conversational manipulation
│   └── dynamic payment manipulation
│
├── Transaction
│   ├── velocity abuse
│   ├── probing
│   ├── behavioral mimicry
│   └── micro-transaction dispersion
│
└── Coordinated / Agentic
    ├── Agent authorization abuse
    ├── Intent drift
    ├── Multi-agent coordination
    ├── Machine-speed fraud
    └── Distributed evasion
```

The uploaded blueprint similarly organizes the threat space into identity, social/APP, transaction and coordinated/agentic layers. 

### Terminology correction

We will **not** call something “Verifiable Intent Hijacking” as though it were an established industry attack category.

Instead:

> **Agent Authorization / Intent Abuse**

until our research establishes more precise terminology.

---

# 2.20 Adaptive Attack Engine

## STATUS: **TARGET, IMPLEMENTATION OPEN**

The attack engine should conceptually optimize:

```text
Attack effectiveness
+
realism
+
novelty
```

A possible conceptual reward is:

[
R =
(1-D_\phi(x))
+
\lambda \cdot Novelty(x)
]

as proposed in the uploaded blueprint. 

But we are **not yet committing to reinforcement learning**.

Possible implementation:

```text
Rule-based search
Evolutionary search
Bayesian optimization
RL
LLM-assisted planning
Hybrid
```

Step 4 will determine what is actually feasible.

---

# 2.21 Synthetic Generation Model

## STATUS: **CANDIDATE, NOT LOCKED**

Candidate technologies:

```text
Rule-based simulation
Probabilistic simulation
GAN
CTGAN
Diffusion
TabDDPM-style generation
Hybrid
```

### TabDDPM-Aug

The attached blueprint proposes TabDDPM-Aug with DCR filtering. 

We retain it as a candidate because recent research makes it interesting.

But:

> **We will not build diffusion merely because it sounds advanced.**

First determine whether simpler generation is insufficient.

---

# 2.22 Privacy

## STATUS: **FROZEN PRINCIPLE**

Synthetic data must not accidentally reproduce sensitive records.

We can use:

### DCR / nearest-record screening

to identify suspiciously similar generated records.

But we correct the blueprint's wording:

> DCR does **not** “guarantee zero memorization.”

It is a **memorization-risk / near-duplicate screening mechanism**.

Formal differential privacy is a separate mechanism.

---

# 2.23 Differential Privacy

## STATUS: **OPTIONAL CANDIDATE**

Formal:

[
(\epsilon,\delta)\text{-DP}
]

is potentially valuable.

But we will only claim DP if we actually implement:

* a valid DP mechanism
* privacy accounting
* appropriate epsilon/delta reporting.

Otherwise:

> **No DP marketing claim.**

---

# 2.24 Payment Protocol Representation

## STATUS: **REPRESENTATION LAYER**

The uploaded blueprint proposes:

* ISO 20022
* `pain.001`
* `pacs.008`
* EMV 3DS 2.3.



This is useful for making the prototype feel like a payment-security system rather than a Kaggle notebook.

But it should sit **around** the ML system, not replace it.

```text
ML / Risk Engine
       ↓
Decision
       ↓
Protocol Adapter
 ├── ISO 20022 representation
 └── EMV 3DS-style step-up
```

We are not building a complete payment-processing network.

---

# 2.25 Decision Policy

## STATUS: **FROZEN CONCEPT**

The system should produce:

```text
LOW RISK
   ↓
ALLOW

MEDIUM RISK
   ↓
STEP-UP / VERIFY

HIGH RISK
   ↓
BLOCK
```

This is superior to merely outputting:

```text
0 / 1
```

The uploaded blueprint calls this a tri-action policy. 

### Thresholds are NOT frozen.

We will **not** use the blueprint's `0.15 / 0.80` values until calibrated against the actual data.

---

# 2.26 Cost-Sensitive Decisioning

## STATUS: **FROZEN CONCEPT, PARAMETERS OPEN**

We should model:

```text
False negative cost
False positive/block cost
Step-up cost
Customer friction
Transaction amount
```

rather than optimize only:

```text
accuracy
```

The exact dollar costs in the uploaded blueprint are **not being treated as official Mastercard parameters**.

Instead:

```text
C_FN
C_STEPUP
C_FP
C_FRICTION
```

remain configurable.

---

# 2.27 Explainability

## STATUS: **FROZEN**

For important decisions:

```text
HIGH RISK
─────────
Reason 1: abnormal velocity
Reason 2: new device
Reason 3: unusual merchant pattern
Reason 4: relational inconsistency
```

TreeSHAP is a candidate implementation.

The uploaded blueprint proposes packaging top risk drivers into an actionable payment-security payload. 

We will validate whether this is useful after the baseline.

---

# 2.28 Empirical Ablation

## **STATUS: ABSOLUTELY FROZEN**

Every sophisticated component must prove incremental value.

Example:

```text
Model A
GBDT

Model B
GBDT + behavioral

Model C
GBDT + behavioral + temporal

Model D
GBDT + behavioral + temporal + relational

Model E
full system
```

Then compare:

* PR-AUC
* ROC-AUC
* F1
* precision
* recall
* false-positive rate
* calibration
* latency.

If:

```text
GNN adds +0.1%
```

but introduces:

```text
huge complexity
+
latency
+
deployment problems
```

we may remove it.

That is exactly how we avoid architecture bloat.

---

# 2.29 Validation Integrity

## STATUS: **FROZEN**

Our validation framework must investigate:

### Out-of-Time split

```text
Past → Train
Later → Validation
Latest → Test
```

### Adversarial validation

Train a classifier:

```text
train row = 0
test row = 1
```

Then examine:

[
AUC_{adv}
]

### Interpretation

```text
≈ 0.50
↓
little detectable shift

high AUC
↓
distribution shift exists
↓
investigate
```

**0.50 is not a mandatory target.**

---

# 2.30 Latency

## STATUS: **FROZEN**

We will measure:

```text
Feature generation
+
model inference
+
decision
+
explanation
=
end-to-end latency
```

The uploaded blueprint proposes a fast-path target below 45 ms. 

We will treat:

> **<45 ms**

as an engineering target for the fast path, **not a claim that the competition mandates exactly 45 ms**.

Actual measured latency will be reported.

---

# 2.31 Dual-Rail Architecture

This is another useful concept from the blueprint.

## Fast path

Used for immediate payment decisions:

```text
Current transaction
+
precomputed behavioral features
+
fast model
        ↓
decision
```

## Async intelligence path

More expensive analysis:

```text
graph construction
+
graph embeddings
+
deep relational analysis
        ↓
feature cache
```

Then:

```text
FAST PATH
    +
ASYNC INTELLIGENCE
        ↓
risk engine
```

The uploaded architecture explicitly separates fast and asynchronous intelligence paths. 

### This is now a strong architectural candidate.

But again:

> actual GNN implementation remains experimental.

---

# 2.32 Competitive Gap

After researching existing systems, our differentiation hypothesis is:

| Existing approach               | Already mature? | Our response                      |
| ------------------------------- | --------------: | --------------------------------- |
| GBDT fraud classification       |         **Yes** | Use as baseline                   |
| Entity/behavioral features      |         **Yes** | Use them                          |
| GNN fraud detection             |         **Yes** | Don't claim as novelty            |
| Synthetic transactions          |         **Yes** | Build only as required            |
| Fraud scenario simulation       |         **Yes** | Extend toward adaptive attacks    |
| Temporal fraud detection        |         **Yes** | Use where valuable                |
| Agentic payments                |    **Emerging** | High-priority attack surface      |
| Adaptive adversarial attacks    |     Less mature | **Primary innovation hypothesis** |
| Defense-aware attack generation |     Less mature | **Primary innovation hypothesis** |
| Closed-loop red/blue hardening  |     Less mature | **Primary innovation hypothesis** |

---

# 2.33 What we explicitly will NOT claim

We will not claim:

### ❌ “We invented GNN fraud detection.”

False.

### ❌ “Synthetic fraud generation is novel.”

False.

### ❌ “TabDDPM is automatically superior.”

Unproven for our dataset.

### ❌ “HOT-GNN beats every fraud model.”

Unproven for our task.

### ❌ “DCR guarantees zero memorization.”

Too strong.

### ❌ “Our 15%/80% thresholds are optimal.”

Unvalidated.

### ❌ “Our system is sub-45 ms.”

Until measured.

### ❌ “We use AI, therefore it's innovative.”

Meaningless.

---

# 2.34 What we ARE claiming

Our working innovation claim is:

> **An adaptive adversarial payment-security laboratory where realistic and coordinated attacks—including a bounded agentic-commerce scenario—are generated against a multi-signal defense, evaluated for both realism and evasion, and fed back into a replay-driven hardening loop.**

That is a claim we can actually demonstrate.

---

# 2.35 Master Step-2 Architecture

```text
                         ┌─────────────────────────────┐
                         │          IDENTIFY           │
                         │                             │
                         │ Threat intelligence         │
                         │ GenAI fraud taxonomy        │
                         │ Agentic-commerce threats    │
                         │ Attack hypotheses            │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │          RED TEAM           │
                         │                             │
                         │ Attack library              │
                         │ Scenario engine             │
                         │ Mutability masks            │
                         │ Adaptive attack engine      │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │   SYNTHETIC PAYMENT WORLD   │
                         │                             │
                         │ Accounts                    │
                         │ Transactions                │
                         │ Merchants                   │
                         │ Devices                     │
                         │ Network entities            │
                         │ Temporal state              │
                         │ AI agents                   │
                         └──────────────┬──────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              │                         │                         │
              ▼                         ▼                         ▼
       ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
       │   TABULAR    │        │  BEHAVIORAL  │        │ RELATIONAL / │
       │   DEFENSE    │        │   TEMPORAL   │        │    GRAPH     │
       │              │        │              │        │              │
       │ LGBM         │        │ Velocity     │        │ Relations    │
       │ XGB          │        │ Sequences    │        │ Graph feats  │
       │ CatBoost     │        │ Recency      │        │ GNN candidates│
       └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      ▼
                         ┌─────────────────────────────┐
                         │       RISK ENGINE            │
                         │                             │
                         │ Probability                 │
                         │ Calibration                 │
                         │ Explainability              │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────┼──────────────┐
                         ▼              ▼              ▼
                       ALLOW         STEP-UP           BLOCK
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │          OUTCOME            │
                         │                             │
                         │ True positive               │
                         │ False positive              │
                         │ True negative               │
                         │ False negative              │
                         │ Attack success rate         │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │      REPLAY / FEEDBACK      │
                         │                             │
                         │ False negatives             │
                         │ Hard examples               │
                         │ Evasive permutations       │
                         │ Attack analysis              │
                         └──────────────┬──────────────┘
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                       RED ADAPTATION       BLUE HARDENING
                              │                   │
                              └─────────┬─────────┘
                                        ▼
                                  NEXT ATTACK
```

---

# 2.36 Step-2 Locked Requirements

| ID  | Requirement                           | Status                             |
| --- | ------------------------------------- | ---------------------------------- |
| C1  | Strong GBDT baseline                  | **LOCKED**                         |
| C2  | Entity/behavioral intelligence        | **LOCKED**                         |
| C3  | Temporal intelligence                 | **LOCKED**                         |
| C4  | Relational intelligence investigation | **LOCKED**                         |
| C5  | Class-imbalance handling              | **LOCKED**                         |
| C6  | Attack simulation                     | **LOCKED**                         |
| C7  | Attack mutability constraints         | **LOCKED**                         |
| C8  | Attack fidelity measurement           | **LOCKED**                         |
| C9  | Attack Success Rate                   | **LOCKED**                         |
| C10 | Closed-loop feedback                  | **LOCKED**                         |
| C11 | Replay buffer / hard-example mining   | **LOCKED**                         |
| C12 | Empirical ablation                    | **LOCKED**                         |
| C13 | OOT validation                        | **LOCKED**                         |
| C14 | Adversarial validation                | **LOCKED**                         |
| C15 | Agentic-commerce attack MVP           | **LOCKED**                         |
| C16 | Tri-action decisioning                | **LOCKED**                         |
| C17 | Explainability                        | **LOCKED**                         |
| C18 | Latency measurement                   | **LOCKED**                         |
| C19 | Synthetic-data privacy screening      | **LOCKED**                         |
| C20 | ISO/EMV representation layer          | **CANDIDATE / presentation layer** |
| C21 | HOT-GNN                               | **CANDIDATE**                      |
| C22 | DynBERG                               | **CANDIDATE**                      |
| C23 | CARE-GNN                              | **CANDIDATE**                      |
| C24 | PC-GNN                                | **CANDIDATE**                      |
| C25 | TabDDPM-Aug                           | **CANDIDATE**                      |
| C26 | Differential privacy                  | **CANDIDATE**                      |
| C27 | RL attacker                           | **CANDIDATE**                      |
| C28 | LLM attacker                          | **CANDIDATE**                      |
| C29 | Fixed risk thresholds                 | **NOT LOCKED**                     |
| C30 | Fixed monetary cost values            | **NOT LOCKED**                     |

---

# 2.37 Step-2 Decision Gate

Before moving to Step 3, the project now has a clear rule:

> **No candidate technology enters the final architecture simply because it is sophisticated or appears in a research paper.**

It must survive:

```text
Candidate
   ↓
Implementation
   ↓
Experiment
   ↓
Ablation
   ↓
Measured benefit
   ↓
Complexity/latency assessment
   ↓
KEEP or REMOVE
```

This is particularly important with **HOT-GNN, DynBERG, TabDDPM-Aug, RL and LLM components**.

---

# STEP 2 — FINAL STATUS

## **FINALIZED AND FROZEN**

The key strategic conclusion is:

> **We are not building another fraud classifier.**

We are building a **competition-grade fraud defense inside an adversarial payment-security laboratory**.

The Blue Team starts with the strongest practical foundation:

**GBDT + behavioral + temporal + entity intelligence**

and adds graph/deep models only if experiments prove they help.

The Red Team starts with reliable scenario simulation and adds:

**mutability constraints + realistic coordinated attacks + adaptive evasion**

with **agentic-commerce abuse as the flagship demonstration**.

Then the two sides interact:

> **Attack → Detect → Measure → Adapt → Harden → Attack again.**

That is now the **final Step-2 foundation**.

---

## Next: STEP 3

We can now move to **Step 3 — Kaggle Data Forensics & Winning Baseline**.

And Step 3 will be much more concrete than Steps 1–2:

**actual competition files → schema → target → metric → distributions → missing values → IDs → timestamps → entity structure → leakage → train/test shift → validation design → baseline experiments.**

Most importantly, **we will not decide the final ML architecture until the actual Kaggle data tells us what signal exists.**

# Step 3
# STEP 3 — FINALIZED: DATA & SIMULATION WORLD DESIGN

**Version 3.0 — Finalized and locked**

I have incorporated the specification you provided into the previous Step 3, but I have **not blindly copied its claims**. I cross-checked the important named components against available sources and corrected places where the specification was stronger than the evidence supports.

That distinction matters. We are building a competition submission, so we should not put an impressive-sounding research claim into the architecture unless we can defend it to a judge.

The central correction from our previous discussion remains:

> **Mastercard does not provide us with a conventional Kaggle train/test dataset. We therefore build the controlled payment world ourselves, calibrate it against credible public/reference data, generate legitimate and fraudulent behavior, and evaluate the Blue Team against both known and unseen attacks.**

The finalized Step 3 is therefore **Data & Simulation World Design**, not Kaggle tabular-data forensics.

---

# 3.1 The purpose of Step 3

Step 2 established **what we should build and where our differentiation should come from**.

Step 3 now defines:

> **What payment world will exist inside our system, how legitimate behavior is generated, how attacks are injected, how realism is measured, and how we create trustworthy ground truth for evaluating the defense.**

Our complete Step-3 pipeline is:

```text
                 PUBLIC REFERENCE DATA
                         │
                         ▼
              EMPIRICAL CALIBRATION
                         │
                         ▼
             ┌─────────────────────┐
             │  PAYMENT WORLD      │
             │                     │
             │ Customers           │
             │ Accounts            │
             │ Merchants           │
             │ Devices             │
             │ IP / Locations      │
             │ Transactions        │
             │ Tokens / Sessions   │
             └──────────┬──────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
      LEGITIMATE WORLD       RED TEAM WORLD
              │                   │
              │             Attack scenarios
              │             Mutability masks
              │             Attack mutations
              │             Agentic attacks
              │                   │
              └─────────┬─────────┘
                        ▼
                 SYNTHETIC WORLD
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
        TRAIN        VALIDATION    ZERO-DAY TEST
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                  BLUE TEAM
                        │
                        ▼
                OUTCOME ANALYSIS
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
             FP         FN       ASR
                        │
                        ▼
                 REPLAY BUFFER
                        │
                ┌───────┴───────┐
                ▼               ▼
          RED ADAPTATION   BLUE HARDENING
                │               │
                └───────┬───────┘
                        ▼
                   NEXT ROUND
```

This is now part of the permanent master project architecture.

---

# 3.2 First principle: we build the world before the detector

We are **not** going to generate:

```text
10,00,000 random rows
        ↓
fraud = 1 for some rows
        ↓
train XGBoost
```

That would produce an artificial benchmark rather than a credible fraud-security laboratory.

Instead:

> **Legitimate behavior is generated first. Fraud is an intervention into that world.**

That gives us causal structure.

---

# 3.3 Empirical Reference Calibration

The uploaded specification proposes four reference sources:

1. 1M Synthetic Bank Transactions
2. MoMTSim
3. NeurIPS Bank Account Fraud / Feedzai
4. IEEE-CIS Fraud Detection



This is directionally correct, but there is an important correction.

## We must distinguish three things

### A. Public benchmark/reference data

Used to estimate distributions and relationships.

### B. Our simulator

Creates the actual competition environment.

### C. Mastercard data

We **do not have this**.

Therefore we will never write:

> "Our simulator reproduces Mastercard's proprietary transaction distribution."

Instead:

> **"Our simulator is calibrated against multiple public fraud/payment references to approximate realistic transaction, behavioral, temporal and relational characteristics."**

That is defensible.

---

# 3.4 Reference datasets

## MoMTSim — KEEP

This is a particularly useful reference because it is specifically designed around synthetic mobile-money transactions and fraud scenarios.

The 2025 data article reports datasets containing transaction timestamps, amounts, balances, participant IDs, transaction types and fraud labels. ([ScienceDirect][1])

It also reports millions of simulated transactions and explicitly compares synthetic distributions with real transaction characteristics. ([PubMed Central (PMC)][2])

The project is publicly available as an open-source simulator. ([GitHub][3])

### Our use

MoMTSim becomes a **reference for stateful transaction behavior and fraud-scenario design**, not a drop-in replacement for our simulator.

---

# 3.5 1M Synthetic Bank Transactions — KEEP, BUT DOWNGRADE THE CLAIM

The specification calls this:

> "1M Synthetic Bank Transactions (May 2026)"

and uses it as a premier reference. 

The available dataset does contain 1 million synthetic banking transactions and is explicitly intended for fraud detection/analytics. ([Kaggle][4])

However:

> **It is synthetic educational data, not real Mastercard/bank transaction data.**

So we use it as a **secondary calibration reference**, not as evidence of real-world banking distributions.

---

# 3.6 IEEE-CIS — KEEP

IEEE-CIS remains useful for:

* transaction metadata
* identity-related features
* card/device relationships
* categorical structures
* fraud modeling.

But again:

> It is a public competition dataset, not Mastercard's proprietary transaction population.

We use it to identify useful feature relationships and realistic fraud-detection structures.

---

# 3.7 BAF / Feedzai — KEEP

The Bank Account Fraud dataset provides another independent reference for account/application-level fraud behavior.

Its purpose in our architecture is different from IEEE-CIS:

```text
IEEE-CIS
   ↓
transaction / identity structure

BAF
   ↓
account/application fraud structure
```

This diversity is useful because our simulator shouldn't inherit the quirks of one dataset.

---

# 3.8 Calibration architecture

We therefore create:

```text
             PUBLIC REFERENCES
                    │
      ┌─────────────┼──────────────┐
      ▼             ▼              ▼
  Transaction    Behavioral     Relational
  statistics     statistics     statistics
      │             │              │
      └─────────────┼──────────────┘
                    ▼
             CALIBRATION LAYER
                    │
                    ▼
             PAYMENT WORLD
```

The goal is **not to copy rows**.

The goal is to estimate:

* amount behavior
* transaction cadence
* temporal patterns
* merchant affinities
* customer behavior
* entity relationships
* fraud prevalence/ranges
* tail behavior.

---

# 3.9 Dependency modeling

The uploaded specification proposes:

> empirical Gaussian-mixture marginals + multivariate t-copula dependency structure with (\nu=4). 

This is retained as a **candidate calibration mechanism**, not an unquestionable requirement.

Conceptually:

```text
amount
   ↕
velocity
   ↕
merchant behavior
   ↕
time
   ↕
risk/history
```

should not be generated independently.

A transaction with a high amount may correlate with:

* customer type
* merchant category
* time
* account history
* geography.

A dependency model helps preserve these relationships.

### Important correction

We will **test whether (t)-copula with (\nu=4)** fits our reference data.

We do not claim beforehand that:

> (\nu=4) is universally correct for financial transactions.

If empirical fitting says another parameter/model is better, we use it.

---

# 3.10 Final decision on the calibration model

### Required

**Empirical calibration**

### Candidate

**GMM marginals**

### Candidate

**t-copula**

### Not frozen

**(\nu=4)**

The data decides the parameter.

---

# 3.11 Dual-engine synthetic transaction pipeline

This is now **LOCKED**.

We have two streams:

```text
                    PAYMENT WORLD
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
        STREAM A                  STREAM B
     BENIGN ENGINE             ATTACK ENGINE
             │                       │
             │                 Tabular generation
             │                 + attack scenarios
             │                 + mutations
             │                 + constraints
             │                       │
             └───────────┬───────────┘
                         ▼
                   PAYMENT EVENTS
```

The uploaded specification defines Stream A as a stateful benign engine and Stream B as a TabDDPM-Aug-based attack engine. 

We retain the **dual-engine concept**, but one technology decision remains conditional.

---

# 3.12 Stream A — Stateful benign engine

## **LOCKED**

The benign engine must maintain state.

We don't generate each transaction independently.

For customer (i):

[
S_t =
{
Balance_t,
Credit_t,
Velocity_t,
KnownDevices_t,
ActiveTokens_t,
History_t
}
]

The next transaction depends partly on that state.

The uploaded specification explicitly proposes a stateful dynamic ledger and token state. 

---

# 3.13 Why statefulness matters

Without state:

```text
Transaction 1
Transaction 2
Transaction 3
```

are independent.

With state:

```text
Transaction 1
       ↓
balance changes
       ↓
device becomes known
       ↓
merchant becomes familiar
       ↓
velocity changes
       ↓
Transaction 2
```

Now fraud can actually manipulate **a behavioral sequence**.

---

# 3.14 Customer archetypes

The specification defines eight archetypes:

* Salaried Professional
* Student / Gig Worker
* High-Net-Worth / VIP
* Autonomous AI Commerce User
* B2B Bulk Payee
* Digital Nomad
* Subscription-Heavy Consumer
* Cross-Border Remitter



### **LOCKED**

These are sufficient for the first world version.

We should not immediately create 50 archetypes.

Eight gives enough behavioral diversity while remaining manageable.

---

# 3.15 Merchant taxonomy

The specification mentions 10 MCC/merchant categories. 

### **LOCKED CONCEPT**

We will use **10 merchant-category groups initially**.

The exact categories will be selected from actual MCC/payment references rather than inventing arbitrary categories.

---

# 3.16 Important correction: 8 archetypes ≠ 10 archetypes

The uploaded text says:

> `N = 10,000`

customers and then specifies eight archetypes. 

There is no contradiction if interpreted as:

```text
10,000 customers
       ↓
distributed across
       ↓
8 archetypes
```

So we lock:

> **10,000 initial simulated customers distributed across 8 archetypes.**

The number 10,000 itself remains an **MVP-scale choice**, not a requirement that the final simulator cannot scale beyond it.

---

# 3.17 Stateful ledger

The ledger will track:

```text
Balance
Available credit
Failed authentication count
Active tokens
Known devices
Recent transaction history
```

The specification explicitly defines this state vector. 

We also add:

```text
Known merchants
Known locations
Recent session
Velocity state
Risk history
```

because these become important to detection.

---

# 3.18 Physical validity

The simulator must prevent impossible financial states.

For example:

```text
balance = ₹1,000
transaction = ₹100,000
```

should not silently succeed unless the simulated payment mechanism legitimately permits it.

The uploaded specification explicitly includes balance and credit-ceiling checks. 

### **LOCKED**

---

# 3.19 Token lifecycle

The proposed token state machine:

```text
ACTIVE
   ↓
SUSPENDED
   ↓
REVOKED
```

with assurance levels is retained as a **payment-protocol simulation layer**.

However:

> We should not imply that our simulator is implementing the full EMVCo ecosystem.

We are modeling the **relevant state transitions** needed for the fraud scenarios.

---

# 3.20 Stream B — Attack engine

The attack engine is the heart of the Red Team.

It must support:

```text
Known attacks
+
Mutated attacks
+
Coordinated attacks
+
Agentic attacks
+
Adaptive attacks
```

---

# 3.21 TabDDPM-Aug — conditional component

The uploaded specification makes TabDDPM-Aug mandatory. 

I am **not freezing that claim as proven**.

Our architecture is:

```text
ATTACK GENERATOR
       │
       ├── Rule/scenario engine
       ├── Probabilistic generator
       └── Tabular diffusion candidate
```

If TabDDPM-Aug is reproducible and improves attack fidelity, it becomes the primary tabular generator.

If not, the system still works.

### Why?

Because:

> **The competition requires realistic attack generation, not a specific diffusion architecture.**

---

# 3.22 Density-Adaptive Sampling

The uploaded specification proposes DBHA/Density-Adaptive Sampling. 

We retain the **idea**:

```text
Dense region
   ↓
preserve multimodal structure

Sparse/tail region
   ↓
carefully augment
```

But again:

> The exact DBHA implementation must be validated experimentally.

---

# 3.23 Mutability mask

## **FROZEN**

This is one of the most important pieces of Step 3.

For every field:

[
m_i \in {0,1}
]

where:

```text
m = 1 → attacker can modify
m = 0 → historical state remains fixed
```

The specification explicitly defines this approach. 

Example:

| Feature                        |    Mutable? |
| ------------------------------ | ----------: |
| Current amount                 |         Yes |
| Current timestamp              |         Yes |
| Current merchant interaction   | Conditional |
| Current session/device context | Conditional |
| Historical account age         |          No |
| Historical spending history    |          No |
| Established identity state     |          No |

This prevents the generator from cheating.

---

# 3.24 DCR privacy screening

The specification proposes:

[
DCR(x)=
\min_{x_i\in D_{train}}
d_{Gower}(x,x_i)
]

and rejects samples below a threshold. 

## **LOCKED CONCEPT**

We will implement near-duplicate screening.

### But important correction:

The statement:

> "This guarantees a 48% reduction in privacy leakage risk"

should **NOT** be carried into our final submission unless we reproduce that exact experiment under comparable conditions.

Likewise:

> DCR does not guarantee zero memorization.

It is a **screening mechanism**.

---

# 3.25 Hard-negative library

This is now **FROZEN**.

The specification proposes four legitimate anomaly scenarios:

### HN-1 — International traveler

```text
new country
+
large hotel transaction
+
historically consistent travel behavior
```

### HN-2 — Flash sale

```text
massive legitimate velocity spike
+
known merchant
+
known promotion window
```

### HN-3 — Shared household device

```text
one device
+
multiple legitimate family accounts
+
consistent household attributes
```

### HN-4 — B2B month-end reconciliation

```text
large transaction
+
predictable recurring business cycle
```

The uploaded taxonomy specifies these examples. 

---

# 3.26 Why hard negatives are mandatory

Otherwise our model learns:

```text
new device → fraud
high amount → fraud
high velocity → fraud
international → fraud
```

That's unacceptable.

We need:

```text
                    HIGH AMOUNT
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
       legitimate                fraud
       B2B payment               theft
       travel                    mule
       flash sale                ATO
```

This forces the model to learn **context**, not shortcuts.

---

# 3.27 Agentic Fraud — Primary Demonstration

This remains our flagship differentiator.

Mastercard's current Verifiable Intent material describes a framework that links consumer identity, original instructions and transaction outcome through a cryptographic/tamper-resistant record. ([Mastercard][5])

That makes agentic fraud a particularly relevant research direction for this challenge.

We therefore retain the three proposed scenarios.

---

# 3.28 Scenario 1 — Intent/Mandate Drift

### Legitimate state

```text
AI agent
   ↓
authorized mandate
   ↓
office supplies
   ↓
≤ defined budget
```

### Attack

```text
agent compromise
       ↓
instruction/intent drift
       ↓
new merchant/category
       ↓
higher-value purchase
```

The uploaded specification uses the example of office supplies drifting toward gift-card purchases. 

### Detection signal

Not:

```text
device changed
```

because it may not.

Instead:

```text
authorized intent
        vs
actual transaction behavior
```

This is much more interesting.

---

# 3.29 Scenario 2 — Multi-Agent Coordinated Smurfing

The proposed scenario:

```text
15 agents
     ↓
75 transactions
     ↓
$15,000 total
     ↓
~$195 each
     ↓
8 minutes
```

is retained as a **demonstration configuration**, not as a universal attack parameter. 

The attacker deliberately stays below individual velocity thresholds.

Therefore:

```text
Transaction-level detector
       ↓
may miss

Network-level detector
       ↓
should detect
```

This directly justifies our relational intelligence layer.

---

# 3.30 Scenario 3 — Agentic Token Replay

The proposed scenario involves:

```text
valid authorization
        ↓
interception
        ↓
destination modification
        ↓
replay
```



### Important implementation boundary

We will **simulate the authorization/token state**.

We will not claim to have implemented or attacked real Mastercard cryptographic infrastructure.

The prototype is a security simulation.

---

# 3.31 Agentic attack matrix

Our final Step-3 flagship attack matrix is:

| Attack               | Primary weakness               | Required intelligence         |
| -------------------- | ------------------------------ | ----------------------------- |
| Intent drift         | Intent ≠ transaction           | behavioral + semantic/context |
| Multi-agent smurfing | Distributed coordination       | graph + temporal              |
| Token replay         | Authorization/context mismatch | protocol + relational         |

This is much stronger than simply saying:

> "We support agentic fraud."

---

# 3.32 HOT-GNN

The specification proposes HOT-GNN as the asynchronous relational engine. 

This research direction is credible: the 2026 HOT-GNN paper specifically addresses heterophily, outliers, temporal information and camouflaged fraud in heterogeneous multi-relational graphs. ([ScienceDirect][6])

### Architecture role

```text
Payment graph
     ↓
HOT-GNN
     ↓
graph anomaly features
     ↓
feature cache
     ↓
real-time Blue Team
```

### Important:

We are **not putting HOT-GNN in the synchronous payment path**.

---

# 3.33 DynBERG

DynBERG is also a legitimate research candidate.

Its 2025 paper combines Graph-BERT and GRU to model dynamic directed financial transaction networks. ([arXiv][7])

Therefore:

```text
HOT-GNN
   ↓
relational / heterophily intelligence

DynBERG
   ↓
dynamic temporal graph intelligence
```

This separation is architecturally sensible.

---

# 3.34 Asynchronous graph cache

This is now **LOCKED as an architecture pattern**.

```text
                TRANSACTION STREAM
                        │
                        ▼
                 FAST BLUE TEAM
                        │
                        │
        ┌───────────────┘
        │
        │
        ▼
   ASYNC GRAPH ENGINE
        │
   ┌────┴────┐
   ▼         ▼
HOT-GNN   DynBERG
   │         │
   └────┬────┘
        ▼
   FEATURE CACHE
        │
        ▼
 FAST MODEL READS
 PRECOMPUTED SIGNALS
```

The specification proposes graph features being written into an in-memory cache and read by the real-time model. 

### But:

We will **measure** whether the claimed `<2 ms` cache-read/inference contribution is actually achieved.

It is not a pre-declared performance result.

---

# 3.35 Zero-Day evaluation

This is one of the most important upgrades in the final Step 3.

We need two different evaluation worlds.

## World A — Known fraud

```text
Train
ATO
Velocity
Device farm
Mule

Test
same families
new instances
```

This measures normal detection.

---

## World B — Zero-day

```text
Train
ATO
Velocity
Device farm
Mule

Test
Intent drift
Multi-agent smurfing
Token replay
```

This measures:

> **Can our model detect behavior it was not explicitly trained on?**

---

# 3.36 Temporal split

The uploaded specification proposes:

```text
Months 1–4 → Train
Months 5–6 → Validation
```



### **LOCKED CONCEPT**

But those exact months only make sense if our simulated world is configured for six months.

Therefore:

> **The temporal split principle is frozen; the exact time horizon is configurable.**

---

# 3.37 Zero-Day Transfer Matrix

We now explicitly create:

```text
                  TEST ATTACK
                 ┌────┬────┬────┐
                 │ A  │ B  │ C  │
TRAIN ATTACK     ├────┼────┼────┤
A                │ ✓  │ ?  │ ?  │
B                │ ?  │ ✓  │ ?  │
C                │ ?  │ ?  │ ✓  │
D                │ ?  │ ?  │ ?  │
                 └────┴────┴────┘
```

The important cells are:

> **Train on one family, test on structurally different families.**

---

# 3.38 Gamma OOD

The uploaded specification defines:

[
\Gamma_{OOD}
============

\frac{
PR\text{-}AUC_{zero-day}
}{
PR\text{-}AUC_{known}
}
]



We retain this metric.

### But we correct one thing:

The proposed:

[
\Gamma_{OOD}\geq0.75
]

is a **project benchmark/target**, not a proven industry-standard threshold.

So:

### Target

[
\Gamma_{OOD}\geq0.75
]

### Interpretation

A high value means the model retains substantial detection capability against novel attack families.

---

# 3.39 Additional evaluation metrics

We will not rely on Gamma alone.

The evaluation dashboard should contain:

### Detection

* PR-AUC
* ROC-AUC
* precision
* recall
* F1

### False-positive control

* FPR
* FPR at selected operating points
* legitimate transaction approval rate

### Novelty

* (\Gamma_{OOD})
* unseen-family recall

### Attack

* Attack Success Rate

### Simulation

* distribution distance
* correlation preservation
* temporal similarity
* graph-structure similarity

### Operational

* latency
* throughput
* memory.

---

# 3.40 Attack Success Rate

This is now **FROZEN**.

[
ASR =
\frac{\text{successful evasions}}
{\text{attack attempts}}
]

For example:

```text
Round 0
ASR = 31%

      ↓ hardening

Round 1
ASR = 22%

      ↓ hardening

Round 2
ASR = 14%
```

That provides direct evidence that the closed loop is doing something.

---

# 3.41 The crucial separation: fidelity vs effectiveness

We permanently separate:

```text
                    ATTACK
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          FIDELITY           EFFECTIVENESS
             │                   │
        Is it realistic?      Does it evade?
             │                   │
             ▼                   ▼
       Distribution          Attack Success
       Structure             Detection rate
       Temporal behavior
```

A synthetic attack can be:

### Realistic but ineffective

Useful for validation.

### Effective but unrealistic

Not acceptable as a production-style attack.

### Realistic and effective

**High-value adversarial example.**

---

# 3.42 Preventing simulator shortcut learning

This is now a **hard requirement**.

We will deliberately introduce:

### Legitimate anomalies

as described above.

### Fraud camouflage

Some fraud should look normal.

### Fraud diversity

Not every fraud uses:

* new device
* huge amount
* high velocity.

### Attack variation

Different attacks must alter different signals.

Otherwise:

```text
generator rule
     ↓
detector learns generator rule
     ↓
fake 99% performance
```

We will explicitly test for this.

---

# 3.43 Ground-truth metadata

Because we control the simulation, every event can carry hidden evaluation metadata.

Example:

```text
transaction_id
customer_id
merchant_id
device_id
timestamp

fraud_label
attack_family
attack_instance_id
attack_stage
attack_parameters
agent_id
mutation_id
```

### Important:

Only the appropriate fields are exposed to the Blue Team.

The hidden attack metadata is reserved for evaluation.

That prevents label leakage.

---

# 3.44 Dataset architecture

The simulator will conceptually generate:

```text
customers
accounts
merchants
devices
ips
locations
agents
tokens
sessions
transactions
attack_events
```

with relationships:

```text
Customer
   ↓
Account
   ↓
Device
   ↓
IP
   ↓
Session
   ↓
Transaction
   ↓
Merchant
```

and:

```text
AI Agent
   ↓
Mandate
   ↓
Token
   ↓
Transaction
```

for agentic commerce.

---

# 3.45 The final synthetic-world architecture

```text
                         REFERENCE DATA
                              │
                              ▼
                    ┌──────────────────┐
                    │ CALIBRATION      │
                    │                  │
                    │ Marginals        │
                    │ Correlations     │
                    │ Temporal stats   │
                    │ Entity stats     │
                    └────────┬─────────┘
                             │
                             ▼
                 ┌─────────────────────────┐
                 │ STATEFUL PAYMENT WORLD  │
                 │                         │
                 │ 10,000 initial users    │
                 │ 8 customer archetypes   │
                 │ 10 merchant categories  │
                 │ devices / IPs / tokens  │
                 │ ledger / sessions       │
                 └────────────┬────────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
       ┌──────────────────┐      ┌──────────────────┐
       │ BENIGN ENGINE    │      │ RED TEAM ENGINE  │
       │                  │      │                  │
       │ normal behavior  │      │ attack library   │
       │ anomalies        │      │ mutations        │
       │ state changes    │      │ agentic attacks  │
       └────────┬─────────┘      │ masks            │
                │                └────────┬─────────┘
                │                         │
                └────────────┬────────────┘
                             ▼
                    SYNTHETIC WORLD
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
              KNOWN TEST           ZERO-DAY TEST
                  │                     │
                  └──────────┬──────────┘
                             ▼
                         BLUE TEAM
```

---

# 3.46 Step-3 locked specification

This is the version we now carry into Step 4.

| ID  | Requirement                                       | Status                                |
| --- | ------------------------------------------------- | ------------------------------------- |
| D1  | Public-data empirical calibration                 | **LOCKED**                            |
| D2  | Multiple independent reference datasets           | **LOCKED**                            |
| D3  | Stateful payment simulator                        | **LOCKED**                            |
| D4  | 10,000 initial simulated customers                | **LOCKED MVP scale**                  |
| D5  | 8 customer archetypes                             | **LOCKED**                            |
| D6  | 10 merchant/MCC groups                            | **LOCKED initial taxonomy**           |
| D7  | Dynamic ledger state                              | **LOCKED**                            |
| D8  | Device/IP/location/session entities               | **LOCKED**                            |
| D9  | Token lifecycle modeling                          | **LOCKED simulation layer**           |
| D10 | Legitimate behavior generation                    | **LOCKED**                            |
| D11 | Hard-negative benign scenarios                    | **LOCKED**                            |
| D12 | Fraud scenario library                            | **LOCKED**                            |
| D13 | Mutability masks                                  | **LOCKED**                            |
| D14 | Attack mutation                                   | **LOCKED**                            |
| D15 | Attack coordination                               | **LOCKED**                            |
| D16 | Agentic fraud scenarios                           | **LOCKED**                            |
| D17 | DCR/near-duplicate screening                      | **LOCKED**                            |
| D18 | TabDDPM-Aug                                       | **CANDIDATE → must validate**         |
| D19 | Density-adaptive sampling                         | **CANDIDATE → must validate**         |
| D20 | GMM marginals                                     | **CANDIDATE → empirically validate**  |
| D21 | t-Copula                                          | **CANDIDATE → empirically validate**  |
| D22 | (\nu=4)                                           | **NOT FROZEN**                        |
| D23 | HOT-GNN                                           | **LOCKED candidate/async experiment** |
| D24 | DynBERG                                           | **LOCKED candidate/async experiment** |
| D25 | Async graph feature cache                         | **LOCKED architecture**               |
| D26 | Out-of-time evaluation                            | **LOCKED**                            |
| D27 | Zero-day attack evaluation                        | **LOCKED**                            |
| D28 | (\Gamma_{OOD})                                    | **LOCKED metric**                     |
| D29 | (\Gamma_{OOD}\geq0.75)                            | **TARGET, not guaranteed standard**   |
| D30 | Attack Success Rate                               | **LOCKED**                            |
| D31 | Statistical fidelity evaluation                   | **LOCKED**                            |
| D32 | Structural/graph fidelity evaluation              | **LOCKED**                            |
| D33 | Hidden attack metadata                            | **LOCKED**                            |
| D34 | Ground-truth reproducibility                      | **LOCKED**                            |
| D35 | No claims of Mastercard proprietary-data matching | **LOCKED**                            |

---

# 3.47 What we deliberately removed from the previous version

There are several claims from the supplied specification that **do not become factual claims in our final submission unless experimentally demonstrated**.

### Removed as unsupported certainty:

* "TabDDPM-Aug is definitively the top-ranked generator."
* "DCR guarantees zero memorization."
* "DCR gives exactly 48% privacy-leakage reduction."
* "(\nu=4) is universally correct."
* "HOT-GNN will necessarily improve our detector."
* "DynBERG will necessarily improve our detector."
* "Graph features will always arrive in <2 ms."
* "(\Gamma_{OOD}\geq0.75) is a universal championship benchmark."
* The exact attack dollar values as though they represent Mastercard's real transaction behavior.

They can remain **experimental hypotheses/targets**.

That is the difference between a technically credible submission and a document full of unverifiable numbers.

---

# 3.48 Final Step-3 architecture

The complete architecture after Steps 1–3 is now:

```text
                         ┌───────────────────────────┐
                         │          IDENTIFY         │
                         │                           │
                         │ GenAI fraud landscape     │
                         │ Agentic threats           │
                         │ Attack taxonomy           │
                         └────────────┬──────────────┘
                                      │
                                      ▼
                         ┌───────────────────────────┐
                         │    PUBLIC REFERENCES      │
                         │                           │
                         │ IEEE-CIS                  │
                         │ BAF / Feedzai             │
                         │ MoMTSim                   │
                         │ Synthetic bank references │
                         └────────────┬──────────────┘
                                      │
                                      ▼
                         ┌───────────────────────────┐
                         │     CALIBRATION LAYER     │
                         │                           │
                         │ distributions             │
                         │ dependencies              │
                         │ temporal behavior         │
                         │ entity structure          │
                         └────────────┬──────────────┘
                                      │
                                      ▼
                         ┌───────────────────────────┐
                         │     PAYMENT WORLD         │
                         │                           │
                         │ Customers                 │
                         │ Accounts                  │
                         │ Merchants                 │
                         │ Devices                   │
                         │ IP / Location             │
                         │ Tokens                    │
                         │ Sessions                  │
                         │ Ledger state              │
                         └────────────┬──────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
           ┌──────────────────┐               ┌──────────────────┐
           │ BENIGN ENGINE    │               │   RED TEAM       │
           │                  │               │                  │
           │ archetypes       │               │ attack library   │
           │ normal behavior  │               │ mutation         │
           │ hard negatives   │               │ coordination     │
           │ state evolution  │               │ agentic attacks  │
           └────────┬─────────┘               └────────┬─────────┘
                    │                                  │
                    └────────────────┬─────────────────┘
                                     ▼
                           SYNTHETIC PAYMENT WORLD
                                     │
                     ┌───────────────┼────────────────┐
                     ▼               ▼                ▼
                  TRAIN          TEMPORAL         ZERO-DAY
                                  TEST             TEST
                     │               │                │
                     └───────────────┼────────────────┘
                                     ▼
                           ┌──────────────────┐
                           │    BLUE TEAM     │
                           │                  │
                           │ GBDT             │
                           │ behavioral       │
                           │ temporal         │
                           │ relational      │
                           │ graph cache      │
                           └────────┬─────────┘
                                    │
                                    ▼
                             RISK DECISION
                                    │
                         ┌──────────┼──────────┐
                         ▼          ▼          ▼
                       ALLOW     STEP-UP      BLOCK
                                    │
                                    ▼
                              EVALUATION
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
               FP/FPR              FN                 ASR
                 │                  │                  │
                 └──────────────────┼──────────────────┘
                                    ▼
                             REPLAY BUFFER
                                    │
                       ┌────────────┴────────────┐
                       ▼                         ▼
                 RED ADAPTATION            BLUE HARDENING
                       │                         │
                       └────────────┬────────────┘
                                    ▼
                              NEXT ROUND
```

---

# 3.49 Why this Step 3 is strategically strong

The important thing is not that we have a lot of components.

It is that **each component now has a reason to exist**.

### Public datasets

Give us calibration evidence.

### Stateful world

Prevents random-row simulation.

### Hard negatives

Prevent shortcut learning.

### Attack library

Provides coverage.

### Mutability mask

Prevents unrealistic attacks.

### Agentic scenarios

Give us a Mastercard-relevant differentiator.

### Graph layer

Captures coordinated fraud.

### Temporal layer

Captures evolving attacks.

### Zero-day split

Tests generalization rather than memorization.

### Attack Success Rate

Measures whether the Red Team actually defeats the Blue Team.

### Replay loop

Turns the system into a genuine closed-loop defense.

---

# 3.50 STEP 3 — FINAL VERDICT

## **FINALIZED AND LOCKED**

The project now has a defensible simulation foundation:

> **A public-data-calibrated, stateful synthetic payment environment containing realistic legitimate behavior, hard negatives, coordinated fraud, and agentic-commerce attack scenarios, with explicit attack constraints, privacy screening, temporal/zero-day evaluation, and ground-truth attack metadata.**

The key innovation is still **not** "we used TabDDPM" or "we used HOT-GNN."

It is:

> **We create an adversarial payment world in which realistic attacks can evolve against a defense, including attacks the defense was never explicitly trained on.**

That is the foundation Step 4 needs.

---

## Master project flow after Step 3

```text
STEP 1
Competition Requirements
        ↓
STEP 2
Competitive Intelligence
        ↓
Innovation Hypothesis
        ↓
STEP 3
DATA & SIMULATION WORLD
        ↓
Public calibration
        ↓
Stateful payment world
        ↓
Legitimate behavior
        ↓
Hard negatives
        ↓
Fraud + agentic attacks
        ↓
Zero-day evaluation
        ↓
────────────────────────────
STEP 4
BLUE TEAM DETECTION ENGINE
────────────────────────────
        ↓
Feature Store
        ↓
GBDT baseline
        ↓
Behavioral + temporal
        ↓
Graph cache
        ↓
Cost-sensitive decisioning
        ↓
Explainability
        ↓
────────────────────────────
STEP 5
ADAPTIVE RED TEAM
────────────────────────────
        ↓
Attack adaptation
        ↓
Replay
        ↓
Adversarial hardening
        ↓
────────────────────────────
STEP 6
CLOSED-LOOP SYSTEM
────────────────────────────
        ↓
Red ↔ Blue iterations
        ↓
────────────────────────────
STEP 7
PROTOTYPE + EVIDENCE
────────────────────────────
        ↓
Dashboard
        ↓
Experiments
        ↓
Latency
        ↓
Attack demonstrations
        ↓
────────────────────────────
STEP 8
DOCX + GITHUB + KAGGLE
────────────────────────────
        ↓
FINAL SUBMISSION
```

# Step 4
Yes. I’ve incorporated the additional evidence into Step 4, but I’m making **one important correction** before freezing it: the report’s statement that *every* cited claim was independently verified is too strong. The main technical directions are supported, but some exact numerical claims are **dataset/paper-specific**, and at least one citation needs qualification.

For example, the 0.9916 ROC-AUC result is supported by a 2025 IEEE Access study involving LightGBM/XGBoost/CatBoost and resampling, but that does **not** mean our future model will achieve 0.9916 on our synthetic world. ([DOAJ][1]) Likewise, HOT-GNN is real and highly relevant, but its published results are benchmark-specific; its reported PaySim inference is not evidence that our implementation will meet a particular latency target. ([ScienceDirect][2])

With that correction, here is the **finalized Step 4**.

---

# STEP 4 — FINALIZED

# BLUE TEAM MULTI-SIGNAL DETECTION ENGINE

**Status: LOCKED**

## 4.0 Step objective

Step 3 created the **synthetic payment world**.

Step 4 builds the **defense operating inside that world**.

The Blue Team must:

1. detect fraudulent transactions,
2. detect coordinated/relational fraud,
3. detect temporal behavioral changes,
4. generalize toward unseen attacks,
5. control false positives,
6. produce calibrated risk,
7. choose an appropriate action,
8. explain the decision,
9. operate within a realistic latency budget.

The core principle is:

> **Do not start with a complicated GNN. Start with a strong tabular baseline, progressively add behavioral, temporal and relational intelligence, and only retain components that demonstrably improve the system.**

That principle is now frozen.

---

# 4.1 Final Blue Team architecture

```text
                         PAYMENT EVENT
                              │
                              ▼
                   ┌────────────────────┐
                   │ FEATURE CONSTRUCTION│
                   └──────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
 TRANSACTION             BEHAVIORAL             TEMPORAL
 FEATURES                 FEATURES              FEATURES
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    RELATIONAL FEATURES
                              │
                              ▼
                   ┌────────────────────┐
                   │ GBDT ENSEMBLE      │
                   │                    │
                   │ LightGBM           │
                   │ XGBoost            │
                   │ CatBoost           │
                   └──────────┬─────────┘
                              │
                              ▼
                       TABULAR RISK
                              │
               ┌──────────────┴──────────────┐
               │                             │
               ▼                             ▼
        REAL-TIME PATH                ASYNCHRONOUS PATH
               │                             │
               │                       HOT-GNN / DynBERG
               │                             │
               │                             ▼
               │                      GRAPH FEATURES
               │                             │
               │                         CACHE
               │                             │
               └──────────────┬──────────────┘
                              ▼
                       FUSION ENGINE
                              │
                              ▼
                     PROBABILITY CALIBRATION
                              │
                              ▼
                    CONFIDENCE / COST ROUTER
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
               ALLOW        STEP-UP       BLOCK
                              │
                              ▼
                        EXPLANATION
                              │
                              ▼
                         ERROR STORE
                              │
                              ▼
                     STEP 5 RED TEAM
```

---

# 4.2 The model-development ladder

We will **not build the entire architecture simultaneously**.

The experimental ladder is locked as follows.

### Blue Team B0

```text
Transaction features
        ↓
LightGBM
```

### B1

```text
B0
+
behavioral features
```

### B2

```text
B1
+
temporal features
```

### B3

```text
B2
+
relational features
```

### B4

```text
B3
+
LightGBM/XGBoost/CatBoost comparison
```

### B5

```text
B4
+
ensemble
```

### B6

```text
B5
+
HOT-GNN / DynBERG graph intelligence
```

### B7

```text
B6
+
calibration
+
cost-sensitive routing
```

This gives us a clean ablation trail.

---

# 4.3 Why GBDT is the foundation

Gradient-boosted trees are not being selected because they're fashionable.

They're being selected because:

* our data is predominantly tabular,
* we have mixed numerical/categorical features,
* nonlinear feature interactions matter,
* training/inference are comparatively practical,
* they provide strong baselines,
* and published fraud work continues to report strong results from these models.

A 2025 IEEE Access study reported an ensemble involving LightGBM, XGBoost and CatBoost improving ROC-AUC from 0.9132 to 0.9916 in its experimental setting, with further gains from stacking/SWA. ([DOAJ][1])

### But our rule is:

> **That number is evidence for testing GBDTs, not a target we pretend to have achieved.**

Our model gets its own measured score.

---

# 4.4 LightGBM / XGBoost / CatBoost

We will initially benchmark:

| Model    | Role                             |
| -------- | -------------------------------- |
| LightGBM | primary baseline                 |
| XGBoost  | strong comparison                |
| CatBoost | categorical-feature comparison   |
| Ensemble | only if validation proves useful |

We will use **identical train/validation/test partitions**.

No cherry-picking.

---

# 4.5 Ensemble

If the individual models produce useful complementary errors:

[
P_{ens}
=======

w_1P_{LGBM}
+
w_2P_{XGB}
+
w_3P_{CAT}
]

with:

[
w_1+w_2+w_3=1
]

Weights are selected using validation data.

We will not simply declare:

> "ensemble = better."

It must be demonstrated.

---

# 4.6 Feature architecture

The Blue Team feature store is divided into six major groups.

## F1 — Transaction features

```text
amount
currency
merchant category
payment channel
transaction type
token state
```

---

## F2 — Behavioral features

```text
customer transaction count
mean amount
median amount
amount variance
usual merchant categories
usual geography
usual transaction hours
```

---

## F3 — Velocity features

```text
transactions_1m
transactions_5m
transactions_15m
transactions_1h
amount_5m
amount_1h
unique_merchants_1h
```

---

## F4 — Behavioral-deviation features

This is particularly important.

For example:

[
z_{amount}
==========

\frac{x-\mu_{customer}}
{\sigma_{customer}+\epsilon}
]

So instead of merely asking:

> Is ₹20,000 unusual globally?

we ask:

> **Is ₹20,000 unusual for this customer?**

---

# 4.7 F5 — Entity features

Examples:

```text
new_device
new_IP
new_location
new_merchant

device_account_count
IP_account_count
merchant_customer_count
device_customer_count
```

These are generated from the relational world established in Step 3.

---

# 4.8 F6 — Relational features

Examples:

```text
shared_device_accounts
shared_IP_accounts
shared_merchant_accounts
cross_account_velocity
network_degree
network_growth
neighbor_risk
community_risk
```

These features give us a **graph-aware baseline without immediately deploying a GNN**.

This is important because we can determine whether graph structure itself is useful before paying the complexity cost of graph deep learning.

---

# 4.9 Temporal intelligence

Every transaction gets temporal context.

Initial candidate windows:

```text
1 minute
5 minutes
15 minutes
1 hour
6 hours
24 hours
7 days
```

We test them rather than assuming every window is useful.

Examples:

[
Velocity_{5m}
=============

N(transactions_{t-5m:t})
]

and:

[
AmountVelocity_{1h}
===================

\sum Amount_{t-1h:t}
]

---

# 4.10 Sequence intelligence

We also capture transitions:

```text
Merchant A
     ↓
Merchant B
     ↓
Merchant C
```

and:

```text
Location A
     ↓
Location B
     ↓
Location C
```

and:

```text
Device A
     ↓
Device B
```

These sequences can distinguish:

```text
legitimate behavioral evolution
```

from:

```text
rapid coordinated behavioral change
```

---

# 4.11 Class imbalance

This remains a **frozen requirement from Step 1**.

But we will not blindly use SMOTE everywhere.

### Candidates

```text
class weights
SMOTE
SMOTE-ENN
ADASYN
focal loss
threshold optimization
```

SMOTE-ENN has been used in recent fraud-detection work alongside ensemble tree models, supporting it as an experimental candidate. ([AITS Kadapa][3])

### Our initial preference

For the stateful temporal dataset:

> **class weighting + threshold optimization first.**

Then test resampling separately.

Why?

Because naive row-level oversampling can create synthetic observations that don't respect our temporal/entity relationships.

---

# 4.12 HOT-GNN

HOT-GNN is now a **formal candidate**, not merely a buzzword.

The 2026 paper describes HOT-GNN as a heterogeneous, multi-relational fraud detector designed for:

* heterophily,
* outliers,
* temporal information,
* class imbalance,
* camouflage.

Its architecture separates similar and dissimilar neighbors instead of assuming all neighboring entities should convey similar information. ([ScienceDirect][2])

The paper evaluates it on multiple fraud benchmarks, including PaySim. ([ScienceDirect][2])

### Why this fits our project

Our Step-3 fraud world intentionally contains:

```text
fraudulent account
      ↕
legitimate account
      ↕
shared device
      ↕
shared merchant
```

Fraud is therefore not necessarily surrounded by fraud.

That makes heterophily relevant.

---

# 4.13 HOT-GNN is NOT our default detector

This is important.

The paper reports strong benchmark performance, but its reported results do not prove that HOT-GNN will outperform our GBDT baseline on **our synthetic environment**.

Therefore:

```text
HOT-GNN
     ↓
candidate experiment
     ↓
measure
     ↓
keep only if useful
```

---

# 4.14 DynBERG

DynBERG is our second temporal-graph candidate.

The 2025 arXiv work, `2511.00047`, proposes a Dynamic BERT-based Graph Neural Network for financial fraud detection, combining Graph-BERT-style graph representation with temporal modeling and adapting the approach to directed edges. ([ResearchGate][4])

Its role in our architecture is:

> **evaluate whether dynamic graph representation provides additional information beyond our handcrafted temporal/relational features.**

Again:

**candidate, not guaranteed winner.**

---

# 4.15 G-GBM — added to Step 4

This is one of the useful additions from your new report.

The 2025 G-GBM paper (`arXiv:2510.05676`) investigates gradient-boosted decision trees directly on graph-derived information for heterogeneous/dynamic fraud settings, motivated partly by the class-imbalance and interpretability challenges of graph approaches. ([ResearchGate][5])

This is particularly relevant because it gives us a middle ground:

```text
Pure tabular GBDT
        │
        ▼
Graph features
        │
        ▼
G-GBM-style approach
        │
        ▼
Full GNN
```

Therefore G-GBM becomes a **candidate experiment between B3 and full GNN deployment**.

---

# 4.16 Updated graph/relational experiment ladder

```text
                 RELATIONAL INTELLIGENCE
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
       Handcrafted      G-GBM      GNN models
       graph features                │
                                     ├── HOT-GNN
                                     └── DynBERG
```

This is better than jumping straight from XGBoost to a complicated GNN.

---

# 4.17 Asynchronous graph architecture

Graph models will **not** sit blindly inside the critical payment path.

Instead:

```text
                         PAYMENT
                            │
                            ▼
                    FAST BLUE TEAM
                            │
                            │
                    ┌───────┴───────┐
                    │               │
                    │       ASYNC GRAPH ENGINE
                    │               │
                    │        ┌──────┴──────┐
                    │        ▼             ▼
                    │     HOT-GNN       DynBERG
                    │        │             │
                    │        └──────┬──────┘
                    │               ▼
                    │        GRAPH FEATURES
                    │               │
                    │             CACHE
                    │               │
                    └───────────────┘
```

The fast path consumes the **latest available graph intelligence**.

---

# 4.18 Why this architecture matters

If the graph model takes too long:

```text
payment
  ↓
wait for GNN
  ↓
decision
```

we have an operational problem.

Instead:

```text
payment
  ↓
GBDT + cached graph intelligence
  ↓
decision
```

while:

```text
graph engine
  ↓
updates cache asynchronously
```

This gives us a realistic path toward low latency.

---

# 4.19 Latency requirement

We retain:

> **real-time feasibility is mandatory.**

But we remove unsupported hard claims such as:

> "graph inference will definitely be <2 ms."

The HOT-GNN paper itself reports different inference timings depending on batch/model configuration; for PaySim it reports approximately 0.13 ms/sample in its own experimental setup, but that is **not transferable directly to our architecture**. ([ScienceDirect][2])

Our system must measure:

```text
P50
P95
P99
```

for the complete decision path.

---

# 4.20 Calibration

The Blue Team does not directly treat raw model outputs as trustworthy probabilities.

We therefore test:

### Platt scaling

and

### Isotonic regression.

These are standard calibration candidates.

The important principle is:

```text
model score
     ↓
calibration
     ↓
risk estimate
```

not:

```text
raw score
     ↓
pretend it is probability
```

---

# 4.21 Important correction to the supplied report

The report states:

> Platt scaling and isotonic regression reduce Brier by ~30% and ECE by ~70%.

We **do not freeze those percentages as expected results**.

Those numbers are study-specific unless we identify and reproduce the exact experiment.

Our requirement is:

> **Measure Brier score and ECE before and after calibration on our own validation/test setup.**

That is the scientifically correct version.

---

# 4.22 Decision threshold

The supplied report correctly identifies Youden's J as a threshold-selection method.

[
J=Sensitivity+Specificity-1
]

It is a legitimate diagnostic threshold criterion, and recent fraud work has used threshold optimization based on Youden's J. ([IJRPR][6])

### But we make an important upgrade:

**Youden's J will NOT be our only threshold method.**

Why?

Because Mastercard's challenge explicitly cares about:

* detection,
* false positives,
* real-world feasibility.

Youden's J effectively gives equal importance to sensitivity and specificity.

Payment systems may not have equal costs.

Therefore we compare:

```text
Youden J
F1-optimal threshold
PR-based operating point
cost-sensitive threshold
fixed-FPR threshold
```

and choose the operationally defensible strategy.

---

# 4.23 Cost-sensitive routing

The final system is not merely:

```text
fraud / not fraud
```

It produces:

```text
ALLOW
STEP-UP
BLOCK
```

For action (a):

[
a^*=\arg\min_a E[C(a|x)]
]

The cost model will include:

* fraud loss,
* false-positive/customer friction,
* verification cost,
* blocking cost.

We will use **relative/configurable costs**, not pretend Mastercard gave us proprietary financial values.

---

# 4.24 Confidence Router

The router receives:

```text
calibrated risk
+
model agreement
+
graph confidence
+
data quality
+
transaction context
```

Then:

```text
HIGH CONFIDENCE / LOW RISK
        ↓
      ALLOW
```

```text
UNCERTAIN
        ↓
    STEP-UP
```

```text
HIGH CONFIDENCE / HIGH RISK
        ↓
      BLOCK
```

This is the operational layer.

---

# 4.25 Why model disagreement matters

Suppose:

```text
GBDT       → 0.91 fraud
Graph      → 0.22 fraud
Temporal   → 0.30 fraud
```

That should not necessarily be treated the same as:

```text
GBDT       → 0.91
Graph      → 0.94
Temporal   → 0.89
```

The second case has much stronger cross-signal agreement.

Therefore **uncertainty itself becomes a signal**.

---

# 4.26 Explainability

For every decision we retain structured evidence.

Example:

```text
RISK = 0.94

WHY?

1. 7.1× normal customer velocity
2. New device
3. Device associated with 4 accounts
4. Merchant category is historically rare
5. Cross-account burst detected
```

For a graph event:

```text
DEVICE D17
    ↓
ACCOUNT A
ACCOUNT B
ACCOUNT C
ACCOUNT D
```

This is much more useful to an investigator than:

```text
fraud_probability = 0.94
```

---

# 4.27 SHAP

For tree models:

```text
Transaction
     ↓
GBDT
     ↓
SHAP
     ↓
feature contributions
```

This is our primary explanation mechanism.

---

# 4.28 LLM explanation layer

The LLM is **not part of the fraud classifier**.

Architecture:

```text
Detector
   ↓
Structured evidence
   ↓
LLM
   ↓
Human-readable summary
```

The LLM cannot invent facts.

Example input:

```json
{
  "risk": 0.94,
  "velocity_ratio": 7.1,
  "new_device": true,
  "device_account_count": 4
}
```

Output:

> "The payment is high risk because transaction velocity is substantially above the customer's historical pattern, the device is new, and the same device is associated with multiple accounts."

---

# 4.29 Classifier vs explanation separation

This becomes a hard architectural rule:

```text
                    ┌─────────────┐
TRANSACTION ───────►│   DETECTOR  │
                    └──────┬──────┘
                           │
                           ▼
                     RISK DECISION
                           │
                           ▼
                    STRUCTURED FACTS
                           │
                           ▼
                         LLM
                           │
                           ▼
                    INVESTIGATOR TEXT
```

Never:

```text
Transaction
   ↓
LLM
   ↓
fraud decision
```

---

# 4.30 Evaluation metrics

The Blue Team will report:

## Detection

* PR-AUC
* ROC-AUC
* precision
* recall
* F1

## False-positive control

* FPR
* false-positive count
* legitimate approval rate

## Calibration

* Brier score
* ECE
* reliability curve

## Novel attacks

* zero-day PR-AUC
* zero-day recall
* (\Gamma_{OOD})

## Operational

* P50 latency
* P95 latency
* P99 latency
* throughput

## Adversarial

* Attack Success Rate

---

# 4.31 Accuracy is NOT the primary metric

This remains frozen.

If:

```text
99.8% legitimate
0.2% fraud
```

a classifier predicting everything legitimate gets 99.8% accuracy.

That tells us almost nothing.

Therefore:

> **PR-AUC + recall/precision + false-positive behavior + operational cost are primary.**

---

# 4.32 Zero-day evaluation

The Blue Team must be tested on attacks it hasn't seen during training.

Example:

### Training

```text
Account takeover
Velocity attack
Device farm
Mule network
```

### Test

```text
Agentic intent drift
Multi-agent smurfing
Token replay
```

This is where our system's real novelty can be demonstrated.

---

# 4.33 (\Gamma_{OOD})

We retain:

[
\Gamma_{OOD}
============

\frac{
PR\text{-}AUC_{zero-day}
}{
PR\text{-}AUC_{known}
}
]

Interpretation:

```text
≈ 1.0
↓
little degradation

lower value
↓
large degradation
```

### Target

[
\Gamma_{OOD}\geq0.75
]

is retained as an **internal project target**, not claimed as a universal industry standard.

---

# 4.34 Error taxonomy

Every false negative must be categorized.

```text
FALSE NEGATIVE
│
├── unseen attack
├── behavioral camouflage
├── graph camouflage
├── low-velocity attack
├── temporal drift
├── agentic intent drift
├── coordinated attack
└── feature failure
```

Every false positive:

```text
FALSE POSITIVE
│
├── travel
├── flash sale
├── household device
├── B2B activity
├── legitimate AI-agent behavior
└── behavioral drift
```

This is critical because **Step 5 consumes these errors**.

---

# 4.35 Ablation table

Our final experimental report will contain something like:

| Version | Transaction | Behavioral | Temporal | Relational |    G-GBM |  HOT-GNN |  DynBERG | PR-AUC | FPR | Recall | P99 |
| ------- | ----------: | ---------: | -------: | ---------: | -------: | -------: | -------: | -----: | --: | -----: | --: |
| B0      |           ✓ |            |          |            |          |          |          |        |     |        |     |
| B1      |           ✓ |          ✓ |          |            |          |          |          |        |     |        |     |
| B2      |           ✓ |          ✓ |        ✓ |            |          |          |          |        |     |        |     |
| B3      |           ✓ |          ✓ |        ✓ |          ✓ |          |          |          |        |     |        |     |
| B4      |           ✓ |          ✓ |        ✓ |          ✓ |        ✓ |          |          |        |     |        |     |
| B5      |           ✓ |          ✓ |        ✓ |          ✓ |          |        ✓ |          |        |     |        |     |
| B6      |           ✓ |          ✓ |        ✓ |          ✓ |          |          |        ✓ |        |     |        |     |
| B7      |        Full |       Full |     Full |       Full | optional | optional | optional |        |     |        |     |

This table is **not decorative**.

It is how we prove which architectural decision was actually useful.

---

# 4.36 The critical experiment

One experiment is particularly important for winning this challenge:

## Known vs unseen attacks

```text
                  KNOWN ATTACKS       UNSEEN ATTACKS
                       │                     │
                       ▼                     ▼
                  Blue Team              Blue Team
                       │                     │
                       ▼                     ▼
                   PR-AUC                PR-AUC
                       │                     │
                       └─────────┬───────────┘
                                 ▼
                              ΓOOD
```

Then compare:

```text
B0
vs
B3
vs
B5/B6
```

If graph/temporal intelligence provides a meaningful advantage specifically on unseen coordinated attacks, **that becomes a central competition result**.

---

# 4.37 G-GBM's strategic position

The addition of G-GBM improves our architecture because we now have a progression:

```text
TABULAR
   │
   ▼
GBDT
   │
   ▼
GBDT + RELATIONAL FEATURES
   │
   ▼
G-GBM
   │
   ▼
GRAPH NEURAL NETWORK
   │
   ├── HOT-GNN
   └── DynBERG
```

This lets us answer a sophisticated question:

> **How much graph intelligence do we actually need?**

Maybe handcrafted graph features get 95% of the benefit.

Maybe G-GBM wins.

Maybe HOT-GNN only helps zero-day attacks.

Maybe DynBERG is too expensive.

**We will let the experiments decide.**

---

# 4.38 Step-4 locked requirements

| ID  | Requirement                          | Status                               |
| --- | ------------------------------------ | ------------------------------------ |
| B1  | LightGBM baseline                    | **LOCKED**                           |
| B2  | XGBoost comparison                   | **LOCKED**                           |
| B3  | CatBoost comparison                  | **LOCKED**                           |
| B4  | Ensemble only if validated           | **LOCKED**                           |
| B5  | Transaction features                 | **LOCKED**                           |
| B6  | Behavioral features                  | **LOCKED**                           |
| B7  | Temporal features                    | **LOCKED**                           |
| B8  | Relational features                  | **LOCKED**                           |
| B9  | Customer-specific deviation features | **LOCKED**                           |
| B10 | Velocity features                    | **LOCKED**                           |
| B11 | Class imbalance treatment            | **LOCKED**                           |
| B12 | Class weighting baseline             | **LOCKED**                           |
| B13 | SMOTE/SMOTE-ENN/ADASYN experiments   | **CANDIDATES**                       |
| B14 | Calibration                          | **LOCKED**                           |
| B15 | Platt scaling                        | **CANDIDATE**                        |
| B16 | Isotonic regression                  | **CANDIDATE**                        |
| B17 | Youden J                             | **CANDIDATE threshold method**       |
| B18 | Cost-sensitive threshold             | **LOCKED**                           |
| B19 | ALLOW / STEP-UP / BLOCK              | **LOCKED**                           |
| B20 | Confidence routing                   | **LOCKED**                           |
| B21 | HOT-GNN                              | **CANDIDATE graph model**            |
| B22 | DynBERG                              | **CANDIDATE temporal graph model**   |
| B23 | G-GBM                                | **CANDIDATE graph-boosting model**   |
| B24 | Async graph processing               | **LOCKED architecture**              |
| B25 | Graph feature cache                  | **LOCKED architecture**              |
| B26 | SHAP explanations                    | **LOCKED**                           |
| B27 | LLM investigator summary             | **LOCKED as explanation layer only** |
| B28 | PR-AUC                               | **PRIMARY**                          |
| B29 | ROC-AUC                              | **SECONDARY**                        |
| B30 | F1 / precision / recall              | **LOCKED**                           |
| B31 | FPR / approval rate                  | **LOCKED**                           |
| B32 | Brier / ECE                          | **LOCKED**                           |
| B33 | P50/P95/P99 latency                  | **LOCKED**                           |
| B34 | Zero-day evaluation                  | **LOCKED**                           |
| B35 | (\Gamma_{OOD})                       | **LOCKED**                           |
| B36 | (\Gamma_{OOD}\geq0.75)               | **INTERNAL TARGET**                  |
| B37 | Attack Success Rate                  | **LOCKED**                           |
| B38 | Error taxonomy                       | **LOCKED**                           |
| B39 | Ablation study                       | **LOCKED**                           |
| B40 | No unsupported performance claims    | **LOCKED**                           |

---

# 4.39 What Step 4 gives Step 5

This is the most important connection.

At the end of Step 4 we will have:

```text
                    BLUE TEAM
                        │
                        ▼
                  TRANSACTION
                        │
                        ▼
                   DECISION
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
        ALLOW         STEP-UP       BLOCK
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                     OUTCOME
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
          DETECTED             MISSED
              │                   │
              │                   ▼
              │             ERROR TAXONOMY
              │                   │
              └─────────┬─────────┘
                        ▼
                  STEP 5 RED TEAM
```

The missed attacks are **not discarded**.

They become the Red Team's targets.

---

# 4.40 Updated master project flow

```text
STEP 1
COMPETITION REQUIREMENTS
        ↓
What Mastercard actually wants
        ↓
STEP 2
COMPETITIVE INTELLIGENCE
        ↓
How we differentiate
        ↓
STEP 3
DATA & SIMULATION WORLD
        ↓
Public calibration
        ↓
Stateful payment world
        ↓
Legitimate behavior
        ↓
Hard negatives
        ↓
Fraud scenarios
        ↓
Agentic attacks
        ↓
Zero-day test environment
        ↓
STEP 4
BLUE TEAM
        ↓
GBDT baseline
        ↓
Behavioral intelligence
        ↓
Temporal intelligence
        ↓
Relational intelligence
        ↓
G-GBM experiment
        ↓
HOT-GNN / DynBERG experiments
        ↓
Calibration
        ↓
Cost-sensitive routing
        ↓
ALLOW / STEP-UP / BLOCK
        ↓
SHAP + evidence
        ↓
ERROR TAXONOMY
        ↓
STEP 5
ADAPTIVE RED TEAM
        ↓
STEP 6
CLOSED-LOOP CO-EVOLUTION
        ↓
STEP 7
PROTOTYPE + EVIDENCE
        ↓
STEP 8
DOCX + GITHUB + KAGGLE
        ↓
FINAL SUBMISSION
```

---

# STEP 4 — FINAL VERDICT

## **FINALIZED AND LOCKED**

The final Blue Team is **not "a GNN fraud detector."**

It is:

> **A calibrated, cost-sensitive, multi-signal fraud defense whose strong tabular backbone is progressively augmented with behavioral, temporal and relational intelligence, with asynchronous graph models used only where experiments demonstrate additional value.**

That distinction is important.

Our competitive hypothesis is now:

> **A strong tabular detector handles ordinary fraud well; relational + temporal intelligence should provide the additional advantage against coordinated, camouflaged and previously unseen attacks.**

And we will **prove or disprove that hypothesis experimentally**.

The newly incorporated research supports the major candidates:

* GBDT ensembles are a credible baseline family. ([DOAJ][1])
* SMOTE-ENN is a legitimate imbalance-handling candidate, but not automatically our best method. ([AITS Kadapa][3])
* HOT-GNN directly addresses heterophily, camouflage and temporal information in fraud graphs. ([ScienceDirect][2])
* DynBERG is a relevant dynamic financial-graph candidate. ([ResearchGate][4])
* G-GBM provides a useful graph + gradient-boosting middle ground. ([ResearchGate][5])
* Youden's J is a legitimate threshold-selection method, but our final router will be cost-sensitive rather than blindly maximizing J. ([IJRPR][6])

**Step 4 is now closed.**


# Step 5
Understood. I’ll integrate those six enhancements into the **already-corrected Step 5**, not append them as a separate addendum. I’ll also preserve the corrections we made earlier, because several of the proposed "hard" claims should remain experimental rather than being falsely presented as guaranteed thresholds.

# STEP 5 — ADAPTIVE RED TEAM ENGINE

## Final Master Specification v4.0 — LOCKED

### Purpose

Step 5 is the adversarial half of our system.

Its job is to continuously answer:

> **What realistic, novel, economically feasible attack can still fool our current Blue Team?**

The Red Team therefore does **not** maximize evasion alone. It must optimize:

**evasion + fidelity + impact + novelty + diversity − attack cost**, while obeying the rules of our synthetic payment world.

This is the point where our project stops being a conventional "fraud classifier + synthetic data" project and becomes an **adaptive payment-security laboratory**.

The supplied v3.0 specification already established the Stackelberg adversary, dual attack streams, Pareto search, fidelity gates and Blue-Team feedback.  We now incorporate the additional enhancements into that architecture.

---

# 5.1 Final Architecture

```text
                         ┌─────────────────────────────┐
                         │     ATTACK KNOWLEDGE BASE    │
                         │                             │
                         │ Attack families            │
                         │ Attack grammar              │
                         │ Motif memory                │
                         │ Blue-Team weaknesses        │
                         │ Historical attack outcomes  │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │   STACKELBERG ADVERSARY     │
                         │                             │
                         │ Anticipatory Red strategy   │
                         │ Predict Blue adaptation     │
                         └──────────────┬──────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
          ┌────────────────────┐                  ┌────────────────────┐
          │ STREAM A           │                  │ STREAM B           │
          │ PAYMENT + GRAPH    │                  │ AGENTIC            │
          │                    │                  │                    │
          │ Graph injection    │                  │ Intent drift       │
          │ Camouflage         │                  │ Agent swarm        │
          │ Temporal attacks   │                  │ Context mismatch   │
          │ Synthetic identity │                  │ Mandate abuse      │
          └──────────┬─────────┘                  └──────────┬─────────┘
                     └────────────────┬──────────────────────┘
                                      ▼
                         ┌─────────────────────────────┐
                         │      ATTACK GRAMMAR         │
                         │                             │
                         │ Compose attack primitives   │
                         │ Create novel combinations   │
                         └──────────────┬──────────────┘
                                        ▼
                         ┌─────────────────────────────┐
                         │      MUTATION ENGINE         │
                         │                             │
                         │ Amount / timing / device   │
                         │ IP / merchant / sequence   │
                         │ Graph / agent / intent     │
                         └──────────────┬──────────────┘
                                        ▼
                         ┌─────────────────────────────┐
                         │   COUNTERFACTUAL SEARCH     │
                         │                             │
                         │ Find minimum change needed  │
                         │ to cross decision boundary  │
                         └──────────────┬──────────────┘
                                        ▼
                         ┌─────────────────────────────┐
                         │ VALIDITY + MUTABILITY GUARD │
                         └──────────────┬──────────────┘
                                        ▼
                  ┌────────────────────────────────────────────┐
                  │ QUALITY / FIDELITY / NOVELTY / DIVERSITY │
                  │                  GATES                    │
                  └────────────────────┬───────────────────────┘
                                       ▼
                         ┌─────────────────────────────┐
                         │      NSGA-II SEARCH         │
                         │                             │
                         │ Evasion                     │
                         │ Fidelity                    │
                         │ Impact                      │
                         │ Novelty                     │
                         │ Diversity                   │
                         │ Cost                        │
                         └──────────────┬──────────────┘
                                        ▼
                         ┌─────────────────────────────┐
                         │       BLUE TEAM TEST        │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
                    DETECTED                         MISSED
                         │                             │
                         ▼                             ▼
                  Hardness record              WEAKNESS STORE
                                                       │
                                  ┌────────────────────┘
                                  ▼
                         ADVERSARIAL MOTIF MEMORY
                                  │
                                  ▼
                         NEXT ATTACK GENERATION
```

---

# 5.2 Research foundation

The major research pillars are retained:

| Component                         | Evidence                             | How we use it                                        |
| --------------------------------- | ------------------------------------ | ---------------------------------------------------- |
| **GT-ACGL / Stackelberg**         | 2026 *Scientific Reports*            | Strategic Red ↔ Blue adaptation                      |
| **MonTi**                         | AAAI 2025                            | Multi-target graph injection                         |
| **CamFD**                         | 2026 dynamic-graph fraud research    | Camouflage-aware temporal/relational defense context |
| **AP2 red teaming**               | 2026 research                        | Agentic payment attack scenarios                     |
| **NSGA-II**                       | Evolutionary optimization literature | Multi-objective attack search                        |
| **Akamai agentic fraud research** | 2026 threat intelligence             | Emerging agentic/synthetic-identity scenarios        |

One important discipline remains:

> **Research results justify our design choices; they do not guarantee our system will reproduce those published scores.**

For example, if a paper reports 99% F1 on its benchmark, we will never write that our architecture therefore "achieves 99% F1" until **our own experiment demonstrates it**.

That distinction stays locked.

---

# 5.3 Official competition alignment

The competition's five evaluation dimensions remain our controlling framework.

| Mastercard requirement     | Our Step 5 response                                    |
| -------------------------- | ------------------------------------------------------ |
| **Attack diversity**       | 10+ families + attack grammar + composite attacks      |
| **Attack fidelity**        | statistical + behavioral + temporal + graph fidelity   |
| **Detection efficacy**     | every generated attack evaluated by Blue Team          |
| **Novelty**                | novel combinations + novelty scoring + adaptive search |
| **Real-world feasibility** | resource budgets + mutability + constrained simulation |

This means Step 5 isn't innovation for innovation's sake.

Every component must ultimately answer one of those judging criteria.

---

# 5.4 Attack taxonomy

The original 10 families remain.

### R1 — Account Takeover

Credential/session compromise followed by behavior designed to resemble the victim.

### R2 — Sybil Device Farm

Synthetic accounts sharing coordinated device/network characteristics.

### R3 — Coordinated Mule Dispersion

Funds distributed through multiple intermediary entities.

### R4 — Micro-Velocity Probing

Small transactions designed to stay beneath simplistic velocity thresholds.

### R5 — Low-and-Slow Drain

Small, distributed transactions over extended periods.

### R6 — Collusive Merchant Manipulation

Merchant/POS-side coordinated fraud patterns.

### R7 — Multi-Target Graph Injection

Structural camouflage against graph-based detection.

### R8 — Agentic Intent Drift

Agent remains authenticated but its behavior diverges from the intended mandate.

### R9 — Multi-Agent Swarm Smurfing

Multiple autonomous agents coordinate individually plausible transactions.

### R10 — Authorization Context Replay

Valid authorization paired with inconsistent transaction context.

---

# 5.5 NEW R11 — Frankenstein Synthetic Identity

This enhancement is now **officially added**.

A synthetic identity attack combines:

```text
realistic attributes
+
fabricated attributes
+
synthetically generated behavioral history
```

For example:

```text
identity
  │
  ├── plausible demographic attributes
  ├── plausible account age
  ├── synthetic transaction history
  ├── generated device behavior
  └── fabricated relationships
```

The point is **not** to create real identities.

Everything is synthetic.

The point is to test whether our Blue Team can detect an entity whose components individually appear legitimate but whose **joint behavioral/relational structure is abnormal**.

This directly strengthens the **Identify** and **Generate** dimensions.

---

# 5.6 Why R11 matters

A traditional detector may ask:

> "Is this feature suspicious?"

Our system should ask:

> **"Does this entire identity make sense as a coherent entity?"**

That gives us:

```text
attribute consistency
+
behavior consistency
+
temporal consistency
+
relationship consistency
```

as the identity-level detection problem.

---

# 5.7 Attack grammar

This is now a permanent component.

Instead of hardcoding every attack, define primitives:

```text
CREATE_ENTITY
LINK_DEVICE
AUTHENTICATE
TRANSACT
TRANSFER
SPLIT
CONVERGE
CHANGE_CONTEXT
ALTER_TIMING
SPREAD
CASH_OUT
```

Then compose them:

```text
CREATE
 ↓
LINK
 ↓
TRANSACT
 ↓
SPLIT
 ↓
CONVERGE
 ↓
CASH_OUT
```

This allows the Red Team to create attacks that were **not explicitly written into the original taxonomy**.

That is important for the "novel attack" requirement.

---

# 5.8 Composite attacks

The taxonomy is therefore not the limit.

Examples:

```text
R5 + R7
Low-and-slow
+
graph camouflage
```

```text
R8 + R9
Intent drift
+
multi-agent coordination
```

```text
R2 + R5 + R7
Device farm
+
low-and-slow
+
graph camouflage
```

```text
R11 + R7
Synthetic identity
+
graph camouflage
```

This is where the attack generator starts producing **new attack families rather than merely variations of known ones**.

---

# 5.9 Stackelberg adversary

The Red Team treats the Blue Team as an adaptive opponent.

Conceptually:

[
\max_{\theta_R}
U_R(\theta_R,\phi_B^*)
]

where:

[
\phi_B^*
========

\arg\min_{\phi_B}
L_B
]

The practical meaning is:

> **Don't only attack today's detector. Search for attacks that remain difficult after the detector responds.**

This is the key distinction between static adversarial testing and our adaptive Red Team.

---

# 5.10 Adversarial Motif Memory

We retain the motif-memory architecture from v3.0. The supplied specification explicitly defines structured motif records containing topology, timing, graph metrics, success count and evasion history. 

It stores:

* attack topology,
* temporal pattern,
* evasion history,
* attack family,
* associated weaknesses,
* mutation history.

So successful attack structures are not forgotten.

---

# 5.11 Dual-stream generation

## Stream A

```text
Payment
Behavior
Temporal
Graph
Identity
```

## Stream B

```text
Agent identity
Mandate
Intent
Context
Multi-agent behavior
Authorization
```

They can also interact:

```text
Agentic attack
       +
Graph camouflage
       +
Low-and-slow behavior
```

This cross-stream composition is particularly important.

---

# 5.12 Graph injection

The MonTi research is relevant here because it explicitly investigates multi-target graph injection against GNN fraud detection. 

Our implementation will therefore support:

```text
node injection
edge injection
attribute mutation
degree budgeting
motif camouflage
temporal rewiring
```

But we will call it:

> **MonTi-inspired graph injection**

unless our implementation reproduces MonTi itself.

No false attribution.

---

# 5.13 Temporal camouflage

The attacker can manipulate:

* transaction timing,
* inter-arrival behavior,
* active hours,
* weekend/weekday pattern,
* burst duration,
* attack duration,
* temporal motifs.

And we correct the statistical model:

For a Poisson process:

[
N(t)\sim Poisson(\lambda t)
]

while inter-arrival times are:

[
\Delta t\sim Exponential(\lambda)
]

But we will **not force every customer into a Poisson model**.

Realistic customer-specific empirical distributions will take priority.

---

# 5.14 NEW — Temporal Motif Signatures

This enhancement now becomes a **Step 4 ↔ Step 5 contract**.

Step 5 generates:

```text
temporal motifs
```

Step 4 detects:

```text
temporal motifs
```

Examples:

```text
A → B → C
```

```text
A → B
B → A
```

```text
A → B
A → C
A → D
```

The Red Team can camouflage timing while preserving the structural motif.

The Blue Team must therefore learn whether:

> **the temporal structure itself is suspicious.**

This creates a direct adversarial relationship between Steps 4 and 5.

---

# 5.15 Agentic Red Team

Each synthetic AI agent has:

```text
identity
owner
mandate
spending limit
merchant restrictions
category restrictions
time window
token/session
transaction history
declared intent
```

This enables attacks that ordinary transaction datasets cannot represent.

---

# 5.16 Agentic R8 — Intent drift

Example:

```text
Declared:
"Purchase office supplies"

Observed:
"Digital gift card purchase"
```

The credential can still be valid.

The question is:

> **Does the action remain consistent with the user's intended authorization?**

---

# 5.17 Semantic intent divergence

We retain:

[
I_{drift}
=========

1-\cos(e_{mandate},e_{transaction})
]

But the threshold is **learned/calibrated**, not permanently fixed at 0.45.

That threshold must be determined from our simulated validation data.

---

# 5.18 Agentic R9 — Swarm

```text
Agent 1 ─┐
Agent 2 ─┤
Agent 3 ─┤
Agent 4 ─┼── coordinated activity
Agent 5 ─┤
Agent 6 ─┘
```

Each individual agent may look legitimate.

The relationship among them is suspicious.

This gives the graph detector a genuine reason to exist.

---

# 5.19 Agentic R10 — Authorization context mismatch

The attacker preserves:

```text
valid identity
valid credential
valid authorization
```

but changes:

```text
merchant
purpose
category
destination
context
aggregate behavior
```

The Blue Team must detect contextual inconsistency.

---

# 5.20 NSGA-II multi-objective optimization

This is now the Red Team search engine.

We optimize:

[
F(A)=
[
Evasion,
Fidelity,
Impact,
Novelty,
Diversity,
-Cost
]
]

subject to:

[
A\in\Omega_{valid}
]

The optimizer does not simply find:

> "the attack that fools the model most."

It finds the **Pareto frontier of useful attacks**.

---

# 5.21 NEW — NSGA-II Blue-Team optimization

The supplied enhancement also recommends NSGA-II for Step 4 hyperparameter optimization.

We therefore create a clear distinction:

### Step 4

NSGA-II can optimize the **Blue Team's model/routing configuration**.

### Step 5

NSGA-II optimizes **Red-Team attack candidates**.

This is important because the two uses have different objectives.

For the Blue Team:

```text
maximize detection
+
minimize false positives
+
minimize latency
+
maintain calibration
```

For the Red Team:

```text
maximize evasion
+
maximize fidelity
+
maximize novelty
+
maximize impact
+
maximize diversity
-
minimize cost
```

This gives us a genuinely adversarial optimization relationship.

---

# 5.22 Mutability mask

Locked.

[
A_{t+1}
=======

m\odot(A_t+\delta)
+
(1-m)\odot A_t
]

### Mutable

* current amount
* timing
* merchant
* device/session
* IP/network context
* transaction sequence
* agent context.

### Immutable

* historical account age
* historical transactions
* issuer identity
* established historical statistics.

The original v3.0 specification correctly establishes this distinction. 

---

# 5.23 Counterfactual attacker

Now formally locked.

The Red Team asks:

> **What is the smallest realistic modification that changes the Blue-Team decision?**

[
\Delta^*
========

\arg\min_\Delta Cost(\Delta)
]

subject to:

[
Decision(A+\Delta)\neq Decision(A)
]

Example:

```text
BLOCK
 ↓
change timing
+
slightly alter amount
+
use known device
 ↓
ALLOW
```

This reveals the actual defensive decision boundary.

---

# 5.24 Why this is powerful

Instead of telling Mastercard:

> "Our model missed this."

we can tell them:

> **"The minimum realistic behavioral change that caused the model to miss the attack was X."**

That is much more actionable.

---

# 5.25 Evasion Efficiency

Now a core metric:

[
EE=
\frac{SuccessfulEvasions}{AttackCost}
]

Cost may include:

* transactions,
* graph modifications,
* agents,
* probes,
* simulation time.

This prevents brute-force attack generation from looking artificially impressive.

---

# 5.26 Attack cost

The Red Team receives an attacker budget.

Examples:

```text
maximum transactions
maximum graph changes
maximum agents
maximum reconnaissance
maximum time
```

We will evaluate multiple budgets rather than arbitrarily hard-coding one:

```text
Budget 0
Budget 5
Budget 10
Budget 20
```

and plot:

[
AttackBudget \rightarrow ASR
]

---

# 5.27 Fidelity gates

We retain:

* marginal distributions,
* correlation structure,
* temporal distributions,
* graph statistics,
* behavioral consistency,
* anti-memorization checks.

But KS < 0.05 and Frobenius < 0.35 are **calibration candidates**, not universal laws.

The final thresholds come from validation experiments.

---

# 5.28 Graph fidelity

Add explicit comparison of:

```text
degree distribution
clustering
community structure
path length
motif frequency
connected components
temporal motif distribution
```

This is critical because Mastercard explicitly evaluates **simulation fidelity**, not merely column-level similarity.

---

# 5.29 Identity fidelity

For R11 we also compare:

```text
attribute coherence
behavior coherence
temporal coherence
relationship coherence
```

A synthetic identity that matches individual fields but produces impossible relationships should fail the fidelity gate.

---

# 5.30 Anti-memorization

We retain:

* nearest-neighbor distance,
* duplicate rate,
* rare-record overlap,
* training-record similarity.

But the language remains:

> **anti-memorization evidence**

not:

> "guaranteed privacy."

---

# 5.31 Attack novelty

Now formally locked:

[
Novelty(A)
==========

Distance(A,\mathcal A_{known})
]

where (\mathcal A_{known}) represents previously observed/generated attack structures.

We can measure novelty across:

* behavior,
* graph topology,
* timing,
* attack composition,
* agentic intent.

---

# 5.32 Attack diversity

We measure:

```text
family diversity
behavioral diversity
graph diversity
temporal diversity
agentic diversity
```

This ensures the Red Team doesn't generate 10,000 versions of one attack.

---

# 5.33 Attack surface map

This becomes a Step 7 visualization requirement.

Example:

```text
                    EVASION
                       ▲
                       │
              ●        │        ●
       graph attack    │    agentic drift
                       │
          ●            │
      low-and-slow     │
                       │
                       └──────────────────►
                              FIDELITY
```

The Pareto frontier can be overlaid.

This gives judges an immediate visual answer to:

> **"What parts of the attack surface has your system explored?"**

---

# 5.34 Weakness Store

Every Blue-Team failure becomes structured knowledge:

```text
attack family
features
graph motif
temporal pattern
agent context
Blue score
decision
confidence
explanation
attack cost
fidelity
novelty
```

The Red Team uses it to select its next attack.

---

# 5.35 Final feedback mechanism

```text
RED
 ↓
ATTACK
 ↓
BLUE
 ↓
DETECTED / MISSED
 ↓
WEAKNESS ANALYSIS
 ↓
MOTIF MEMORY
 ↓
RED MUTATION
 ↓
NEW ATTACK
```

This is the foundation for Step 6.

---

# 5.36 Hidden evaluation

This remains mandatory.

The Red Team must **not** see the final hidden evaluation attack families.

For example:

```text
Development:
R1 R2 R3 R4 R5 R7

Hidden:
R8 R9 R10 R11
```

or hidden composite combinations.

This prevents us from simply optimizing against the benchmark.

---

# 5.37 Five mandatory experiments

### E1 — Static vs adaptive

```text
static Red
vs
adaptive Red
```

### E2 — Random vs intelligent

```text
random
vs
constraint-aware
vs
adaptive Pareto
```

### E3 — Known vs novel

```text
known attacks
vs
held-out attacks
vs
composite attacks
```

### E4 — Red-Team evolution

```text
Round 0
→ Round 1
→ Round 2
→ Round 3
```

### E5 — Attack modality

```text
transaction
graph
temporal
agentic
graph + agentic
```

---

# 5.38 Mandatory metrics

## Red Team

* Attack Success Rate
* Evasion Efficiency
* Fidelity
* Novelty
* Diversity
* Impact
* Attack Cost.

## Blue Team

* PR-AUC
* ROC-AUC
* precision
* recall
* F1
* false-positive rate
* calibration
* latency.

## Closed loop

* ASR before hardening
* ASR after hardening
* Blue recall before/after
* performance recovery
* forgetting rate
* attack rediscovery rate.

---

# 5.39 Final Step-5 acceptance criteria

Step 5 is considered operationally complete only when we can demonstrate:

| ID  | Acceptance requirement        |
| --- | ----------------------------- |
| R1  | 10 core attack families       |
| R2  | Synthetic-identity attack     |
| R3  | Attack grammar                |
| R4  | Composite attacks             |
| R5  | Mutability enforcement        |
| R6  | Temporal camouflage           |
| R7  | Behavioral camouflage         |
| R8  | Graph camouflage              |
| R9  | Multi-target graph injection  |
| R10 | Agentic intent drift          |
| R11 | Multi-agent coordination      |
| R12 | Authorization-context attack  |
| R13 | Stackelberg-style adaptation  |
| R14 | Adversarial motif memory      |
| R15 | NSGA-II attack optimization   |
| R16 | Counterfactual attacker       |
| R17 | Evasion Efficiency            |
| R18 | Fidelity measurement          |
| R19 | Novelty measurement           |
| R20 | Diversity measurement         |
| R21 | Hidden evaluation             |
| R22 | Blue-Team weakness dispatch   |
| R23 | Reproducible attack IDs/seeds |
| R24 | Simulation-only operation     |

---

# 5.40 Complete project flowchart — updated

This is now the **master flowchart** that we continue extending after every finalized step.

```text
┌──────────────────────────────────────────────────────────────┐
│ STEP 1 — REQUIREMENTS                                        │
│                                                              │
│ IDENTIFY → GENERATE → DEFEND                                │
│ Attack Diversity | Fidelity | Detection | Novelty |        │
│ Real-world Feasibility                                      │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 2 — COMPETITIVE INTELLIGENCE                            │
│                                                              │
│ Winning patterns | Research | Innovation gap | Benchmarking │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 3 — SYNTHETIC PAYMENT WORLD                            │
│                                                              │
│ Legitimate behavior                                          │
│ Hard negatives                                               │
│ Fraud scenarios                                              │
│ Dynamic heterogeneous graph                                  │
│ Agent entities                                               │
│ Temporal world                                               │
│ Hidden evaluation                                            │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 4 — BLUE TEAM                                           │
│                                                              │
│ GBDT Ensemble                                                │
│ Behavioral intelligence                                     │
│ Temporal intelligence                                       │
│ Graph intelligence                                          │
│ G-GBM / HOT-GNN / DynBERG experiments                       │
│ Temporal Motif Signatures                                   │
│ NSGA-II model optimization                                  │
│ Calibration                                                 │
│ Cost-sensitive Router                                       │
│ ALLOW / STEP-UP / BLOCK                                     │
│ SHAP + Evidence                                             │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
╔══════════════════════════════════════════════════════════════╗
║ STEP 5 — ADAPTIVE RED TEAM                                  ║
║                                                              ║
║ Attack Knowledge Base                                       ║
║         ↓                                                    ║
║ Attack Grammar                                               ║
║         ↓                                                    ║
║ Stackelberg Adversary                                       ║
║         ↓                                                    ║
║ ┌──────────────────────┬──────────────────────┐              ║
║ │ PAYMENT / GRAPH      │ AGENTIC              │              ║
║ │ STREAM               │ STREAM               │              ║
║ └──────────┬───────────┴──────────┬───────────┘              ║
║            ↓                      ↓                          ║
║       Mutation + Camouflage + Composition                    ║
║                       ↓                                      ║
║               Counterfactual Search                          ║
║                       ↓                                      ║
║              Mutability / Validity                           ║
║                       ↓                                      ║
║          Fidelity / Novelty / Diversity                      ║
║                       ↓                                      ║
║                 NSGA-II                                      ║
║                       ↓                                      ║
║                  BLUE TEAM                                   ║
║                   ↓     ↓                                    ║
║               CAUGHT    MISSED                               ║
║                         ↓                                    ║
║                 WEAKNESS STORE                               ║
║                         ↓                                    ║
║                 MOTIF MEMORY                                 ║
║                         ↓                                    ║
║                 NEXT ATTACK                                  ║
╚══════════════════════════════╤═══════════════════════════════╝
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 6 — CLOSED-LOOP CO-EVOLUTION                            │
│                                                              │
│ Replay Buffer | Prioritization | Retraining |                │
│ Continual Learning | Forgetting Protection | Stability      │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 7 — PROTOTYPE + EVIDENCE                               │
│                                                              │
│ Live simulation | Graph view | Attack Surface Map |         │
│ Red/Blue evolution | Metrics | Explainability | Demo        │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 8 — FINAL SUBMISSION                                   │
│                                                              │
│ Kaggle Writeup | TeamName.docx | Public GitHub | Prototype  │
│ Reproducibility | Evidence | Final presentation             │
└──────────────────────────────────────────────────────────────┘
```

---

# 5.41 Final competition audit

At the end of Step 5:

| Competition requirement          | Coverage                                                |
| -------------------------------- | ------------------------------------------------------- |
| Identify emerging GenAI fraud    | **Covered**                                             |
| Generate realistic attacks       | **Covered**                                             |
| Defend against generated attacks | **Covered through Step 4**                              |
| Attack diversity                 | **Strongly covered**                                    |
| Attack fidelity                  | **Strongly covered**                                    |
| Detection efficacy               | **Covered**                                             |
| Novelty                          | **Strongly covered**                                    |
| Real-world feasibility           | **Covered through constraints/budgets**                 |
| Closed-loop system               | **Architecture established; Step 6 operationalizes it** |
| Web prototype                    | **Step 7**                                              |
| Public GitHub                    | **Step 8**                                              |
| DOCX                             | **Step 8**                                              |
| Kaggle submission                | **Step 8**                                              |

One correction to the supplied audit: **Step 5 itself does not make the whole project "fully covered" yet.** The closed loop is architecturally defined, but the actual automated retraining/forgetting mechanism belongs to Step 6. Likewise, the web prototype and submission artifacts remain future deliverables. That distinction is important if we're going to be honest in the final documentation.

---

# 5.42 Final verdict

### Step 5 is now locked.

The final system is:

> **A constrained, multi-objective, adaptive Red Team that generates realistic payment, graph, temporal, synthetic-identity and agentic attacks; searches for Blue-Team blind spots; discovers minimal decision-boundary changes; remembers successful attack motifs; and evolves attacks using Blue-Team feedback.**

The six enhancements are now incorporated:

1. **NSGA-II for Blue-Team optimization** → Step 4/implementation.
2. **Evasion Efficiency** → Step 5 core metric.
3. **Frankenstein synthetic identity** → new R11.
4. **Temporal Motif Signatures** → Step 4 ↔ Step 5 adversarial capability.
5. **Counterfactual Attacker** → Step 5 core capability.
6. **Attack Surface Map** → Step 7 mandatory visualization.

And the most important thing is that we **didn't add complexity merely to sound advanced**. Each addition has a role in satisfying one of Mastercard's evaluation dimensions.

---

# Step 6
Yes. I reviewed the supplied **Step 6 v3.0 specification against the competition requirements, our previous Steps 1–5, and current 2026 literature**. I would **not lock the supplied version unchanged**. Its architecture is strong, but several claims are too absolute or technically over-specified for our situation.

The important correction is this:

> **We should lock the Step 6 architecture and evaluation framework, but keep implementation choices and numerical thresholds experimentally configurable.**

The supplied document already has the right overall structure—Red → Blue → failure analysis → replay → challenger → promotion gate → Red reseeding.

Below is the **finalized Step 6 specification** I recommend we actually use for the project.

---

# STEP 6 — CLOSED-LOOP CO-EVOLUTION & ACTIVE HARDENING

## Final Master Specification v4.0

### Project role of Step 6

Steps 1–5 established:

```text
STEP 3
Synthetic Payment World
        ↓
STEP 4
Blue Team
        ↓
STEP 5
Adaptive Red Team
```

Step 6 makes this system **self-hardening**:

```text
RED ATTACK
    ↓
BLUE DETECTION
    ↓
FAILURE ANALYSIS
    ↓
MEMORY
    ↓
BLUE ADAPTATION
    ↓
VALIDATION
    ↓
PROMOTION
    ↓
STRONGER BLUE
    ↓
RED ADAPTS
    ↓
NEW ATTACK
    ↓
...
```

This is the part that makes our solution a genuine **closed-loop red-team/blue-team system**, rather than a collection of independent models.

Recent research strongly supports the importance of this direction. GT-ACGL, published in *Scientific Reports* in July 2026, explicitly models fraud detection as a continual Stackelberg game with adversarial motif memory and addresses forgetting under strategic attack. ([Nature][1])

---

# 6.1 FINAL ARCHITECTURE

```text
                         ┌─────────────────────────────┐
                         │       STEP 5 RED TEAM       │
                         │                             │
                         │ Adaptive attack generation  │
                         │ NSGA-II                     │
                         │ Graph / temporal / agentic  │
                         │ Counterfactual attacks      │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │       BLUE CHAMPION         │
                         │                             │
                         │ GBDT + behavioral signals   │
                         │ graph signals               │
                         │ temporal signals            │
                         │ confidence / policy         │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │      FAILURE ANALYZER       │
                         │                             │
                         │ What failed?                │
                         │ Why did it fail?            │
                         │ Which signal was blind?     │
                         │ Which attack motif?         │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │    ZERO-TRUST MEMORY        │
                         │                             │
                         │ Provenance                  │
                         │ Validation                  │
                         │ Deduplication               │
                         │ Poisoning checks             │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │     PRIORITIZED REPLAY      │
                         │                             │
                         │ Historical fraud            │
                         │ Historical benign           │
                         │ New fraud                   │
                         │ Hard negatives              │
                         │ Boundary cases              │
                         │ Rare/novel motifs           │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │     BLUE CHALLENGER         │
                         │                             │
                         │ Replay                     │
                         │ Continual learning          │
                         │ Distillation candidate      │
                         │ EWC candidate               │
                         │ Calibration                 │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │      PROMOTION GATES        │
                         │                             │
                         │ New-threat improvement      │
                         │ Old-threat retention        │
                         │ OOD performance             │
                         │ Calibration                 │
                         │ Latency                     │
                         └──────────────┬──────────────┘
                                        │
                             ┌──────────┴──────────┐
                             ▼                     ▼
                           PASS                  FAIL
                             │                     │
                             ▼                     ▼
                      BLUE CHAMPION            ROLLBACK
                             │
                             ▼
                         STEP 5 RED
                         RE-GENERATION
                             │
                             └──────────► LOOP
```

---

# 6.2 Core principle: never blindly retrain

This is one of the most important decisions.

We will **not** implement:

```text
Red finds fraud
      ↓
append sample
      ↓
retrain model
```

That is too primitive.

Instead:

```text
Red finds weakness
      ↓
diagnose weakness
      ↓
validate sample
      ↓
assign priority
      ↓
insert into memory
      ↓
train Challenger
      ↓
test Challenger
      ↓
promote only if it passes
```

This gives us a controlled learning system.

---

# 6.3 Red/Blue co-evolution

We retain the Stackelberg/strategic formulation from the supplied specification.

Conceptually:

[
\max_{\theta_R}
U_R(\theta_R,\phi_B^*)
]

while:

[
\phi_B^*
========

\arg\min_{\phi_B}
L_B
]

The practical interpretation is:

> Red searches for weaknesses in the current Blue model; Blue learns from validated weaknesses; Red then attacks the improved Blue.

---

# 6.4 Historical attack mixture

A major improvement from the supplied specification is that Blue should not train exclusively against the **latest** Red attacks.

Otherwise we risk:

```text
Round 1:
Blue learns A

Round 2:
Blue learns B

Round 3:
Blue forgets A
```

Instead:

```text
Blue training =
recent attacks
+
historical attacks
+
legitimate anchors
+
hard negatives
+
rare motifs
```

This is the mechanism that gives us stability.

GT-ACGL independently uses historical adversarial motif memory to reduce this type of forgetting. Its reported forgetting reduction is benchmark-specific, however; we should not copy its ≤6-point result as though it were guaranteed for us. ([Nature][1])

---

# 6.5 Stability vs plasticity

We now explicitly measure two properties.

## Plasticity

Can Blue learn the new attack?

[
P =
\frac{1}{|K_{new}|}
\sum_{k}
(
PR\text{-}AUC_{after,k}
-----------------------

PR\text{-}AUC_{before,k}
)
]

Higher is better.

## Stability

Does Blue retain old knowledge?

[
F =
\frac{1}{|K_{old}|}
\sum_k
\max
(
0,
PR\text{-}AUC_{before,k}
------------------------

PR\text{-}AUC_{after,k}
)
]

Lower is better.

### Important correction

The supplied document hard-locks:

[
F\le0.06
]

because GT-ACGL reported a forgetting rate below six percentage points.

We **will not call 0.06 a universal requirement**.

Instead:

> **0.06 becomes an aspirational target / warning threshold initially.**

Our actual acceptance threshold will be determined after establishing the baseline.

That is scientifically cleaner.

---

# 6.6 Replay Memory

The replay buffer becomes one of the most important assets in the system.

It contains:

```text
┌───────────────────────────────┐
│        REPLAY MEMORY          │
├───────────────────────────────┤
│ Historical legitimate         │
│ Historical fraud              │
│ Recent legitimate             │
│ Recent fraud                  │
│ Red-Team successful evasions  │
│ Hard negatives                │
│ Boundary cases                │
│ Rare graph motifs             │
│ Novel/open-set cases          │
└───────────────────────────────┘
```

The exact percentages are **not frozen yet**.

The supplied proposal of:

* 30% benign anchors
* 20% historical fraud
* 20% live legitimate
* 20% evasions
* 10% rare

is a reasonable starting configuration.

But we'll tune it experimentally.

---

# 6.7 Prioritized replay

Every sample receives a priority:

[
P_i =
w_HH_i+
w_NN_i+
w_BB_i+
w_RR_i
]

where:

* (H) = hardness
* (N) = novelty
* (B) = boundary proximity
* (R) = rarity

This means a rare attack that barely fooled the model can receive higher replay priority than thousands of obvious fraud samples.

---

# 6.8 Boundary examples

These are particularly valuable.

Suppose:

```text
fraud probability = 0.49
```

and:

```text
fraud probability = 0.51
```

These are far more informative for decision-boundary learning than:

```text
0.001
```

or:

```text
0.999
```

Therefore boundary cases become a dedicated replay category.

---

# 6.9 Zero-Trust Replay Buffer

This is an enhancement I **do want to retain**, but with a correction.

The supplied specification proposes:

```text
HMAC provenance
+
Cook's Distance
+
domain-state validation
```

### We keep:

**Provenance**

Every generated sample gets:

```text
attack_id
generator_version
seed
parent_attack
mutation_history
timestamp
fidelity_score
novelty_score
```

and a cryptographic provenance token.

### But:

HMAC proves **origin/authenticity under a protected key**.

It does **not** prove that the generated example is semantically correct or non-poisonous.

Therefore:

```text
HMAC
≠
anti-poisoning by itself
```

We also need validation.

---

# 6.10 Replay validation pipeline

```text
Generated sample
       ↓
Schema validation
       ↓
Generator provenance
       ↓
Duplicate detection
       ↓
Fidelity check
       ↓
Label consistency
       ↓
Influence/outlier check
       ↓
Distribution sanity check
       ↓
Domain-state validation
       ↓
ACCEPT / QUARANTINE
```

This is stronger than simply signing samples.

---

# 6.11 Cook's Distance — downgraded from mandatory

The supplied specification makes Cook's Distance a hard component.

I don't recommend that.

Cook's Distance is traditionally an influence diagnostic in regression. It may be useful as an **experimental influence diagnostic**, but it is not a universal solution for detecting poisoned high-dimensional fraud samples.

So:

> **Influence analysis stays; Cook's Distance becomes one candidate technique rather than a mandatory dependency.**

We can compare:

* Cook's Distance,
* robust distance,
* embedding-space outlier detection,
* nearest-neighbor inconsistency.

---

# 6.12 Open-set fraud detection

This is an important addition.

Blue shouldn't only answer:

```text
fraud
/
legitimate
```

It should also be able to say:

> **"This does not look sufficiently like the attack families I know."**

That is the open-set problem.

The supplied specification proposes SCALE-style adaptive prototypes.

Recent 2026 work on SCALE specifically addresses open-set unknown financial fraud using adaptive heterogeneous graph prototype learning. ([EurekaMag][2])

We therefore retain:

```text
known fraud
known legitimate
unknown / novel
```

as a conceptual third state.

---

# 6.13 Open-set pathway

```text
Transaction
    ↓
Known-model score
    ↓
Prototype distance
    ↓
Graph novelty
    ↓
Temporal novelty
    ↓
┌───────────────┬──────────────────┐
│ Known         │ Unknown          │
│ pattern       │ pattern          │
└───────┬───────┴─────────┬────────┘
        ↓                 ↓
 normal detection    analyst / step-up
                     + Red investigation
```

This directly supports our "novel fraud" objective.

---

# 6.14 Drift detection

We retain automated drift detection.

But we should monitor multiple types:

### Feature drift

[
P_t(X)\neq P_{t-1}(X)
]

### Label/concept drift

[
P_t(Y|X)\neq P_{t-1}(Y|X)
]

### Graph drift

Changes in:

* degree distribution,
* communities,
* edge types,
* motifs.

### Temporal drift

Changes in:

* transaction intervals,
* active hours,
* burst duration,
* fraud persistence.

---

# 6.15 ADWIN

ADWIN remains a candidate/primary streaming detector.

It can trigger adaptation when a monitored statistic changes significantly.

But again:

> **ADWIN does not become a sacred requirement.**

We will compare its behavior with simpler distribution tests where appropriate.

The supplied specification's idea of replacing arbitrary cron-based retraining with statistically triggered adaptation is correct.

---

# 6.16 Failure taxonomy

The 12-category taxonomy is retained.

| Code | Failure                        |
| ---- | ------------------------------ |
| W1   | Micro-velocity blindness       |
| W2   | Temporal camouflage            |
| W3   | Relational camouflage          |
| W4   | Device-farm masking            |
| W5   | Collusive merchant behavior    |
| W6   | Synthetic identity             |
| W7   | Agentic intent drift           |
| W8   | Multi-agent smurfing           |
| W9   | Authorization/context mismatch |
| W10  | Calibration failure            |
| W11  | Distribution drift             |
| W12  | Open-set novel topology        |

This taxonomy becomes a bridge between:

**Red Team → Failure Analysis → Blue adaptation.**

The supplied specification already formalizes this mapping.

---

# 6.17 Failure → remediation

We should not retrain everything for every failure.

| Failure | Preferred response                         |
| ------- | ------------------------------------------ |
| W1      | Update velocity features                   |
| W2      | Update temporal features                   |
| W3      | Strengthen graph representation            |
| W4      | Update device relationship features        |
| W5      | Update merchant concentration signals      |
| W6      | Update identity consistency signals        |
| W7      | Update intent/context signals              |
| W8      | Update cross-entity coordination features  |
| W9      | Update authorization context               |
| W10     | Recalibrate                                |
| W11     | Drift adaptation/retrain                   |
| W12     | Open-set investigation + new attack family |

This is a major architectural advantage.

---

# 6.18 Continual-learning engine

The supplied specification uses:

[
L_{total}
=========

L_{BCE}
+
\lambda_{distill}D_{KL}
+
L_{EWC}
]

We retain this **as the candidate hybrid objective**.

But we do not blindly assume that:

```text
Replay + Distillation + EWC
```

is automatically better.

We must compare:

### A

```text
Normal retraining
```

### B

```text
Replay
```

### C

```text
Replay + distillation
```

### D

```text
Replay + EWC
```

### E

```text
Replay + distillation + EWC
```

Then keep the simplest configuration that wins.

---

# 6.19 Why this matters

We don't want to build a system with five sophisticated techniques and discover:

```text
simple replay
>
replay + EWC + distillation
```

That would be unnecessary complexity.

Our project principle remains:

> **Evidence before architecture.**

---

# 6.20 Generative replay

The supplied specification proposes STG-DGR / diffusion-based replay.

This is legitimate research.

STG-DGR was published at the ACM Web Conference 2026 and specifically addresses catastrophic forgetting in streaming transaction graphs through diffusion-based generative replay. ([DOI][3])

However, one correction is essential:

### Do NOT claim:

> "STG-DGR gives us O(1) memory."

The paper says it generates synthetic replay rather than storing all historical real samples; that is **not equivalent to the entire system having mathematically O(1) memory**. ([DOI][3])

So our specification will say:

> **Generative replay is an advanced memory-efficiency option.**

Not a guaranteed O(1) implementation.

---

# 6.21 Implementation hierarchy

This is what I recommend:

### Level 1 — Mandatory

```text
Prioritized replay
```

### Level 2 — Strong enhancement

```text
Replay + distillation/EWC
```

### Level 3 — Advanced

```text
Generative replay
```

### Level 4 — Research showcase

```text
Graph-aware generative replay
```

We only move upward if the lower level has been validated.

---

# 6.22 Champion / Challenger

This is now mandatory.

```text
BLUE CHAMPION
      │
      ├── production candidate
      │
      ▼
BLUE CHALLENGER
      │
      ├── trained on new knowledge
      │
      ▼
VALIDATION
```

The Challenger replaces Champion **only after passing every gate**.

---

# 6.23 Final promotion gate

The supplied document contains five gates.

We retain the five dimensions but make thresholds configurable.

## Gate 1 — New-threat improvement

Did the Challenger improve on newly discovered attacks?

## Gate 2 — Forgetting

Did old fraud performance remain acceptable?

## Gate 3 — OOD transfer

Does improvement transfer to unseen attack distributions?

## Gate 4 — Calibration

Are probabilities still reliable?

## Gate 5 — Latency

Can the model still operate within the intended inference budget?

---

# 6.24 Why I am removing the hard-coded +0.12 PR-AUC requirement

The supplied document says:

[
PR\text{-}AUC\ Gain\ge0.12
]

But that's too arbitrary.

A 0.12 PR-AUC improvement might be huge in one setting and impossible in another.

Instead:

> **We will define the promotion threshold relative to the baseline and uncertainty of our own validation experiment.**

For example:

```text
meaningful improvement
+
statistical stability
+
no unacceptable regression
```

The exact number is locked **after Step 7 experiments**, not before.

---

# 6.25 OOD transfer

This remains one of the strongest components.

The system must demonstrate:

```text
TRAIN
known attacks
      ↓
CO-EVOLUTION
      ↓
TEST
unseen attack structures
```

This is the most important defense against self-confirmation.

---

# 6.26 Tri-split anti-circularity

The supplied specification's three-way concept is retained.

But we need to fix one issue:

It proposes:

> real-world reference sets such as BAF and IEEE-CIS.

These can be useful **external evaluation references**, but they cannot automatically be assumed to be available, licensed for every use, or representative of Mastercard's environment.

Therefore:

### Split A — Co-evolution arena

Our synthetic world.

### Split B — Drifted synthetic world

New correlations, graph structures, temporal distributions.

### Split C — External benchmark evaluation

Only datasets whose access/licensing and preprocessing we verify.

This is a **validation benchmark**, not our training world.

---

# 6.27 The crucial anti-self-confirmation mechanism

This is one of the strongest additions to the project.

We need:

```text
Synthetic World A
        ↓
Red/Blue training
        ↓
Synthetic World B
different parameters
        ↓
evaluation
        ↓
External benchmark
        ↓
evaluation
```

If:

```text
A = excellent
B = excellent
C = reasonable
```

then our argument becomes much stronger.

If:

```text
A = excellent
B = terrible
```

then we know we overfit our simulator.

That honesty will actually improve the credibility of the project.

---

# 6.28 External benchmark caution

We are **not** going to claim:

> "Mastercard's real fraud data."

We don't have it.

We will say:

> **"Our synthetic payment world is designed from publicly documented fraud/payment distributions and evaluated against external reference datasets where legally and technically appropriate."**

That's defensible.

---

# 6.29 New addition — attack-independent holdout

This is even stronger than simply holding out attack labels.

We should create:

```text
HOLDOUT A
unseen attack family

HOLDOUT B
known family + unseen composition

HOLDOUT C
known family + unseen temporal behavior

HOLDOUT D
known family + unseen graph topology

HOLDOUT E
agentic + transaction hybrid
```

This tests different forms of generalization.

---

# 6.30 New addition — seed-independent evaluation

Red and Blue should not repeatedly see identical random seeds.

We should use:

```text
Training seeds
Evaluation seeds
Hidden seeds
```

separately.

Otherwise the generator may accidentally memorize its own randomness.

---

# 6.31 New addition — attack lineage tracking

Every attack gets:

```text
Attack ID
Parent ID
Generation
Mutation sequence
Generator version
Seed
Attack family
Composite family
Fidelity
Novelty
Evasion
Cost
Blue response
```

Then we can reconstruct:

```text
Attack A
   ↓
Mutation 1
   ↓
Attack B
   ↓
Mutation 2
   ↓
Attack C
```

This will become extremely useful in the final UI.

---

# 6.32 New addition — model lineage

Same for Blue:

```text
BLUE_001
   ↓
trained on attacks 1–100
   ↓
BLUE_002
   ↓
trained on attacks 1–150
   ↓
BLUE_003
```

We can then reproduce:

> "Exactly why did Blue_003 improve?"

This is essential for a serious technical project.

---

# 6.33 New metric — Recovery Gain

Retained.

[
RecoveryGain =
ASR_{before}-ASR_{after}
]

Example:

```text
Before:
ASR = 42%

After:
ASR = 14%

Recovery Gain = 28 percentage points
```

This is a very strong demo metric.

---

# 6.34 New metric — Adaptation Cost

Measure:

* CPU time,
* GPU time,
* memory,
* training samples,
* retraining duration.

Then:

[
AdaptationEfficiency
====================

\frac{PerformanceGain}{AdaptationCost}
]

This helps satisfy Mastercard's **real-world feasibility** criterion.

---

# 6.35 New metric — Robustness Retention

[
RR=
\frac{Performance_{old,after}}
{Performance_{old,before}}
]

Target:

[
RR\approx1
]

while new-threat performance improves.

---

# 6.36 New metric — Attack Rediscovery

This is another useful addition.

Suppose Red discovers Attack A.

Blue learns it.

Then Red later rediscovers a variation of A.

Measure:

[
RediscoveryRate
]

This tells us whether our Red generator is actually exploring new attack space or repeatedly rediscovering the same patterns.

---

# 6.37 New metric — Evolutionary Novelty

Measure novelty across successive generations:

[
Novelty_t
=========

Distance(A_t,A_{1:t-1})
]

Then visualize:

```text
Generation
    ↓
Novelty
```

If novelty collapses, our Red Team is stagnating.

---

# 6.38 New metric — Defense Saturation

At some point:

```text
Blue improves
↓
Blue improves
↓
Blue improves
↓
improvement ≈ 0
```

We track:

[
\Delta BluePerformance
]

across cycles.

This tells us whether the system is approaching a stable frontier.

---

# 6.39 The co-evolution scoreboard

This should eventually be visible in the prototype:

| Round | Blue Recall | Red ASR | Fidelity | Novelty | Forgetting |
| ----: | ----------: | ------: | -------: | ------: | ---------: |
|     0 |           — |       — |        — |       — |          — |
|     1 |           ↑ |       ↓ |        — |       ↑ |          — |
|     2 |           ↑ |       ↓ |        — |       ↑ |          — |
|     3 |           ↑ |       ↓ |        — |       ↑ |          — |

This gives judges a **story**, not just a model score.

---

# 6.40 RAG Evidence Verifier — corrected role

The supplied specification adds an LLM/RAG evidence verifier.

I recommend keeping this, but **not inside the primary transaction scoring path**.

Why?

Because an LLM/RAG call in every payment decision would create:

* latency,
* reliability,
* operational complexity,
* hallucination risk.

Instead:

```text
Primary detector
      ↓
high confidence → decision
      ↓
borderline case
      ↓
Evidence / investigator layer
```

This is much more realistic.

---

# 6.41 Research correction: RAG result

The supplied document says:

> FPR from 17.2% to 3.5%.

The underlying 2026 paper does indeed report the RAG-enhanced fraud detection reducing false positives from **17.2% to 3.5%**. ([Research Trend][4])

One version of the indexed text contains a typo saying "to 35%," but the paper's reported value is 3.5%. ([ResearchGate][5])

So:

> **3.5% is the figure we should use if we cite that result, with attribution to the paper—not as a guarantee for our system.**

---

# 6.42 RAG's actual job

It should provide:

```text
Risk evidence
+
SHAP explanation
+
historical attack context
+
policy context
+
investigator summary
```

For example:

> "High risk because the device is newly associated with three accounts, transaction velocity increased 4.2×, and the temporal motif resembles a previously observed coordinated attack."

That's much more useful than:

> "Fraud probability = 0.93."

---

# 6.43 ORACLE-style trajectory modeling

The supplied specification proposes ORACLE for multi-session trajectories.

We retain **multi-session trajectory intelligence as a candidate**, but not as a mandatory dependency until the actual paper and reproducibility are confirmed sufficiently.

The capability we want is:

```text
transaction 1
 ↓
transaction 2
 ↓
login
 ↓
device change
 ↓
merchant interaction
 ↓
transaction 3
```

rather than looking at each transaction independently.

That is valuable regardless of whether we use the exact ORACLE architecture.

---

# 6.44 Agentic Red-Team integration

Step 5 already contains agentic attacks.

Step 6 now allows Blue to learn from them:

```text
Agentic intent drift
        ↓
failure
        ↓
intent-context replay
        ↓
Blue challenger
        ↓
validation
        ↓
new Blue
```

This closes the loop for one of our strongest differentiators.

---

# 6.45 Final Step 6 experimental program

We should eventually run:

### E1 — Static vs continual

```text
Static Blue
vs
Continual Blue
```

### E2 — Fine-tuning vs replay

```text
Fine-tuning
vs
Replay
```

### E3 — Replay vs hybrid

```text
Replay
vs
Replay + distillation
vs
Replay + EWC
```

### E4 — Static Red vs adaptive Red

### E5 — No hidden set vs hidden set

### E6 — Known vs unseen attacks

### E7 — Normal vs drifted simulator

### E8 — Graph attacks

### E9 — Agentic attacks

### E10 — Composite attacks

### E11 — Replay poisoning resistance

### E12 — Generative replay

Only the results decide which techniques survive into the final architecture.

---

# 6.46 Step 6 acceptance criteria

The final system should satisfy:

| ID  | Requirement                          | Status                      |
| --- | ------------------------------------ | --------------------------- |
| C1  | Red failures enter structured memory | **LOCKED**                  |
| C2  | Prioritized replay                   | **LOCKED**                  |
| C3  | Historical benign anchors            | **LOCKED**                  |
| C4  | Historical fraud retention           | **LOCKED**                  |
| C5  | Hard-negative retention              | **LOCKED**                  |
| C6  | Novel attack retention               | **LOCKED**                  |
| C7  | Failure taxonomy                     | **LOCKED**                  |
| C8  | Drift monitoring                     | **LOCKED**                  |
| C9  | Continual adaptation                 | **LOCKED**                  |
| C10 | Forgetting measurement               | **LOCKED**                  |
| C11 | Plasticity measurement               | **LOCKED**                  |
| C12 | Champion/Challenger                  | **LOCKED**                  |
| C13 | Hidden evaluation                    | **LOCKED**                  |
| C14 | Attack provenance                    | **LOCKED**                  |
| C15 | Model lineage                        | **LOCKED**                  |
| C16 | Replay integrity                     | **LOCKED**                  |
| C17 | Red regeneration                     | **LOCKED**                  |
| C18 | Recovery Gain                        | **LOCKED**                  |
| C19 | Adaptation Cost                      | **LOCKED**                  |
| C20 | Robustness Retention                 | **LOCKED**                  |
| C21 | OOD evaluation                       | **LOCKED**                  |
| C22 | Seed-independent evaluation          | **LOCKED**                  |
| C23 | Attack lineage                       | **LOCKED**                  |
| C24 | Evolutionary novelty                 | **LOCKED**                  |
| C25 | Defense saturation                   | **LOCKED**                  |
| C26 | Open-set pathway                     | **LOCKED**                  |
| C27 | External benchmark evaluation        | **CONDITIONAL**             |
| C28 | Generative replay                    | **OPTIONAL/EXPERIMENTAL**   |
| C29 | RAG evidence layer                   | **OPTIONAL/SECONDARY PATH** |
| C30 | Exact continual-learning algorithm   | **EXPERIMENTAL**            |

---

# 6.47 What we are deliberately NOT locking

This is critical.

We are **not** yet locking:

* exact RAM requirements,
* GPU requirements,
* exact model sizes,
* exact GNN architecture,
* exact replay percentage,
* exact drift threshold,
* exact forgetting threshold,
* exact NSGA-II population,
* exact number of co-evolution rounds,
* exact EWC coefficient,
* exact distillation coefficient,
* exact generative replay model,
* exact RAG model,
* exact latency target.

Those depend on the machine and execution environment.

---

# 6.48 Final Step 6 flow

```text
                STEP 5
            ADAPTIVE RED
                 │
                 ▼
          BLUE CHAMPION
                 │
                 ▼
          FAILURE ANALYSIS
                 │
                 ▼
        ZERO-TRUST VALIDATION
                 │
                 ▼
        PRIORITIZED MEMORY
                 │
                 ▼
        BLUE CHALLENGER
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
     NEW       OLD       OOD
   THREATS    THREATS   THREATS
       │         │         │
       └─────────┼─────────┘
                 ▼
           CALIBRATION
                 ▼
             LATENCY
                 ▼
        CHAMPION / ROLLBACK
                 │
                 ▼
           UPDATED BLUE
                 │
                 ▼
          ADAPTIVE RED
                 │
                 └──────────────► NEXT ROUND
```

---

# 6.49 Updated master project flow

We now have:

```text
┌──────────────────────────────────────────────┐
│ STEP 1 — REQUIREMENTS                        │
│ Mastercard problem + judging criteria        │
└──────────────────────┬───────────────────────┘
                       ▼
┌──────────────────────────────────────────────┐
│ STEP 2 — COMPETITIVE INTELLIGENCE            │
│ Research + competitors + innovation gaps     │
└──────────────────────┬───────────────────────┘
                       ▼
┌──────────────────────────────────────────────┐
│ STEP 3 — SYNTHETIC PAYMENT WORLD             │
│ Customers + merchants + devices + graph      │
│ transactions + temporal behavior + agents    │
└──────────────────────┬───────────────────────┘
                       ▼
┌──────────────────────────────────────────────┐
│ STEP 4 — BLUE TEAM                            │
│ GBDT + behavioral + temporal + graph         │
│ calibration + router + explainability        │
└──────────────────────┬───────────────────────┘
                       ▼
┌──────────────────────────────────────────────┐
│ STEP 5 — ADAPTIVE RED TEAM                   │
│ Attack grammar + mutation + graph + agentic │
│ NSGA-II + counterfactual + novelty          │
└──────────────────────┬───────────────────────┘
                       ▼
╔══════════════════════════════════════════════╗
║ STEP 6 — CLOSED-LOOP CO-EVOLUTION            ║
║                                              ║
║ RED                                       ║
║  ↓                                           ║
║ BLUE                                         ║
║  ↓                                           ║
║ FAILURE ANALYSIS                             ║
║  ↓                                           ║
║ ZERO-TRUST REPLAY                            ║
║  ↓                                           ║
║ PRIORITIZED MEMORY                           ║
║  ↓                                           ║
║ BLUE CHALLENGER                              ║
║  ↓                                           ║
║ NEW + OLD + OOD TEST                         ║
║  ↓                                           ║
║ PROMOTION / ROLLBACK                         ║
║  ↓                                           ║
║ UPDATED BLUE                                 ║
║  ↓                                           ║
║ ADAPTIVE RED                                 ║
║  └──────────────────────────────► LOOP       ║
╚══════════════════════╤═══════════════════════╝
                       ▼
┌──────────────────────────────────────────────┐
│ STEP 7 — PROTOTYPE + EVIDENCE                │
│ Interactive Red/Blue laboratory              │
│ Attack Surface Map                           │
│ Co-evolution scoreboard                      │
│ Graph visualization                          │
│ Explainability                               │
│ Experiments + benchmark evidence             │
└──────────────────────┬───────────────────────┘
                       ▼
┌──────────────────────────────────────────────┐
│ STEP 8 — FINAL SUBMISSION                    │
│ Kaggle Writeup                               │
│ TeamName.docx                                │
│ Public GitHub                                │
│ Reproducibility + final evidence             │
└──────────────────────────────────────────────┘
```

---

# 6.50 Final assessment of the supplied Step 6

### What I kept

The supplied document's strongest ideas are retained:

* PSRO/Stackelberg co-play
* prioritized replay
* zero-trust memory
* drift-triggered adaptation
* stability/plasticity
* continual learning
* Champion/Challenger
* OOD validation
* open-set fraud
* generative replay
* RAG evidence
* Red regeneration
* attack/model lineage

The core pipeline is sound.

### What I corrected

I specifically removed or softened claims that were too strong:

* **"mathematically certified"** → removed.
* **F ≤ 0.06 as universal requirement** → changed to target/experimental threshold.
* **PR-AUC gain ≥ 0.12** → removed as arbitrary hard gate.
* **Gamma OOD ≥ 0.75** → experimental threshold.
* **P99 < 4.5 ms** → depends on our actual hardware and deployment design.
* **STG-DGR = O(1) memory** → corrected.
* **HMAC = anti-poisoning** → corrected to provenance/authenticity.
* **Cook's Distance mandatory** → changed to candidate influence diagnostic.
* **RAG in real-time primary path** → moved to secondary investigator/evidence path.
* External datasets → **evaluation references, not assumed training data**.

These corrections make the project **more credible**, not less ambitious.

---

# 6.51 One additional thing I would add

There is one concept I think is worth explicitly locking because it makes the whole project substantially more defensible:

## **External Reality Anchor**

Our simulator is ultimately our own creation.

Therefore:

> **The simulator cannot be the only judge of whether our simulator is realistic.**

Step 7 should therefore contain an **External Reality Anchor layer**:

```text
Our Synthetic World
        ↓
Compare against
        ↓
Public fraud/payment datasets
+
Published fraud statistics
+
Known behavioral distributions
+
Research benchmarks
```

This doesn't mean training on those datasets.

It means using them to challenge our assumptions.

That is the cleanest answer to the biggest weakness of a self-generated dataset.

---

# Step 7
Yes. I reviewed the additional Step 7 specification you attached, and I would **not simply append it unchanged**. It contains several strong additions, but also several claims and implementation commitments that are too absolute for a two-person, four-day, free-compute project.

The attached specification is useful as a source because it adds concrete contracts, gates, task ownership, and an anti-circularity evaluation design. For example, it formalizes the six-stage loop and the Red/Blue interfaces. 

I also re-checked the important external claims. Mastercard really did introduce Verifiable Intent in March 2026 and describes it as a standards-based, privacy-preserving trust layer connecting authorization, intent and action. ([Mastercard][1]) Mastercard also launched Agent Pay for Machines in June 2026 for high-frequency, machine-driven payments with credentialing, permissioning and settlement. ([Mastercard][2]) MonTi and FRAUD-RLA are real research, and GT-ACGL is a July 2026 Scientific Reports paper. ([GitHub][3]) STG-DGR is also a real WWW 2026 paper. ([DOI][4])

But some numbers in the attached specification are **research results or proposed targets, not facts about our future system**. For example, GT-ACGL reports below-6-percentage-point forgetting on its evaluated benchmarks; that does **not** justify promising our system will achieve `<6%`. ([Nature][5]) Likewise, `<4.5 ms P99`, `ASR drop ≥25%`, `ECE ≤0.04`, `1M rows`, and particular Kaggle GPU configurations must be **measured project targets**, not pre-declared achievements.

With that correction, here is the **actual final Step 7** I would lock.

---

STEP 7 — FINAL MASTER SPECIFICATION v2.0
Cloud-Orchestrated Implementation, Adaptive Red/Blue Co-Evolution, Evaluation Gates, Reproducibility & Offline Prototype
Status: FINALIZED FOR EXECUTION
Purpose

This version combines:

the latest finalized Step 7,
the missing useful engineering components from the older Step 7,
the strongest closed-loop mechanisms from Step 6,
the realistic compute constraints,
the prototype requirements,
the claim/evidence system,
and the additional five corrections identified in the audit.

It deliberately does not turn every research idea into a mandatory implementation requirement.

1. MISSION

We are building:

Mastercard AI Defense Lab for Payment Security

A controlled adversarial payment-security laboratory that continuously:

IDENTIFY
   ↓
GENERATE
   ↓
ATTACK
   ↓
DETECT
   ↓
EXPLAIN
   ↓
HARDEN
   ↓
RE-ATTACK
   ↓
MEASURE
   ↓
EVOLVE

The objective is not to win by having the largest technology stack.

The objective is to demonstrate:

A realistic adaptive attacker can discover weaknesses in a payment-defense system, those failures can be diagnosed and retained, and subsequent defensive versions can measurably become harder to defeat without unacceptable legitimate-customer degradation.

This is the central project thesis.

2. CORE INNOVATION THESIS

Traditional fraud detection primarily asks:

“Does this transaction look fraudulent?”

Our system asks:

“Can a realistic adaptive attacker defeat the current defense, why did it succeed, and can the next defense become measurably harder to defeat?”

The system therefore contains:

Red Team

Attempts to discover realistic, high-fidelity attacks.

Blue Team

Attempts to detect and mitigate those attacks while controlling legitimate-customer friction.

Closed Loop
Blue failure
    ↓
Failure diagnosis
    ↓
Replay / memory
    ↓
Red adaptation
    ↓
Harder attacks
    ↓
Blue challenger
    ↓
Promotion gate
    ↓
New champion
    ↓
Red attacks again

The failure itself becomes reusable evaluation material.

3. SIX-STAGE PROJECT NARRATIVE

The project narrative remains:

1. IDENTIFY

Map emerging attack families and payment-security surfaces.

2. GENERATE

Generate realistic constrained attack instances.

3. DEFEND

Detect and mitigate them.

4. EXPLAIN

Determine why the system detected or missed an attack.

5. HARDEN

Train/test a challenger against the discovered weakness.

6. EVOLVE

Allow the Red Team to challenge the new champion.

This six-stage structure is explicitly retained from the older specification.

4. MASTER CLOSED-LOOP ARCHITECTURE
                    ┌────────────────────────────┐
                    │    THREAT INTELLIGENCE     │
                    │                            │
                    │ Attack taxonomy            │
                    │ Payment surfaces           │
                    │ Agentic threats             │
                    │ Graph threats               │
                    │ Temporal threats            │
                    │ Behavioral threats          │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │   SYNTHETIC PAYMENT WORLD  │
                    │                            │
                    │ Customers                  │
                    │ Accounts                   │
                    │ Merchants                  │
                    │ Devices                    │
                    │ IP / geography              │
                    │ Transactions               │
                    │ Tokens / credentials       │
                    │ Agents                     │
                    │ Intent / authorization     │
                    └─────────────┬──────────────┘
                                  │
                ┌─────────────────┴──────────────────┐
                ▼                                    ▼
       ┌────────────────┐                  ┌────────────────┐
       │   BLUE TEAM    │                  │    RED TEAM    │
       │                │                  │                │
       │ GBDT           │                  │ Attack Grammar │
       │ Behavioral     │                  │ Mutation       │
       │ Temporal       │                  │ NSGA-II        │
       │ Relational     │                  │ Graph attacks  │
       │ Intent         │                  │ RL optional    │
       │ Calibration    │                  │ PSRO optional  │
       │ Decision       │                  │                │
       └───────┬────────┘                  └───────┬────────┘
               │                                   │
               └────────────────┬──────────────────┘
                                ▼
                    ┌────────────────────────────┐
                    │    ATTACK EVALUATION       │
                    │                            │
                    │ Evasion                    │
                    │ Fidelity                   │
                    │ Novelty                    │
                    │ Coverage                   │
                    │ Cost                       │
                    │ Realism                    │
                    └─────────────┬──────────────┘
                                  ▼
                    ┌────────────────────────────┐
                    │     FAILURE ANALYZER        │
                    │                            │
                    │ Why did Blue miss?         │
                    │ Failure category            │
                    │ Feature weakness            │
                    │ Boundary proximity          │
                    └─────────────┬──────────────┘
                                  ▼
                    ┌────────────────────────────┐
                    │       REPLAY MEMORY         │
                    │                            │
                    │ Hard failures               │
                    │ Historical attacks          │
                    │ Benign anchors              │
                    │ Novel motifs                │
                    │ Provenance                  │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────┴──────────────┐
                    ▼                            ▼
            RED ADAPTATION                BLUE CHALLENGER
                    │                            │
                    │                    Retrain / calibrate
                    │                    Regression testing
                    │                            │
                    └─────────────┬──────────────┘
                                  ▼
                    ┌────────────────────────────┐
                    │    PROMOTION GATES          │
                    │                            │
                    │ Detection                  │
                    │ Robustness                 │
                    │ Calibration                │
                    │ Forgetting                 │
                    │ Latency                    │
                    │ Cost                       │
                    └─────────────┬──────────────┘
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                     CHAMPION           ROLLBACK
                         │
                         ▼
                    RED ATTACKS AGAIN
5. MASTERCARD-SPECIFIC DIFFERENTIATOR

The project retains agentic payment security as its flagship emerging threat surface.

Mastercard's current direction around Verifiable Intent and Agent Pay for Machines makes the problem materially relevant: determining whether an AI agent's eventual action remains consistent with what the user authorized is a real emerging security problem.

We therefore model:

USER AUTHORIZATION
        ↓
DECLARED INTENT
        ↓
AGENT PLAN
        ↓
ACTUAL ACTION
        ↓
TRANSACTION
        ↓
INTENT DIVERGENCE?

Example:

User authorization:

"Buy office stationery under ₹5,000."

        ↓

Agent:
Authorized ✓

        ↓

Transaction:
₹18,000 digital gift cards

        ↓

Authorization:
Valid

        ↓

Semantic intent:
MISMATCH

We explicitly state:

This is our research/prototype mechanism inspired by the problem Mastercard is addressing.

We do not claim that intent_drift_score is Mastercard's production scoring mechanism.

The older Step 7 correctly makes this distinction.

6. INTENT-DRIFT ENGINE

The prototype calculates:

Declared / Authorized Intent
            ↓
Expected Action
            ↓
Actual Transaction
            ↓
Intent Divergence
            ↓
intent_drift_score

Potential signals:

MCC mismatch
amount deviation
merchant deviation
geography deviation
temporal deviation
product/category deviation
spending-limit violation
sequence deviation
unusual frequency
agent-permission mismatch.

The feature is tested through ablation:

Transaction-only
       vs
Transaction + Intent

on controlled intent-drift attacks.

7. SYNTHETIC PAYMENT WORLD

The project owns the simulation environment.

The simulator creates:

Entities
Customers
Accounts
Merchants
Devices
IP / geography
Tokens / credentials
Agents
Events
Transactions
Authentication attempts
Device changes
Account changes
Agent actions
Merchant interactions
Authorization events
Stateful variables
Balance
Available credit
Velocity
Failed authentication count
Known devices
Active tokens
Merchant relationships
Agent permissions
Historical behavior

The key principle remains:

Legitimate behavior is generated first. Fraud is an intervention into that world.

This prevents the project from becoming merely:

random rows
+
fraud labels
+
classifier
8. HARD NEGATIVES

Hard negatives are mandatory.

Examples:

Traveler
Flash-sale shopper
Shared family device
B2B month-end payments
Large legitimate purchase
New device after travel
Legitimate repetitive agent purchases
Unusual but legitimate geography

The detector must distinguish:

UNUSUAL

from:

FRAUDULENT

This is important for customer-friction control.

9. ATTACK-SURFACE COVERAGE MATRIX

This is the major addition I am explicitly locking after the audit.

Attack diversity alone is insufficient.

Every attack is categorized across:

Attack Family
       ×
Payment Channel / Rail
       ×
Attack Mechanism
       ×
Temporal Pattern
       ×
Coordination Level
       ×
Agentic Context
Example attack families
Identity fraud
Account takeover
Social engineering
AI impersonation
Transaction manipulation
Automated fraud
Coordinated fraud
Device/network abuse
Merchant abuse
Synthetic identity
Graph manipulation
Agentic payment abuse
Example surfaces
Card-not-present
E-commerce
Mobile commerce
Wallet/tokenized payments
Recurring payments
P2P
Account-to-account
Cross-border
Microtransactions
Machine-to-machine
Agent-to-merchant
Agent-to-agent
Coverage metric
Attack Coverage =
covered defined surface cells
/
total defined surface cells

This directly converts “broad attack coverage” into something measurable.

10. DATA-GENERATION QUALITY

Synthetic realism must be measured.

Distribution tests
KS statistic
Wasserstein distance where appropriate
categorical divergence.
Correlation/dependency
correlation matrix comparison
dependency structure comparison.
Temporal
inter-arrival distributions
velocity
burst characteristics.
Graph
degree distribution
clustering
component structure
motif statistics.
Privacy
nearest-neighbor/DCR-style analysis
memorization checks.

Thresholds are configuration parameters, not invented facts.

11. EXTERNAL REALITY ANCHOR

This is retained and upgraded to a mandatory evaluation layer.

Our simulator cannot prove its own realism.

Therefore:

OUR SYNTHETIC WORLD
        ↓
EXTERNAL REALITY ANCHOR
        ↓
Public fraud/payment datasets
Published fraud statistics
Known behavioral distributions
Research benchmarks

External datasets are used for:

calibration,
sanity checks,
plausibility,
external validation where possible.

They are not automatically the competition training dataset.

This distinction is explicitly supported by the earlier project audit.

12. TEMPORAL LEAKAGE DEFENSE

Mandatory.

Every feature must satisfy:

feature(t) = f(events <= t)

Never:

f(events > t)

Graph snapshots:

G_t = (V_t, E_<t)

No future edges.

This applies to:

transaction features,
aggregates,
behavioral features,
temporal features,
graph features,
replay construction,
evaluation.
13. BLUE TEAM

Core architecture:

Behavioral features
        +
Temporal features
        +
Relational features
        +
Intent features
        ↓
GBDT backbone
        ↓
Calibration
        ↓
Cost-sensitive decision policy
        ↓
ALLOW / STEP-UP / BLOCK

Candidates:

LightGBM
XGBoost
CatBoost

We first establish the strongest single-model baseline.

Only then:

ensemble

if evidence supports it.

The older specification explicitly preserves the rule that sophisticated models cannot replace the baseline without empirical evidence.

14. BEHAVIORAL INTELLIGENCE

Required.

Examples:

current amount
vs
customer historical amount distribution

and:

new device
+
new geography
+
unusual velocity
+
merchant deviation

Features include:

historical aggregates
velocity
recency
personal baselines
merchant behavior
device behavior
account behavior
entity-level patterns.
15. TEMPORAL INTELLIGENCE

Required.

t-3 → t-2 → t-1 → t

Features:

time since previous transaction
rolling transaction count
rolling amount
merchant transitions
geography transitions
device transitions
behavioral change.

Deep sequence models remain optional.

16. RELATIONAL / GRAPH INTELLIGENCE

The system must investigate:

Account
   ↕
Device
   ↕
IP
   ↕
Merchant
   ↕
Transaction

Start with relational features.

Possible advanced models:

GraphSAGE
GAT
R-GCN
CARE-GNN
PC-GNN
HOT-GNN

GNN implementation remains Tier 2, not a mandatory dependency.

The older specification correctly warned not to promote unverified benchmark numbers into our final claims.

17. CLASS-IMBALANCE HANDLING

Mandatory requirement:

Class imbalance must be explicitly analyzed and handled using the method empirically appropriate for the data and model.

Candidates:

Class weighting
SMOTE
SMOTE-ENN
ADASYN
Focal loss
Under/over-sampling
Threshold optimization
Hybrid approaches
Critical rule

Resampling occurs after the temporal/data split and only inside training folds.

Correct:

RAW DATA
   ↓
TIME SPLIT
   ↓
TRAIN ONLY
   ↓
SMOTE / SMOTE-ENN
   ↓
MODEL

Never:

RAW DATA
   ↓
SMOTE
   ↓
TIME SPLIT
18. BLUE DECISION POLICY
Risk score
    ↓
Calibration
    ↓
Cost-sensitive policy
    ↓
ALLOW / STEP-UP / BLOCK

Business objective:

Utility =
- λ_f FraudLoss
- λ_friction CustomerFriction
- λ_review ReviewCost

subject to:

Security
Latency
Calibration
False-positive constraints

We do not optimize F1 alone.

19. DECISION AUDIT TRAIL

New mandatory engineering requirement.

Every production-style decision record should contain:

transaction_id
risk_score
decision
model_version
feature_version
policy_version
top_reason_codes
attack_family if known
intent_drift_score
timestamp

This gives the prototype an auditable answer to:

Why did the system block this transaction?

20. RED TEAM

Primary Red engine:

Attack Grammar + Constrained Mutation + NSGA-II

RL remains optional.

Attack process:

Attack family
      ↓
Mutable attributes
      ↓
Constraints
      ↓
Mutation
      ↓
Evaluation
      ↓
Pareto selection
21. MUTABILITY MASK

Every attack explicitly defines what can change.

Example:

amount        → mutable
timestamp     → mutable
merchant      → constrained
device        → immutable
identity      → immutable
authorization → constrained

This prevents the attacker from generating impossible scenarios.

22. NSGA-II

Objectives:

Maximize
Evasion
Fidelity
Novelty
Impact
Minimize
Attack cost
Constraint violations

The goal is not merely:

“Find something that fools the classifier.”

It is:

Find something that fools the classifier while remaining plausible and within the attack model.

23. ATTACK QUALITY GATE

Every generated attack passes:

Schema
   ↓
Constraint
   ↓
Fidelity
   ↓
Novelty
   ↓
Privacy
   ↓
Coverage
   ↓
Blue Team

Invalid or unrealistic attacks do not count as Red Team wins.

24. MONTI-INSPIRED GRAPH ATTACKS

MonTi remains a Tier 2 candidate/inspiration for multi-target graph injection and fraud-gang camouflage.

We may implement a simplified constrained version if:

time permits,
the graph representation is ready,
it produces measurable benefit,
and its methodology is implemented accurately enough to justify the description.

We do not claim:

“We reproduced MonTi”

unless we actually reproduce its methodology and evaluation.

25. RL — GATED

Possible:

PPO
DQN
Bandit

Hierarchy:

Attack Grammar
      ↓
Mutation
      ↓
NSGA-II
      ↓
RL

RL enters the final architecture only if it demonstrably improves the evaluation suite enough to justify its complexity.

If not:

NSGA-II remains the final Red optimizer.

This is important for the four-day implementation window.

26. PSRO / FICTITIOUS CO-PLAY — GATED

The older specification introduced:

PSRO / fictitious co-play / Stackelberg-style Red–Blue adaptation

This is conceptually useful for the co-evolution architecture.

However, it should not be mandatory Tier 1.

Use it only if the basic loop is already stable:

Red
 ↓
Blue
 ↓
Failure
 ↓
Replay
 ↓
Blue challenger
 ↓
Promotion

Then investigate:

PSRO / weighted historical Red mixture

as a higher-level strategy-selection mechanism.

If implementation complexity is high, the simpler replay + NSGA-II loop remains valid.

27. FAILURE TAXONOMY

Initial categories:

W1 Velocity blindness
W2 Device novelty blindness
W3 Geographic camouflage
W4 Merchant collusion
W5 Low-and-slow behavior
W6 Graph camouflage
W7 Intent drift
W8 Coordinated multi-account behavior
W9 Synthetic identity
W10 Agent swarm behavior
W11 Temporal camouflage
W12 Open-set anomaly

These categories are initial, not sacred.

If experiments reveal better categories, update them.

28. REPLAY BUFFER

Replay items contain:

attack
decision
features
failure category
model version
attack generator version
timestamp
evaluation result
provenance

The buffer should support:

hard failures,
novelty,
rarity,
historical attacks,
benign anchors,
boundary-proximity examples.
Prioritized replay

A practical priority score can combine:

hardness
+
novelty
+
boundary proximity
+
rarity

This is preferred over blindly replaying everything.

29. HMAC PROVENANCE

The older specification introduced HMAC-style integrity.

Retain it as a lightweight engineering mechanism:

artifact
+
metadata
+
HMAC

But explicitly document:

HMAC provides integrity/authenticity relative to control of the secret. It is not magically “zero trust.”

30. CONTINUAL LEARNING / FORGETTING

The project tracks:

Old-threat performance
New-threat performance
Forgetting
Adaptation gain

Potential techniques:

Replay
Knowledge distillation
EWC
Generative replay

But:

Tier 1

Replay + regression suite.

Tier 2/3

Distillation / EWC / generative replay.

The older specification's STG-DGR idea is retained as an optional research enhancement rather than a mandatory dependency.

This avoids spending the entire project implementing a complicated continual-learning system.

31. ADWIN — GATED

ADWIN may be used for statistical change-point/drift detection.

But it is not mandatory for the MVP.

If the project has time:

stream
 ↓
ADWIN
 ↓
detected drift
 ↓
retraining trigger

If not, a simpler explicit evaluation/retraining schedule is acceptable.

Do not pretend the system is “continuous online learning” if we only run periodic offline cycles.

32. CHAMPION / CHALLENGER

Never promote a challenger because one metric improved.

Required evaluation:

New attacks
+
Historical attacks
+
Hard negatives
+
OOD attacks
+
Calibration
+
Latency
+
Business utility

Then:

PASS → CHAMPION
FAIL → ROLLBACK
33. FIVE-DIMENSION PROMOTION GATE

The promotion gate checks:

Gate A — Detection

PR-AUC / recall / F1 / relevant metrics.

Gate B — Robustness

Hidden/OOD attack performance.

Gate C — Calibration

Calibration error and reliability.

Gate D — Forgetting

Historical threat performance.

Gate E — Latency

End-to-end decision latency.

A sixth practical dimension is:

Gate F — Business utility

Fraud loss + friction + review cost.

The exact thresholds are configuration targets, not guaranteed results.

34. ANTI-CIRCULARITY — THREE WORLDS

This remains locked.

World A — Evolution

Red and Blue learn here.

World B — Shifted Physics

Simulator parameters change:

merchant distribution
velocity patterns
geography
fraud prevalence
dependency structure
World C — Hidden Attacks

Attack families withheld during adaptation.

The system must face them after training.

35. EXTERNAL BENCHMARK WORLD

If suitable public datasets are available and usable within the competition constraints, use them as an external sanity check.

They do not replace the synthetic competition world.

This prevents:

our simulator
→ our attacks
→ our detector
→ our evaluation

from becoming the only evidence.

36. CLAIM → TEST → RESULT

Every major claim follows:

CLAIM
 ↓
HYPOTHESIS
 ↓
TEST
 ↓
BASELINE
 ↓
TREATMENT
 ↓
METRIC
 ↓
RESULT
 ↓
CONCLUSION

This is mandatory.

37. CORE CLAIMS
C1

GBDT ensemble improves over the strongest individual GBDT.

C2

Graph features improve coordinated-fraud detection.

C3

Adaptive Red attacks expose weaknesses missed by static generation.

C4

Closed-loop hardening reduces attack success.

C5

Hardening does not materially destroy old-threat performance.

C6

Intent-drift features detect attacks missed by transaction-only features.

C7

Adaptive training generalizes to hidden attack families.

Every one must be experimentally demonstrated before being stated as a result.

38. TARGET / VERIFIED / RESULT

Every numerical or research statement gets one of three labels:

VERIFIED

Supported by a source or completed experiment.

TARGET

A threshold we intend to achieve.

RESULT

Actually measured.

For example:

P99 latency target: <5 ms

Measured:
3.7 ms

Status:
RESULT

Never write:

“Guaranteed <4.5 ms”

before measurement.

This distinction is explicitly required in the finalized specification.

39. RESEARCH CLAIM REGISTER

Create:

docs/research/CLAIM_REGISTER.md

Each claim contains:

Claim ID
Statement
Source
Source type
Date
Applicability
Assumptions
How we test it
Status
40. EXPERIMENT REGISTER

Create:

docs/experiments/EXPERIMENT_REGISTER.md

Each experiment:

EXP-XXX
Hypothesis
Dataset version
Code commit
Config
Seed
Baseline
Treatment
Metrics
Result
Conclusion
Artifact

The latest specification explicitly locks these registers.

41. FEATURE → TEST RULE

Every significant feature:

Feature
 ↓
Hypothesis
 ↓
Implementation
 ↓
Unit test
 ↓
Ablation
 ↓
Evaluation
 ↓
Keep / Remove

No component stays simply because it sounds sophisticated.

42. COMPUTE ARCHITECTURE
Local — MacBook Pro

Use local machine for:

Git
Antigravity
Claude review
Coding
Unit tests
Lint
Type checks
Schemas
Documentation
Streamlit
Lightweight demo
Artifact validation
Integration
Cloud

Use Kaggle/Colab for:

Large synthetic generation
Model training
Graph experiments
NSGA-II sweeps
Large evaluations
RL if attempted
Diffusion if attempted
Hard rule

No heavy training locally.

The older Step 7 explicitly separates local orchestration from cloud-heavy computation.

43. DYNAMIC COMPUTE PROFILES

Use:

configs/
├── base.yaml
├── local.yaml
├── kaggle_cpu.yaml
├── kaggle_gpu.yaml
├── colab_cpu.yaml
└── colab_gpu.yaml

Detect:

GPU
VRAM
RAM
CPU

then select the appropriate profile.

Do not hard-code:

T4 × 2
30 hours/week

as guaranteed resources.

44. RESUMABLE CLOUD EXECUTION

Every heavy run should support:

checkpoint
   ↓
artifact
   ↓
manifest
   ↓
resume

If a cloud runtime dies, the experiment must not require starting from zero.

This is an important engineering addition because of the actual deadline and free-compute constraints.

45. EXPERIMENT MANIFEST

Every cloud run produces:

run/
├── manifest.json
├── config.yaml
├── environment.json
├── metrics.json
├── predictions.parquet
├── logs/
└── plots/

Manifest:

git commit
dataset version
model version
seed
runtime
parameters
metrics
artifact hashes

No W&B dependency.

46. W&B

Optional.

The system must work with:

Git
+
manifest
+
metrics
+
artifacts

without W&B.

47. INTERNAL JSON CONTRACTS

This missing engineering piece from the older Step 7 is now locked.

Red and Blue communicate through versioned internal schemas.

Example:

{
  "attack_id": "...",
  "attack_family": "...",
  "world_id": "...",
  "features": {},
  "constraints": {},
  "generator_version": "...",
  "provenance": {}
}

Blue response:

{
  "attack_id": "...",
  "risk_score": 0.0,
  "decision": "BLOCK",
  "detected": true,
  "reason_codes": [],
  "model_version": "...",
  "latency_ms": 0.0
}

Schemas are tested.

No silent interface changes.

48. OFFLINE DEMO

Mandatory.

DEMO_MODE=true

loads:

models
graphs
attacks
metrics
evolution history
sample transactions

The demo must continue functioning if:

Kaggle is unavailable,
Colab is unavailable,
internet fails,
GPU quota disappears.
49. STREAMLIT PROTOTYPE

The web prototype has four main views.

View 1 — Mission Control
Transactions
ALLOW
STEP-UP
BLOCK
Risk
Latency
View 2 — Red Team
Attack family
Attack cost
Evasion
Fidelity
Novelty
Coverage
Pareto frontier
View 3 — Blue Team
Risk
Decision
Reason codes / SHAP
Intent drift
Graph evidence
View 4 — Co-evolution
Round
Red ASR
Blue performance
Forgetting
Adaptation gain
Champion version

The older specification explicitly defined these operational views and the offline artifact requirement.

50. ATTACK SURFACE MAP

The UI includes:

                 EVASION
                    ↑
                    │
                 ●  │
           ●       │
                    │   ●
        ●           │
                    └────────────→ FIDELITY

But only real experiment results are plotted.

No fabricated values.

51. CO-EVOLUTION SCOREBOARD

The UI should show:

Round | Red ASR | Blue PR-AUC | FPR | Forgetting | Latency

This gives judges visual evidence of whether the loop actually improves.

The central demonstration should be:

Before hardening:
Attack succeeds

        ↓

Failure analysis

        ↓

Hardening

        ↓

Same family / unseen variant

        ↓

Attack success decreases
52. REPOSITORY

Use:

mastercard-ai-defense-lab/

├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── CHANGELOG.md

├── pyproject.toml
├── uv.lock
├── Makefile

├── PROJECT_CONTEXT.md
├── PROJECT_STATUS.md
├── HANDOFF.md
├── PROJECT_LOG.md

├── configs/
│   ├── base.yaml
│   ├── local.yaml
│   ├── kaggle_cpu.yaml
│   ├── kaggle_gpu.yaml
│   ├── colab_cpu.yaml
│   └── colab_gpu.yaml

├── src/
│   └── mastercard_defense/
│       ├── schemas/
│       ├── simulation/
│       ├── features/
│       ├── blue_team/
│       ├── red_team/
│       ├── graph/
│       ├── temporal/
│       ├── intent/
│       ├── replay/
│       ├── continual/
│       ├── evaluation/
│       ├── provenance/
│       └── utils/

├── scripts/
│   ├── generate_world.py
│   ├── train_baseline.py
│   ├── train_blue.py
│   ├── run_red_team.py
│   ├── run_nsga2.py
│   ├── run_rl.py
│   ├── run_coevolution.py
│   └── evaluate.py

├── notebooks/
│   ├── kaggle/
│   └── colab/

├── app/
│   ├── app.py
│   ├── components/
│   └── services/

├── tests/
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   ├── data/
│   └── e2e/

├── artifacts/
│   ├── manifests/
│   ├── metrics/
│   └── demo/

├── docs/
│   ├── architecture/
│   ├── experiments/
│   ├── research/
│   ├── decisions/
│   └── submission/

├── project/
│   ├── tasks/
│   │   └── TASK_REGISTRY.md
│   ├── progress/
│   │   ├── ankit/
│   │   └── friend/
│   ├── handoffs/
│   └── decisions/

└── .github/
    └── workflows/
        ├── ci.yml
        ├── security.yml
        └── docs.yml

This preserves the older specification's detailed repository discipline.

53. AI CODER RULES

Every AI coding agent must:

Read PROJECT_CONTEXT.md.
Read PROJECT_STATUS.md.
Read HANDOFF.md.
Read assigned TASK_ID.
Modify only permitted scope.
Write tests.
Run tests.
Record results.
Update status.
Write handoff.
Never invent results.
Never claim cloud execution without artifacts.
Never silently change architecture.
Never overwrite another developer's work.
Never add dependencies without documenting why.

These rules are retained from the older Step 7 because they are genuinely useful, not cosmetic.

54. MULTI-AGENT CONTEXT CONTROL

PROJECT_CONTEXT.md contains:

Current objective
Architecture
Locked decisions
Current branch
Completed steps
Known limitations
Current metrics
Open questions
Forbidden changes
Next tasks

HANDOFF.md contains:

FROM
TO
TASK
COMPLETED
FILES CHANGED
TESTS RUN
RESULTS
BLOCKERS
NEXT ACTION

Workflow:

Antigravity
     ↓
Git
     ↓
Claude review
     ↓
Friend
     ↓
Git
     ↓
Ankit

Claude remains a reviewer, not a second autonomous architect.

55. GITHUB WORKFLOW
main
 ↑
PR
 ↑
dev
 ↑
feature/TASK-ID-name

No direct changes to main.

Workflow:

branch
 ↓
code
 ↓
test
 ↓
commit
 ↓
push
 ↓
PR
 ↓
review
 ↓
merge
56. CI

Every PR:

Install
 ↓
Lint
 ↓
Type check
 ↓
Unit tests
 ↓
Schema tests
 ↓
Integration tests
 ↓
Security checks
 ↓
Build

Heavy ML experiments do not run on every PR.

Instead:

CI
├── lightweight deterministic tests
└── cloud evaluation workflows

This keeps the development loop fast.

57. TWO-PERSON DIVISION
ANKIT — Integration / Evaluation / Product

Own:

Infrastructure
Evaluation
Integration
UI
Documentation
Submission
Evidence
FRIEND — ML / Cloud

Own:

Data
Blue
Red
Graph
Cloud
Co-evolution

But both must be able to run the full project.

No single-person knowledge silo.

58. TASK DEPENDENCY
INFRA
  │
  ▼
DATA SCHEMA
  │
  ▼
SIMULATOR
  │
  ├───────────────┐
  ▼               ▼
BLUE          EVALUATION
  │               │
  └───────┬───────┘
          ▼
         RED
          │
          ▼
        LOOP
          │
          ▼
         UI
          │
          ▼
  FINAL EVALUATION
          │
          ▼
     SUBMISSION

Some branches execute in parallel.

59. BENCHMARK LADDER
Level 0 — Simple heuristic

Level 1 — Single GBDT

Level 2 — GBDT ensemble

Level 3 — Behavioral + temporal

Level 4 — Graph features

Level 5 — Adaptive Red

Level 6 — Closed-loop hardening

Level 7 — Intent-aware defense

Level 8 — Full co-evolution

At every level:

Did the addition produce measurable improvement?

60. FINAL ABLATION MATRIX

Blue:

GBDT
+ Behaviour
+ Temporal
+ Graph
+ Intent
+ Conformal
+ Adaptive Red
+ Replay
+ Co-evolution

Red/system:

Attack Success Rate
Fidelity
Novelty
Coverage
Forgetting
Latency
Adaptation Cost
Robustness Retention
61. ADAPTATION COST

This is another useful older-specification metric that should be retained.

Measure:

Adaptation Cost =
CPU/GPU time
+
number of retraining steps
+
generation cost

This prevents a system from “improving” simply by consuming unlimited compute.

62. ROBUSTNESS RETENTION

Track:

Performance after hardening
/
Performance before hardening

on historical attack families.

Goal:

Hardening should improve new-threat performance without materially destroying mature-threat performance.

63. PLASTICITY

Track performance improvement on novel attack vectors:

Novel-threat performance after adaptation
-
Novel-threat performance before adaptation

This measures whether the system actually learns new threats.

64. NO ARCHITECTURE BLOAT

Explicitly prohibited:

GNN
+
Transformer
+
LLM
+
RL
+
Diffusion
+
GAN
+
Knowledge graph
+
Blockchain

simply because the combination looks impressive.

Every additional component introduces:

implementation risk,
integration risk,
debugging cost,
latency,
explainability difficulty,
demonstration complexity.

The objective remains:

Minimum architecture achieving maximum measurable differentiation.

65. TECHNOLOGY PRIORITY
TIER 1 — NON-NEGOTIABLE
Synthetic payment world
GBDT baseline
Behavioral features
Temporal features
Attack grammar
Constrained mutation
NSGA-II
Evaluation harness
Failure analysis
Replay
Champion/challenger
Closed loop
Core metrics
Streamlit
Offline demo
GitHub
CI
JSON contracts
Experiment manifests
Claim register
TIER 2 — DIFFERENTIATION
Intent drift
Graph features
Temporal motifs
Conformal uncertainty
Hidden attack evaluation
Anti-circularity
Attack surface map
External reality anchor
Prioritized replay
ADWIN
PSRO if feasible
MonTi-inspired graph attack
Adaptation-cost tracking
Robustness-retention tracking
TIER 3 — RESEARCH ENHANCEMENTS
PPO
DQN / bandit
GNN
STG-DGR
Diffusion
EWC
Knowledge distillation
RAG investigator
LLM-assisted attacker
Hard rule

If Tier 1 is unstable, Tier 3 does not get built.

This is the biggest realism safeguard in the whole specification.

66. OPTIONAL COMPONENT DECISION RULE

For any Tier 2/3 component:

Candidate
   ↓
Implementation
   ↓
Experiment
   ↓
Ablation
   ↓
Measured benefit
   ↓
Complexity / latency / compute assessment
   ↓
KEEP or REMOVE

No research paper automatically becomes architecture.

67. STOP / GO GATES
Gate 1 — Simulator
GO
Valid data
Valid state
Hard negatives
Fidelity checks
No leakage
STOP
Invalid transactions
Leakage
Obviously unrealistic distributions
Gate 2 — Blue Baseline
GO

Baseline beats simple heuristic.

STOP

If it doesn't.

Then fix:

data
features
validation

before GNN/RL.

Gate 3 — Red
GO

Attacks are:

valid
realistic
diverse
challenging
STOP

If Red only generates garbage that fools Blue.

Gate 4 — Closed Loop
GO

Attack success decreases while legitimate performance remains acceptable.

STOP

If:

ASR doesn't improve
OR
false positives explode
OR
historical performance collapses
Gate 5 — Advanced Models

Only after Tier 1/2 stability:

GNN
PPO
DQN
Diffusion
STG-DGR
Gate 6 — Final Claims

Only claim superiority when:

baseline
vs
ours

is supported by the actual evaluation protocol.

68. TARGETS — NOT GUARANTEES

Potential project targets may include:

P99 latency < 4.5 ms
Forgetting < 6%
ASR reduction ≥ 25%
ECE ≤ 0.04
1M-row scale

But these are:

TARGETS

not guaranteed results.

If measured differently, report the actual result.

Do not change the result to match the target.

69. SAFETY BOUNDARY

Everything operates in:

Synthetic data
Anonymized data
Authorized competition data
Controlled simulation

Never:

Real cardholder data
PII
Production payment data
Live payment-system attacks
Third-party attacks

The prototype is a security research simulation, not a live attack platform.

70. FINAL ENGINEERING CHECKLIST — ENG-01 TO ENG-25

This is the part from the older Step 7 that I specifically do want preserved, but corrected for feasibility.

[ENG-01]
Decoupled local/cloud compute.

[ENG-02]
Dynamic CPU/GPU hardware detection.

[ENG-03]
Standalone run manifests.

[ENG-04]
Attack Grammar + NSGA-II as primary Red engine.

[ENG-05]
RL PPO/DQN = gated Tier 3.

[ENG-06]
GBDT family as core Blue baseline.

[ENG-07]
Class balancing only inside training folds.

[ENG-08]
Streaming/online feature store using time-decay features where needed.

[ENG-09]
Causal graph snapshots G_t = (V_t, E_<t).

[ENG-10]
Conformal uncertainty investigated only with correct assumptions.

[ENG-11]
Cost-sensitive decision router.

[ENG-12]
Agentic intent-drift engine.

[ENG-13]
MonTi-inspired graph attacks = Tier 2.

[ENG-14]
PSRO / Stackelberg co-evolution = gated Tier 2/3.

[ENG-15]
Replay provenance + integrity.

[ENG-16]
STG-DGR/generative replay = Tier 3.

[ENG-17]
ADWIN drift detection = Tier 2/3.

[ENG-18]
Champion/challenger promotion gate.

[ENG-19]
Tri-split anti-circularity evaluation.

[ENG-20]
Measured latency profiling — NO hard SLA guarantee before measurement.

[ENG-21]
Streamlit interactive prototype with four operational views.

[ENG-22]
Offline demo artifact pack.

[ENG-23]
Versioned internal JSON contracts.

[ENG-24]
Submission artifacts mapped and validated.

[ENG-25]
Zero real PII / zero live payment attacks.

This is the corrected version of the older checklist. The older source had several of these components explicitly, including dynamic compute, manifests, NSGA-II, gated RL, causal graphs, intent drift, PSRO, replay, STG-DGR, ADWIN, tri-split evaluation, Streamlit, offline artifacts and JSON contracts.

71. WHAT WE WILL NEVER CLAIM WITHOUT TESTING

Never claim:

<4.5 ms P99
<6% forgetting
25% ASR reduction
state-of-the-art
better than Mastercard's systems
actual Mastercard production integration
actual EMV 3DS integration
actual Verifiable Intent verification
guaranteed privacy
RL superiority
GNN superiority

unless the corresponding evidence exists.

72. WHAT WE CAN CLAIM

After implementation:

We designed and implemented a controlled adversarial payment-security laboratory that identifies attack families, generates constrained synthetic attacks, evaluates attack fidelity and evasion, detects them using a multi-signal defense, stores failures, and evaluates whether subsequent challengers become more robust.

Then:

Our experiments show X improvement under Y evaluation protocol.

only when X and Y actually exist.

73. FINAL EVIDENCE PACKAGE

Before submission, we want:

Realistic attacks
+
Attack-surface coverage
+
Quantitative fidelity
+
Strong baseline
+
Adaptive attacks
+
Hidden attacks
+
Failure analysis
+
Measurable hardening
+
No catastrophic forgetting
+
Low false positives
+
Measured latency
+
Adaptation cost
+
Offline demo
+
Reproducibility manifests
+
Public GitHub
+
DOCX
+
Kaggle Writeup
74. FINAL MASTER FLOW
STEP 1
Competition requirements
        ↓
STEP 2
Competitive intelligence
        ↓
STEP 3
Synthetic payment world
        ↓
STEP 4
Blue Team defense
        ↓
STEP 5
Adaptive Red Team
        ↓
STEP 6
Closed-loop co-evolution
        ↓
STEP 7
IMPLEMENTATION
+
ENGINEERING
+
TESTING
+
EVALUATION
+
PROTOTYPE
        ↓
 ┌───────────────┬────────────────┐
 ▼               ▼                ▼
CLAIMS          TESTS          BASELINES
 └───────────────┬────────────────┘
                 ▼
          EXPERIMENT RESULTS
                 ↓
          PROMOTION GATES
                 ↓
          OFFLINE DEMO PACK
                 ↓
STEP 8
EXECUTION + SUBMISSION
                 ↓
       ┌─────────┼──────────┐
       ▼         ▼          ▼
    GitHub      DOCX      Kaggle
       └─────────┼──────────┘
                 ▼
              JUDGING
My analysis of this merged Step 7

This is the important part.

What I deliberately added from the old Step 7

I did not throw away the older material just because the newer Step 7 was cleaner.

I brought over:

dynamic compute detection
compute profiles
resumable cloud philosophy
internal JSON contracts
streaming feature-store concept
causal graph snapshots
PSRO/fictitious co-play
prioritized replay
ADWIN
STG-DGR/generative replay
EWC/distillation as optional forgetting mechanisms
adaptation-cost metric
robustness-retention metric
plasticity/adaptation metric
detailed repository structure
AI-agent operating rules
PROJECT_CONTEXT.md
HANDOFF.md
explicit Git workflow
CI workflow
exact Antigravity/Claude roles
detailed prototype views
offline demo pack
ENG-01–ENG-25 operational checklist
stronger promotion-gate structure.

Those are real additions, not fluff. The older specification explicitly contained the repository/agent-control and task-management structure.

What I deliberately DID NOT make mandatory

This is where I am pushing back on the old specification.

I did not make mandatory:

PPO
DQN
PSRO
STG-DGR
ADWIN
EWC
diffusion
GNN
full MonTi reproduction
RAG
LLM attacker
exact 1M-row scale
exact T4×2 hardware
exact <4.5 ms
exact <6% forgetting
exact −25% ASR.

Why?

Because that would make the project specification internally contradictory.

You have two developers and roughly four days. The older Step 7's technology list was too large to guarantee successful implementation. The latest version correctly introduced Tiering specifically to prevent this.

So the merged version preserves the ideas without falsely promising the implementation.

One more correction: the old Step 7's “certified” language

I specifically changed the old wording around conformal prediction.

The old operational checklist said:

“Mondrian Conformal Prediction Sets ... outputting certified error bounds.”

That is too strong for our project unless the assumptions and calibration conditions are genuinely satisfied.

Our specification now says:

Conformal uncertainty can be investigated, with guarantees described only under the assumptions that actually hold.

That is technically safer.

One more correction: “continuous” co-evolution

I also don't want the final submission to claim:

“continuous online learning”

unless we're actually running continuous online updates.

For the MVP, what we can honestly implement is:

Round 1
 ↓
evaluate
 ↓
failure memory
 ↓
retrain challenger
 ↓
promotion
 ↓
Round 2

That is iterative closed-loop co-evolution.

If ADWIN/online retraining actually gets implemented, then we can describe the system as more continuous.

That distinction matters.

# Step 8
# STEP 8 — 96-HOUR EXECUTION, TASK CONTROL & SUBMISSION SPECIFICATION

**Status: FINAL EXECUTION PLAN**

I have pressure-tested Step 7 against the current situation. The biggest correction is simple:

> **We do not have time to build every research idea in Step 7.**

Today is **27 August 2026**, and the competition material you supplied says submission closes **31 August 2026 EOD**. So we have roughly four days. That means Step 8 must be a **delivery system**, not another architecture exercise.

The project will be built in layers, with hard stop/go gates. Research-heavy components that do not prove their value are dropped.

The goal is not "implement every SOTA paper."

The goal is:

> **Ship the strongest defensible end-to-end system we can actually test, demonstrate and submit before the deadline.**

---

# 1. STEP 8 MISSION

Step 8 converts:

```text
Architecture
     ↓
Tasks
     ↓
Code
     ↓
Cloud experiments
     ↓
Measured evidence
     ↓
Demo
     ↓
GitHub
     ↓
DOCX
     ↓
Kaggle submission
```

Everything from this point becomes executable.

---

# 2. THE 96-HOUR RULE

We divide the remaining time into four execution blocks.

```text
27 AUG
│
├── BLOCK A — FOUNDATION
│   Repository + simulator + evaluation
│
28 AUG
│
├── BLOCK B — CORE INTELLIGENCE
│   Blue + Red + metrics
│
29 AUG
│
├── BLOCK C — CLOSED LOOP
│   Adaptive hardening + UI + experiments
│
30 AUG
│
├── BLOCK D — EVIDENCE
│   Ablations + demo + documentation
│
31 AUG
│
└── SUBMISSION BUFFER
    Final validation + Kaggle submission
```

**Important:** We should aim to have a technically complete submission candidate by **30 August**, not 31 August.

31 August is the emergency buffer.

---

# 3. THE MOST IMPORTANT EXECUTION PRINCIPLE

## Build vertically, not horizontally.

Bad approach:

```text
finish simulator
finish GNN
finish RL
finish UI
finish documentation
```

Good approach:

```text
Generate 1000 transactions
       ↓
Detect them
       ↓
Generate one attack
       ↓
Detect attack
       ↓
Measure result
       ↓
Feed failure back
       ↓
Show it in UI
```

Once that works:

```text
1,000
 ↓
10,000
 ↓
100,000
 ↓
1M if useful
```

This gives us a working system early.

---

# 4. FINAL PRIORITY ORDER

## P0 — MUST SHIP

```text
Synthetic payment world
        +
Temporal split
        +
GBDT baseline
        +
Attack grammar
        +
NSGA-II / constrained mutation
        +
Attack fidelity evaluation
        +
Failure analyzer
        +
Closed-loop retraining
        +
Ablation framework
        +
Streamlit demo
        +
GitHub
        +
DOCX
```

## P1 — STRONG DIFFERENTIATORS

```text
Intent drift
Graph-derived features
Conformal uncertainty
Hidden attack families
Champion/challenger
Anti-circular evaluation
```

## P2 — ONLY IF P0/P1 ARE STABLE

```text
GNN
PPO
DQN
STG-DGR
Diffusion generation
RAG investigator
```

This ordering is now **locked**.

---

# 5. TASK ID SYSTEM

Every task receives an ID.

```text
INF  = Infrastructure
DATA = Synthetic world
EVAL = Evaluation
BLUE = Blue Team
RED  = Red Team
LOOP = Closed loop
APP  = Prototype
DOC  = Documentation
FINAL = Submission
```

Example:

```text
DATA-003
```

means:

> Synthetic-world task 003.

---

# 6. TWO-PERSON OWNERSHIP

## ANKIT — Integration / Evaluation / Product Lead

Own:

```text
INF
EVAL
APP
DOC
FINAL
integration
GitHub
CI/CD
architecture
acceptance testing
```

## FRIEND — ML / Cloud Compute Lead

Own:

```text
DATA
BLUE
RED
LOOP
cloud experiments
model training
large-scale generation
```

---

# 7. HANDOFF RULE

Friend never says:

> "Done."

Instead he updates:

```text
project/progress/friend/
```

with:

```text
TASK_ID
STATUS
WHAT_CHANGED
FILES
COMMANDS
TESTS
RESULTS
ARTIFACTS
BLOCKERS
NEXT_TASK
```

Then updates:

```text
HANDOFF.md
```

and pushes the branch.

---

# 8. BRANCHING STRATEGY

```text
main
 │
 └── dev
      │
      ├── feature/INF-001-repo
      ├── feature/DATA-001-simulator
      ├── feature/BLUE-001-baseline
      ├── feature/RED-001-grammar
      └── feature/APP-001-dashboard
```

No direct development on `main`.

---

# 9. MERGE RULE

Every PR requires:

```text
Code
+
Tests
+
Status update
+
Handoff
+
No unrelated modifications
```

For heavy ML:

```text
Code test locally
        +
Cloud experiment
        +
Saved manifest
```

---

# 10. INFRASTRUCTURE TASKS

## INF-001 — Repository Initialization

### Owner

Ankit

### Build

```text
mastercard-ai-defense-lab/
```

with the Step 7 repository structure.

### Acceptance

```text
git status clean
package imports
pytest executes
Streamlit launches
```

---

## INF-002 — Python Environment

Use `uv` rather than unnecessarily heavy environment tooling.

Core dependencies:

```text
polars
numpy
scipy
scikit-learn
lightgbm
xgboost
catboost
pydantic
pyyaml
pytest
ruff
mypy
streamlit
plotly
networkx
```

Add:

```text
torch
torch-geometric
stable-baselines3
```

only when those modules are actually activated.

This reduces installation failures.

---

## INF-003 — Configuration System

Create:

```text
configs/
├── base.yaml
├── local.yaml
├── kaggle.yaml
└── colab.yaml
```

Runtime detection:

```text
CPU/GPU
RAM
VRAM
workers
dataset scale
```

---

## INF-004 — Schema Contracts

Use Pydantic models.

At minimum:

```text
Transaction
Customer
Merchant
Device
AttackCandidate
BlueDecision
ExperimentManifest
EvaluationResult
```

This is critical because Red and Blue will be developed separately.

---

## INF-005 — Testing Framework

Create:

```text
tests/
├── unit/
├── integration/
├── data/
├── regression/
└── e2e/
```

---

## INF-006 — CI

GitHub Actions:

```text
checkout
 ↓
install
 ↓
ruff
 ↓
mypy
 ↓
pytest
 ↓
package validation
```

Heavy GPU jobs are excluded from normal PR CI.

---

# 11. DATA TASKS

## DATA-001 — Synthetic Schema

Define all entities and relationships.

### Acceptance

Generate:

```text
1000 transactions
```

without invalid references.

---

# 12. DATA-002 — Customer Archetypes

Create the agreed archetypes.

But don't hard-code fake realism.

Each archetype needs:

```text
distribution
parameters
reason
test
```

---

# 13. DATA-003 — Merchant World

Generate:

```text
merchant
MCC
geography
risk profile
transaction distribution
```

---

# 14. DATA-004 — Stateful Ledger

Maintain:

```text
balance
credit
velocity
devices
tokens
authentication
```

The simulator must reject impossible events.

Example:

```text
available credit = ₹1,000

transaction = ₹10,000

→ invalid unless explicitly configured as an overdraft scenario
```

---

# 15. DATA-005 — Hard Negatives

Generate:

```text
travel
flash sale
family device
B2B reconciliation
```

and additional legitimate anomalies.

---

# 16. DATA-006 — Fidelity Harness

Every dataset generation run outputs:

```text
dataset.parquet
manifest.json
fidelity_report.json
```

Measure:

```text
marginals
correlations
temporal distributions
graph statistics
```

---

# 17. DATA-007 — Dataset Versioning

Every dataset gets:

```text
DATASET-v001
DATASET-v002
...
```

Never overwrite datasets used for experiments.

---

# 18. EVALUATION TASKS

These are **Ankit-owned and must start immediately**, not after the models.

---

## EVAL-001 — Metric Framework

Mandatory metrics:

### Classification

```text
PR-AUC
ROC-AUC
precision
recall
F1
```

### Operational

```text
false-positive rate
false-negative rate
decision distribution
latency
```

### Red Team

```text
Attack Success Rate
fidelity
novelty
attack cost
```

### Closed loop

```text
ASR before
ASR after
forgetting
OOD performance
```

---

# 19. EVAL-002 — Baseline Ladder

Automatically compare:

```text
B0 Random/heuristic
B1 Single LightGBM
B2 XGBoost
B3 CatBoost
B4 Ensemble
B5 Ensemble + behavioral
B6 Ensemble + temporal
B7 Ensemble + graph
B8 Ensemble + intent
```

This becomes the project's scientific backbone.

---

# 20. EVAL-003 — Temporal Split

Example:

```text
70% earliest → train
15% next      → validation
15% latest    → test
```

Exact proportions can be configured.

No random leakage.

---

# 21. EVAL-004 — Hidden Attack Set

Some attack families must never appear in Blue training.

Example:

```text
Training:
ATO
velocity
mule

Hidden:
intent drift
graph camouflage
agent coordination
```

Then test them later.

This gives us a genuine novelty/generalization experiment.

---

# 22. EVAL-005 — Anti-Circularity

Automatically verify:

```text
training attack IDs ∩ test attack IDs = ∅
```

and:

```text
training generator seeds ≠ evaluation seeds
```

---

# 23. BLUE TASKS

## BLUE-001 — Feature Store

Implement streaming:

```text
velocity_1h
velocity_6h
velocity_24h
amount_decay
merchant_velocity
device_account_count
```

---

# 24. BLUE-002 — Strong Single Baseline

Start with **LightGBM**.

Not ensemble.

Why?

Because we need:

```text
baseline
```

before claiming the ensemble helps.

---

# 25. BLUE-003 — XGBoost + CatBoost

Train independently.

Compare against LightGBM.

---

# 26. BLUE-004 — Ensemble

Only retain ensemble if:

```text
ensemble > best individual
```

on the same evaluation protocol.

---

# 27. BLUE-005 — Calibration

Test:

```text
raw probability
vs
Platt
vs
isotonic
```

Measure:

```text
Brier
ECE
```

Keep the best calibrated method.

---

# 28. BLUE-006 — Decision Router

Output:

```text
ALLOW
STEP_UP
BLOCK
```

based on risk + business cost.

---

# 29. BLUE-007 — SHAP

For selected cases:

```text
risk
↓
top features
↓
reason
```

Do not force SHAP onto every transaction if latency becomes problematic.

---

# 30. BLUE-008 — Graph Features

Before implementing a full GNN, create cheap graph-derived features:

```text
shared_device_accounts
shared_ip_accounts
merchant_degree
device_degree
account_degree
recent_neighbor_fraud_rate
transaction_cluster_size
```

This is a huge time-saving decision.

If these features produce a meaningful lift:

> then consider GNN.

If not:

> don't build GNN merely for novelty.

---

# 31. BLUE-009 — Intent Engine

Calculate:

```text
declared intent
vs
actual transaction
```

and produce:

```text
intent_drift_score
```

Then run:

```text
without intent
vs
with intent
```

---

# 32. RED TASKS

## RED-001 — Attack Grammar

Define:

```text
attack family
target
mutable fields
constraints
objective
budget
```

---

# 33. RED-002 — Attack Families

Initial families:

```text
R1 Account Takeover
R2 Velocity Burst
R3 Low-and-Slow
R4 Mule Ring
R5 Device Farm
R6 Merchant Collusion
R7 Graph Camouflage
R8 Intent Drift
R9 Multi-Agent Coordination
R10 Synthetic Identity
```

---

# 34. RED-003 — Mutation Engine

Generate valid mutations.

Example:

```text
amount:
₹500 → ₹700

timestamp:
+30 sec → +180 sec

merchant:
same category → alternate merchant
```

Constraints prevent impossible attacks.

---

# 35. RED-004 — Attack Fidelity

Reject attacks that:

```text
break schema
break ledger
produce unrealistic distributions
violate immutable fields
```

---

# 36. RED-005 — NSGA-II

Only after the mutation engine works.

Optimize:

```text
evasion
fidelity
novelty
impact
cost
```

---

# 37. RED-006 — Counterfactual Attack

For a detected attack:

```text
BLOCK
 ↓
change minimum mutable feature
 ↓
ALLOW?
```

This gives us:

> **Minimum Evasion Distance**

This is a particularly strong explanatory metric.

---

# 38. RED-007 — RL

Only if everything above works.

The PPO agent can select:

```text
attack family
budget
strategy
```

But if PPO does not beat NSGA-II:

**remove it from the final critical path.**

---

# 39. LOOP TASKS

## LOOP-001 — Failure Analyzer

Every successful Red attack becomes:

```text
failure case
```

with:

```text
why missed
features
attack family
model version
```

---

# 40. LOOP-002 — Replay Buffer

Store successful attacks and hard negatives.

---

# 41. LOOP-003 — Challenger

Train:

```text
Champion
vs
Champion + failures
```

---

# 42. LOOP-004 — Regression

Old attacks must continue to be detected.

This directly tests catastrophic forgetting.

---

# 43. LOOP-005 — Promotion Gate

A challenger only wins if:

```text
NEW ATTACK PERFORMANCE ↑
AND
OLD ATTACK PERFORMANCE ≈ maintained
AND
LEGITIMATE PERFORMANCE maintained
AND
CALIBRATION acceptable
AND
LATENCY acceptable
```

---

# 44. LOOP-006 — Closed Loop Experiment

Final experiment:

```text
Round 0
 ↓
Red attacks
 ↓
Blue misses
 ↓
Harden
 ↓
Round 1
 ↓
Red adapts
 ↓
Harden
 ↓
Round 2
```

Measure:

```text
ASR(t)
```

This is the project's central result.

---

# 45. APP TASKS

## APP-001 — Mission Control

Display:

```text
transactions
decision
risk
latency
```

---

## APP-002 — Red Console

Display:

```text
attack family
evasion
fidelity
cost
Pareto frontier
```

---

## APP-003 — Decision Intelligence

Display:

```text
decision
risk
SHAP
intent drift
graph evidence
```

---

## APP-004 — Co-evolution

Display:

```text
Round 0
Round 1
Round 2
...
```

and:

```text
Red ASR
Blue performance
```

---

# 46. APP-005 — DEMO MODE

This is mandatory.

```bash
DEMO_MODE=true streamlit run app/app.py
```

The demo must not depend on Kaggle.

---

# 47. APP-006 — DEMO SCRIPT

The judge should be able to follow:

```text
1. Start system
2. Normal transactions
3. Turn Red Team on
4. Attack appears
5. Blue catches some
6. One attack succeeds
7. Failure is analyzed
8. Challenger hardens
9. Same attack fails
10. New attack appears
```

That is the story.

---

# 48. APP-007 — ATTACK SURFACE

Plot actual generated attacks:

```text
X = Fidelity
Y = Evasion
size = Impact
symbol = Attack Family
```

---

# 49. DOCUMENTATION TASKS

## DOC-001 — Technical Report

Structure:

```text
1 Executive Summary
2 Problem
3 Threat Landscape
4 Identify
5 Generate
6 Defend
7 Closed Loop
8 Architecture
9 Experiments
10 Results
11 Ablations
12 Limitations
13 Deployment Feasibility
14 Responsible AI
15 Future Work
```

---

# 50. DOC-002 — CLAIM REGISTER

Every external claim gets:

```text
source
date
URL
claim
verification
```

---

# 51. DOC-003 — EXPERIMENT REGISTER

Every result gets:

```text
experiment ID
commit
dataset
seed
config
metric
result
```

---

# 52. DOC-004 — LIMITATIONS

We explicitly state:

```text
synthetic data
no Mastercard production data
simulation-only
prototype integration
cloud compute limitations
```

This is not weakness.

It increases credibility.

---

# 53. FINAL TASKS

## FINAL-001 — Full Cloud Run

Run the final experiment from a clean commit.

---

## FINAL-002 — Reproduce Results

Run the final evaluation again.

If results materially change:

> investigate.

---

## FINAL-003 — Freeze Artifacts

Create:

```text
artifacts/final/
├── models/
├── metrics/
├── plots/
├── manifests/
├── demo/
└── README.md
```

---

# 54. FINAL-004 — GitHub Freeze

Check:

```text
README
installation
tests
demo
architecture
license
security
```

No secrets.

No API keys.

No credentials.

No private datasets.

---

# 55. FINAL-005 — DOCX

Create:

```text
TeamName.docx
```

matching the Kaggle instructions you supplied.

---

# 56. FINAL-006 — KAGGLE WRITEUP

According to the official instructions you pasted:

```text
Writeup
 ↓
Title
 ↓
Subtitle
 ↓
Project Description
 ↓
Team members + registered emails
 ↓
TeamName.docx
 ↓
Public GitHub TeamName
 ↓
Submit
```

The submission must be **actually submitted**, not merely saved as draft.

---

# 57. FINAL-007 — SUBMISSION AUDIT

Before clicking Submit:

```text
[ ] Team formed
[ ] All members registered
[ ] Names correct
[ ] Registered emails correct
[ ] TeamName.docx uploaded
[ ] GitHub public
[ ] Repository works
[ ] README works
[ ] Demo works
[ ] No secrets
[ ] Tests pass
[ ] Final metrics frozen
[ ] Writeup complete
[ ] Submit button completed
[ ] Confirmation visible
```

---

# 58. CLOUD WORKFLOW

Friend:

```text
git pull
 ↓
Kaggle/Colab
 ↓
execute notebook
 ↓
save artifact
 ↓
manifest
 ↓
metrics
 ↓
commit metadata
 ↓
push
```

Never manually report:

> "training looks good."

Instead:

```text
EXP-014
PR-AUC = 0.xxx
F1 = 0.xxx
ASR = 0.xxx
P99 = xxx ms
```

---

# 59. ARTIFACT RULE

Cloud produces:

```text
model
metrics
manifest
plots
sample data
```

Mac receives only what the UI needs.

This preserves your:

> **Mac = development/integration; Cloud = heavy compute**

rule.

---

# 60. EXACT ANTIGRAVITY MASTER RULE

Antigravity should be instructed:

> **You are an implementation agent inside the Mastercard AI Defense Lab repository. Before modifying anything, read PROJECT_CONTEXT.md, PROJECT_STATUS.md, HANDOFF.md and the assigned TASK_ID. Implement only the assigned task. Do not redesign architecture without explicit approval. Every implementation must have appropriate tests. Never fabricate experiment results. Never claim cloud execution occurred unless an execution artifact exists. After implementation, run the applicable tests, update PROJECT_STATUS.md and create a structured HANDOFF.md entry. Preserve existing interfaces and do not modify unrelated files.**

This should become the project's agent discipline.

---

# 61. EXACT CLAUDE REVIEW ROLE

Claude should receive:

> **Act as an independent technical reviewer. Do not rewrite the architecture. Inspect the assigned TASK_ID, implementation diff, tests and experiment results. Identify correctness bugs, leakage, unrealistic assumptions, unsupported claims, security issues, reproducibility problems and missing tests. Distinguish blocking issues from optional improvements. Do not approve based on complexity or novelty; approve only when the acceptance criteria are satisfied.**

That gives us genuine second-agent review instead of duplicated coding.

---

# 62. STOP/GO GATES

This is probably the most important section.

## GATE 1 — Simulator

### GO

If:

```text
valid data
valid state
hard negatives
fidelity checks
```

### STOP

If:

```text
invalid transactions
leakage
obvious unrealistic distributions
```

---

# 63. GATE 2 — Blue Baseline

### GO

If the model beats the simple baseline.

### STOP

If it doesn't.

Then fix features/data before adding GNN/RL.

---

# 64. GATE 3 — Red

### GO

If attacks are:

```text
valid
realistic
diverse
measurably challenging
```

### STOP

If Red only generates garbage that fools Blue.

---

# 65. GATE 4 — Closed Loop

### GO

If:

```text
ASR decreases
```

while:

```text
legitimate performance
```

doesn't materially deteriorate.

---

# 66. GATE 5 — Advanced Models

Only proceed to:

```text
GNN
PPO
DQN
Diffusion
```

if Tier 1 and Tier 2 pass.

---

# 67. GATE 6 — FINAL

Only claim superiority where:

```text
baseline
vs
ours
```

is statistically/evaluationally supported.

---

# 68. THE FINAL EXPERIMENT MATRIX

Before submission we want something approximately like:

| Experiment | Question                                    |
| ---------- | ------------------------------------------- |
| EXP-001    | Does simulator produce valid transactions?  |
| EXP-002    | Does synthetic data preserve distributions? |
| EXP-003    | Does LightGBM detect baseline fraud?        |
| EXP-004    | Does ensemble beat best GBDT?               |
| EXP-005    | Do temporal features help?                  |
| EXP-006    | Do graph features help?                     |
| EXP-007    | Does intent drift help?                     |
| EXP-008    | Does NSGA-II produce harder attacks?        |
| EXP-009    | Are generated attacks realistic?            |
| EXP-010    | Does adaptive Red outperform static Red?    |
| EXP-011    | Does replay hardening reduce ASR?           |
| EXP-012    | Does hardening preserve old performance?    |
| EXP-013    | Does hidden-family performance hold?        |
| EXP-014    | Does calibration improve decision quality?  |
| EXP-015    | Does the final system meet latency target?  |

These IDs may expand during implementation.

---

# 69. WHAT SUCCESS LOOKS LIKE

The final presentation should not begin:

> "We use LightGBM, XGBoost, CatBoost, HOT-GNN, PPO, NSGA-II, conformal prediction..."

That is technology soup.

Instead:

### Slide/demo story:

```text
HERE IS AN ATTACK
       ↓
BLUE TEAM MISSED IT
       ↓
WE EXPLAINED WHY
       ↓
WE FED IT BACK
       ↓
BLUE HARDENED
       ↓
THE SAME ATTACK FAILED
       ↓
RED ADAPTED
       ↓
BLUE HARDENED AGAIN
```

Then show the measured graph.

That is the actual innovation.

---

# 70. WHAT WE ARE NOT DOING

We are **not**:

* building a production Mastercard payment gateway;
* connecting to real payment rails;
* attacking real payment systems;
* using real customer PII;
* claiming access to Mastercard internal data;
* pretending our simulation is Mastercard's real transaction distribution;
* building ten research models just to list them;
* claiming benchmark superiority without testing;
* spending the last day fixing an unfinished RL system.

---

# 71. CUMULATIVE PROJECT FLOWCHART

Our master flow is now:

```text
STEP 1
Requirements
   │
   ▼
STEP 2
Competitive Intelligence
   │
   ▼
STEP 3
Synthetic Payment World
   │
   ▼
STEP 4
Blue Team
   │
   ▼
STEP 5
Adaptive Red Team
   │
   ▼
STEP 6
Closed-Loop Co-Evolution
   │
   ▼
STEP 7
Architecture + Cloud + Engineering
   │
   ▼
┌─────────────────────────────────────────┐
│ STEP 8                                   │
│                                         │
│ EXECUTION CONTROL                       │
│                                         │
│ Tasks → Code → Tests → Cloud → Evidence │
└────────────────┬────────────────────────┘
                 │
                 ▼
        BASELINE EVIDENCE
                 │
                 ▼
        RED/BLUE EXPERIMENTS
                 │
                 ▼
        CLOSED-LOOP EVIDENCE
                 │
                 ▼
        FINAL ABLATIONS
                 │
                 ▼
        OFFLINE DEMO
                 │
                 ▼
        GITHUB + DOCX
                 │
                 ▼
        KAGGLE WRITEUP
                 │
                 ▼
             SUBMIT
```

---

# 72. STEP 8 FINAL VERDICT

**Step 8 is now finalized.**

More importantly, we have reached the point where additional architecture discussion has diminishing returns.

## We should now start coding.

The first implementation target is **not the simulator at 1 million rows**.

It is:

```text
INF-001
      ↓
INF-002
      ↓
INF-003
      ↓
INF-004
      ↓
INF-005
      ↓
EVAL-001
      ↓
DATA-001
      ↓
DATA-002
```

At the same time, your friend can start the data-side work once the schemas are agreed.

### First milestone:

> **A clean GitHub repository + validated transaction schema + tiny working synthetic world + executable evaluation harness.**

Once that works, we scale.

---

STEP 8 — REQUIRED PATCHES ONLY

Add these at the end of Step 8.

STEP 8 PATCH 1 — TIER-AWARE TASK REGISTRY

Every advanced component must be explicitly tagged:

TIER-1
TIER-2
TIER-3

Example:

BLUE-001   GBDT baseline              TIER-1
BLUE-002   Behavioral features       TIER-1
BLUE-003   Temporal features         TIER-1

RED-001    Attack grammar            TIER-1
RED-002    Mutation engine            TIER-1
RED-003    NSGA-II                   TIER-1

EVAL-001   Three-world harness       TIER-2
EVAL-002   Hidden attacks             TIER-2

GRAPH-001  Relational features       TIER-2
GRAPH-002  GNN                       TIER-3

RL-001     PPO                       TIER-3
RL-002     DQN                       TIER-3

CONT-001   Replay                    TIER-1
CONT-002   ADWIN                     TIER-2/3
CONT-003   EWC                       TIER-3
CONT-004   STG-DGR                   TIER-3

This prevents the AI agents from interpreting every item in Step 7 as mandatory.

STEP 8 PATCH 2 — NEW STOP CONDITIONS

Add:

STOP:
Attack-surface coverage is too narrow.

STOP:
External reality anchor reveals unrealistic simulation.

STOP:
Decision audit trail is incomplete.

STOP:
JSON contract mismatch between Red and Blue.

STOP:
Challenger improves new attacks but causes unacceptable historical forgetting.

STOP:
Cloud experiment cannot be reproduced from its manifest.

STOP:
Advanced model has no measurable improvement over Tier-1/Tier-2 baseline.
STEP 8 PATCH 3 — NEW EVIDENCE REQUIREMENTS

For every experiment, collect:

Experiment ID
Git commit
Config
Seed
Dataset/world version
Hardware
Runtime
Model version
Metrics
Artifact hash
Plots
Conclusion

This is consistent with the existing experiment-register requirement.

STEP 8 PATCH 4 — ADD THE FIVE AUDIT GAPS

These are the five corrections from my previous audit and these should go after Step 8 exactly as you requested.

FINAL PROJECT CORRECTIONS — POST STEP 8
F1 — Attack Surface Coverage Matrix

Every generated attack must be mapped to:

Family
×
Channel/Rail
×
Mechanism
×
Temporal pattern
×
Coordination
×
Agentic context

Report coverage quantitatively.

F2 — Decision Audit Trail

Every Blue decision must record:

transaction_id
risk_score
decision
model_version
feature_version
policy_version
reason_codes
intent_drift
timestamp
F3 — Remove obsolete Kaggle-data wording

The canonical Step 3 is:

Data & Simulation World Design

not conventional Kaggle dataset forensics.

Do not allow an AI agent to assume that the competition provides a conventional fraud train/test dataset.

F4 — Distinguish official requirements from our strategic deliverables

Do not call something an official competition requirement unless the event terms explicitly establish it.

Maintain separate labels:

OFFICIAL REQUIREMENT
STRATEGIC DELIVERABLE
RESEARCH ENHANCEMENT

This prevents accidental overclaiming in the DOCX/Kaggle Writeup.

F5 — Mandatory resumable cloud runs

Every heavy experiment must support:

Checkpoint
↓
Artifact
↓
Manifest
↓
Resume

No critical experiment should depend on one uninterrupted cloud session.

Final verdict

This merged Step 7 is the version I would now freeze.

It is materially better than either version alone:

Latest Step 7 contributed
evidence-first architecture,
claim register,
experiment register,
three-world anti-circularity,
baseline ladder,
measured claims,
Tier 1/2/3 governance,
external reality anchor,
realistic competition framing.
Older Step 7 contributed
concrete engineering contracts,
dynamic compute,
manifests,
JSON interfaces,
streaming/temporal engineering,
detailed replay/provenance,
PSRO/continual-learning options,
ADWIN/STG-DGR/EWC as controlled options,
explicit agent workflow,
repository structure,
CI,
prototype specification,
ENG-01–ENG-25 operational checklist.

The combination is stronger because the older research-heavy items are now subordinate to the evidence gates rather than being assumed to work.

And that's the critical realism check:

We are not promising to implement 25 advanced technologies. We are defining the complete research/engineering space, then forcing the actual implementation through Tier 1 → Tier 2 → Tier 3 gates.

That makes the project realistically achievable.

The current Step 8 does not need a rewrite; it needs the four synchronization changes above plus the five final corrections. Its core structure—task registry, dependency graph, agent roles, Git workflow, cloud workflow, tests, stop/go gates and evidence collection—is already correct.

So when you update your master .md, the correct order is:

STEP 1
STEP 2
STEP 3
STEP 4
STEP 5
STEP 6

STEP 7 — MERGED MASTER SPECIFICATION v2.0
        ↑
        latest Step 7
        +
        missing older Step 7 capabilities
        +
        feasibility gates

STEP 8 — EXECUTION / TASK / SUBMISSION SPECIFICATION
        +
        Step-7 synchronization patches

FINAL PROJECT CORRECTIONS
        F1 — Attack Surface Coverage
        F2 — Decision Audit Trail
        F3 — Step-3 wording correction
        F4 — Official vs strategic requirements
        F5 — Resumable cloud execution

# FINAL ADDITION — DOCUMENT FREEZE & GLOBAL STATUS CONTROL

**Status: FINAL — APPEND TO THE END OF THIS MASTER SPECIFICATION**

This section is the final governance layer for the entire project. It exists to eliminate the remaining ambiguity between mandatory requirements, implementation tiers, experimental candidates, engineering targets, measured results, and official competition requirements.

---

## 1. GLOBAL STATUS VOCABULARY

Every component, requirement, experiment, metric, and architectural decision in this document must use one of the following statuses:

### `OFFICIAL REQUIREMENT`

A requirement explicitly imposed by the competition, submission platform, or official competition instructions.

**Rule:** Must be satisfied.

---

### `FROZEN`

A project-level architectural, methodological, safety, or evaluation decision that has been deliberately locked.

**Rule:** Do not change without explicit project-level approval.

---

### `TIER-1 — CORE`

The minimum implementation required for a valid and competitive end-to-end system.

**Rule:** Must be implemented and validated before Tier-2 or Tier-3 work.

---

### `TIER-2 — ENHANCEMENT`

A meaningful enhancement that may be implemented after Tier-1 is stable.

**Rule:** Implement only when the corresponding Tier-1 acceptance gates pass.

---

### `TIER-3 — RESEARCH SHOWCASE`

An advanced research component such as RL, advanced GNNs, diffusion/generative replay, or equivalent methods.

**Rule:** Never required for project completion. Implement only if Tier-1/Tier-2 results justify the additional complexity and sufficient time remains.

---

### `CANDIDATE`

A technically plausible method under investigation that has not yet earned a place in the final architecture.

**Rule:** No candidate is considered part of the implemented system until experimentally validated.

---

### `TARGET`

A desired engineering or research objective.

Examples:

```text
P99 latency target
ASR reduction target
forgetting target
calibration target
scale target
```

**Rule:** Targets are not results and must never be presented as achieved values.

---

### `MEASURED RESULT`

A value actually produced by an executed experiment with a reproducible configuration.

**Rule:** Only measured results may be used to support performance claims.

---

## 2. SOURCE-OF-TRUTH RULE

The project must maintain the following distinction:

```text
OFFICIAL REQUIREMENTS
        ↓
PROJECT FROZEN DECISIONS
        ↓
TIER-1 CORE
        ↓
TIER-2 ENHANCEMENTS
        ↓
TIER-3 RESEARCH SHOWCASE
```

No research paper, previous architecture proposal, AI-generated recommendation, or candidate technology automatically overrides this hierarchy.

If a conflict occurs:

```text
Official competition requirement
        >
Safety / integrity constraint
        >
Frozen project decision
        >
Tier-1 requirement
        >
Tier-2 enhancement
        >
Tier-3 research idea
        >
Candidate
```

---

# 3. FINAL ARCHITECTURE FREEZE

The central project architecture is now considered complete:

```text
THREAT INTELLIGENCE
        ↓
SYNTHETIC PAYMENT WORLD
        ↓
BLUE TEAM
        ↓
ADAPTIVE RED TEAM
        ↓
ATTACK / DETECTION EVALUATION
        ↓
FAILURE ANALYSIS
        ↓
REPLAY / ADVERSARIAL MEMORY
        ↓
BLUE CHALLENGER
        ↓
PROMOTION GATES
        ↓
NEW BLUE CHAMPION
        ↓
RED RE-ADAPTATION
        ↓
HIDDEN / OOD EVALUATION
        ↓
MEASURED EVIDENCE
```

This architecture is sufficient for the final project.

**No additional major architectural subsystem should be added merely to increase perceived sophistication.**

---

# 4. FINAL IMPLEMENTATION PRIORITY

The implementation order is permanently:

## P0 — Mandatory Core

```text
Repository
Schemas
Synthetic payment world
Validation harness
Blue baseline
Behavioral features
Temporal features
Attack grammar
Mutation / mutability controls
Core Red attacks
Blue evaluation
Failure analysis
Replay
Champion / Challenger
Promotion gates
Prototype
Reproducible experiment artifacts
```

## P1 — High-Value Enhancements

```text
Relational intelligence
Graph attack scenarios
Agentic intent drift
Attack fidelity scoring
Novelty scoring
Hidden attacks
OOD evaluation
Decision audit trail
Advanced Red optimization
```

## P2 — Research Enhancements

```text
Advanced GNN
PSRO / Stackelberg co-play
ADWIN
Conformal uncertainty
Advanced continual-learning methods
```

## P3 — Optional Research Showcase

```text
PPO
DQN
Diffusion
STG-DGR
Generative replay
Other advanced research models
```

If time or compute becomes constrained, remove work from **P3 → P2 → P1** in that order.

**Never sacrifice P0 to complete P2/P3.**

---

# 5. UNIVERSAL EXPERIMENT RULE

Every non-trivial component must follow:

```text
BASELINE
   ↓
COMPONENT ADDED
   ↓
CONTROLLED EXPERIMENT
   ↓
ABLATION
   ↓
MEASURED BENEFIT
   ↓
COMPLEXITY / LATENCY / COMPUTE COST
   ↓
KEEP / REMOVE
```

A component must be removed when its measured benefit does not justify its complexity.

Complexity alone is never evidence of innovation.

---

# 6. UNIVERSAL CLAIM RULE

The project must distinguish:

```text
TARGET
≠
RESULT
≠
CLAIM
```

The following may never be claimed without corresponding evidence:

```text
specific latency guarantee
specific ASR reduction
specific forgetting guarantee
state-of-the-art performance
superiority over Mastercard systems
production Mastercard integration
production EMV 3DS integration
production agentic-payment integration
RL superiority
GNN superiority
formal privacy guarantee
formal security guarantee
continuous online learning
```

unless the project has actually implemented, measured, and documented the relevant capability.

Research papers may justify **why a method was investigated**.

They do not establish **our project's performance**.

---

# 7. FINAL ATTACK VALIDITY RULE

An attack is not considered successful merely because it fools Blue.

Every attack must satisfy, where applicable:

```text
Valid transaction state
+
Valid world constraints
+
Mutability constraints
+
Behavioral plausibility
+
Temporal plausibility
+
Relational plausibility
+
Attack-family validity
+
Required authorization/context constraints
```

Therefore:

```text
REALISTIC ATTACK
        +
BLUE EVASION
        =
VALID ADVERSARIAL RESULT
```

not:

```text
BLUE EVASION
        =
VALID ATTACK
```

This prevents the Red Team from becoming a generator of unrealistic adversarial garbage.

---

# 8. FINAL ANTI-CIRCULARITY RULE

The evaluation system must prevent the project from proving its own assumptions.

Where feasible, maintain separation between:

```text
TRAIN / ADAPTATION WORLD
        ↓
VALIDATION WORLD
        ↓
HIDDEN / OOD TEST WORLD
```

The Red Team must not be allowed to optimize directly against the final hidden evaluation set.

The final evaluation must contain attacks or variants not directly used to train the final champion.

---

# 9. FINAL DECISION AUDIT TRAIL

Every important Blue decision must be traceable through:

```text
transaction_id
risk_score
decision
model_version
feature_version
policy_version
reason_codes
intent_drift
timestamp
```

Where applicable, the corresponding Red attack must also retain:

```text
attack_id
attack_family
parent_attack_id
seed
mutation_parameters
world_version
generator_version
objective_values
fidelity_score
novelty_score
evasion_result
```

This creates end-to-end lineage:

```text
ATTACK
  ↓
TRANSACTION
  ↓
BLUE DECISION
  ↓
FAILURE / SUCCESS
  ↓
REPLAY
  ↓
CHALLENGER
  ↓
PROMOTION
```

---

# 10. FINAL EVIDENCE REQUIREMENT

Every final experiment must retain:

```text
Experiment ID
Git commit
Configuration
Seed
Dataset / world version
Hardware
Runtime
Model version
Feature version
Metrics
Artifact hash
Plots
Conclusion
```

Cloud execution is considered valid only when the corresponding artifacts exist.

Statements such as:

> “training worked”

or

> “the model performed better”

are not acceptable evidence.

The project must report actual measured values.

---

# 11. FINAL STOP / GO RULES

### STOP — Simulator

If:

```text
invalid transactions
data leakage
unrealistic distributions
broken state transitions
```

are discovered.

### STOP — Blue

If the core model does not outperform the simple baseline.

Fix:

```text
data
features
validation
```

before adding advanced models.

### STOP — Red

If attacks are unrealistic, invalid, narrow, or only exploit simulator artifacts.

### STOP — Closed Loop

If:

```text
ASR does not improve
OR
false positives become unacceptable
OR
historical performance collapses
OR
OOD performance deteriorates materially
```

### STOP — Advanced Models

If an advanced model provides no meaningful measured improvement over the simpler validated system.

### STOP — Submission

If final claims cannot be reproduced from the submitted repository and artifacts.

---

# 12. FINAL DEMONSTRATION REQUIREMENT

The primary demonstration must tell one coherent story:

```text
1. Start system
2. Show legitimate activity
3. Activate Red Team
4. Generate realistic attack
5. Show attack
6. Show Blue detection
7. Demonstrate one successful evasion
8. Explain why it succeeded
9. Store the failure
10. Train / evaluate Challenger
11. Apply promotion gates
12. Promote only if gates pass
13. Re-attack with same-family unseen variant
14. Demonstrate measured change
15. Evaluate hidden/OOD attack
16. Show historical-performance retention
```

The demonstration must not depend on live internet connectivity, external APIs, or Kaggle availability.

A complete offline artifact pack must exist.

---

# 13. FINAL SAFETY BOUNDARY

The project operates only on:

```text
Synthetic data
Anonymized data
Authorized competition data
Controlled simulation
```

The project must never use:

```text
Real cardholder data
Real PII
Production payment data
Live payment-system attacks
Unauthorized third-party systems
```

The resulting system is a:

> **controlled payment-security research and evaluation laboratory**

and not a live attack platform.

---

# 14. FINAL SUBMISSION INTEGRITY CHECK

Before submission, verify:

```text
[ ] Official requirements satisfied
[ ] Team information correct
[ ] Public GitHub repository available
[ ] Repository installs successfully
[ ] README works
[ ] Demo works
[ ] Tests pass
[ ] No secrets
[ ] No credentials
[ ] No private datasets
[ ] Final models/artifacts frozen
[ ] Experiment manifests included
[ ] Final metrics reproducible
[ ] Technical report complete
[ ] Limitations disclosed
[ ] Claims supported by evidence
[ ] DOCX generated correctly
[ ] Kaggle writeup complete
[ ] GitHub URL correct
[ ] Submission completed
[ ] Submission confirmation verified
```

---

# 15. FINAL PROJECT DEFINITION

The final project should be described as:

> **A controlled adversarial payment-security laboratory that identifies emerging attack surfaces, generates constrained and measurable synthetic attacks, evaluates their fidelity and evasion capability, detects them using a multi-signal defense, records failures as reusable adversarial knowledge, and evaluates whether subsequent defensive challengers become measurably more robust without unacceptable degradation of legitimate-customer performance.**

The project is **not** defined by how many advanced algorithms it contains.

It is defined by whether it can demonstrate:

```text
REALISTIC ATTACK
      ↓
DEFENSE FAILURE
      ↓
EXPLANATION
      ↓
MEMORY
      ↓
HARDENING
      ↓
VALIDATION
      ↓
MEASURABLE IMPROVEMENT
      ↓
UNSEEN RE-ATTACK
```

---

# 16. FINAL FREEZE STATEMENT

**This document is now the master project specification.**

From this point forward:

1. **Do not reopen the architecture without evidence of a blocking problem.**
2. **Do not add technology merely for novelty.**
3. **Do not treat targets as results.**
4. **Do not claim capabilities that were not implemented and measured.**
5. **Do not sacrifice Tier-1 reliability for Tier-3 sophistication.**
6. **Do not allow unrealistic Red attacks to inflate performance.**
7. **Do not allow test-set leakage into adaptive training.**
8. **Do not claim cloud execution without artifacts.**
9. **Do not modify frozen decisions silently.**
10. **Every final competitive claim must be traceable to reproducible evidence.**

## **FINAL STATUS: READY FOR IMPLEMENTATION**

The architecture, evaluation framework, engineering controls, evidence requirements, prototype direction, safety boundary, and submission governance are now considered **complete and frozen**.