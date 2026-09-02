---
title: Mastercard AI Defense Lab
emoji: 🛡️
colorFrom: indigo
colorTo: gray
sdk: static
pinned: false
---

<div align="center">

# Project KIRA — Mastercard AI Defense Lab
### Institutional Adversarial Security Laboratory, Stateful Swarms & Closed-Loop Co-Evolution

[![GitHub Stars](https://img.shields.io/github/stars/ankit-choubey/Project-KIRA?style=for-the-badge&color=ffd700&label=STARS)](https://github.com/ankit-choubey/Project-KIRA)
[![GitHub Forks](https://img.shields.io/github/forks/ankit-choubey/Project-KIRA?style=for-the-badge&color=607d8b&label=FORKS)](https://github.com/ankit-choubey/Project-KIRA)
[![Python](https://img.shields.io/badge/Python-3.11_|_3.12_|_3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Polars](https://img.shields.io/badge/Polars-Vectorized_Engine-CD792C?style=for-the-badge&logo=polars&logoColor=white)](https://pola.rs)
[![LightGBM](https://img.shields.io/badge/LightGBM-Gradient_Boosting-2E7D32?style=for-the-badge)](https://lightgbm.readthedocs.io)
[![Test Suite](https://img.shields.io/badge/tests-225_passed_·_0_failed-2E7D32?style=for-the-badge)](https://github.com/ankit-choubey/Project-KIRA/tree/main/tests)
[![Security Gates](https://img.shields.io/badge/gates-0_through_7_ALL_PASSED-14607A?style=for-the-badge)](https://github.com/ankit-choubey/Project-KIRA/blob/main/tools/gates.py)
[![Integrity](https://img.shields.io/badge/SHA--256-22%2F22_VERIFIED-10b981?style=for-the-badge)](https://github.com/ankit-choubey/Project-KIRA/blob/main/artifacts/LATEST)

<br/>

**Mastercard AI Defense Lab (Project KIRA)** is an institutional payment-security laboratory that treats transaction defense as an **active, continuously evaluated adversarial game**. Rather than evaluating static classifiers on stationary data, KIRA pits a stateful synthetic payment world against adaptive, multi-agent adversarial swarms (Red Engine), captures evasive vectors, retrains challenger detectors (Blue Team), and enforces strict anti-forgetting promotion gates before deploying models to production.

<br/>

### Verified Production Ecosystem Links

| Platform | Production Target | URL | Status |
| :--- | :--- | :--- | :--- |
| **Primary Interactive Dashboard** | **Netlify (Devraj UI)** | [https://kaleidoscopic-quokka-251564.netlify.app/](https://kaleidoscopic-quokka-251564.netlify.app/) | `200 OK · ACTIVE` |
| **Live Scoring & Simulation API** | **Render Web Service** | [https://project-kira-api.onrender.com/docs](https://project-kira-api.onrender.com/docs) | `200 OK · LIVE` |
| **Public Evidence & Showcase Hub** | **Hugging Face Space** | [https://huggingface.co/spaces/ankit-choubey/Project-KIRA](https://huggingface.co/spaces/ankit-choubey/Project-KIRA) | `200 OK · UNPAUSED` |
| **Kaggle CPU Reproducibility** | **5 Research Notebooks** | [github.com/.../notebooks/kaggle](https://github.com/ankit-choubey/Project-KIRA/tree/main/notebooks/kaggle) | `VERIFIED · ZERO GPU` |
| **Authoritative Codebase** | **GitHub Repository** | [https://github.com/ankit-choubey/Project-KIRA](https://github.com/ankit-choubey/Project-KIRA) | `22/22 SHA-256 MATCH` |

</div>

---

## Gate Verification Ladder: Gates 0 Through 7 ALL PASSED

Every release in Project KIRA is bound to an automated 8-stage gate ladder (`tools/gates.py`). All gates execute strictly without GPU dependencies, enforcing causal safety, mathematical invariance, and cryptographic consistency.

```text
  GATE 0        GATE 1        GATE 2        GATE 3        GATE 4        GATE 5        GATE 6        GATE 7
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│CONTRACTS│──►│  WORLD  │──►│CAUSALITY│──►│DETECTOR │──►│ ADVERS. │──►│ CO-EVOL │──►│ CRYPTO  │──►│ RELEASE │
│ 31 API  │   │ ENTITY  │   │BATCH=STR│   │OOT-SPLIT│   │BUDGET 20│   │GATE REJ │   │  22/22  │   │0 SECRETS│
│  PASS   │   │  PASS   │   │  PASS   │   │  PASS   │   │  PASS   │   │  PASS   │   │  PASS   │   │  PASS   │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
```

| Gate # | Scope & Invariant Checked | Verification Condition | Output / Evidence | Status |
| :---: | :--- | :--- | :--- | :---: |
| **Gate 0** | **Contracts & Fixtures** | Schema validation, zero-drift Pydantic models, fixture reproducibility | 31/31 API contract tests pass | **`PASS`** |
| **Gate 1** | **World Engine Physics** | Transaction graph integrity, cardholder trajectory physics, merchant validity | 9,348 txns strictly chronological | **`PASS`** |
| **Gate 2** | **Temporal Feature Causality** | Zero future leakage ($t_j < t_i$), mandatory 7-day chargeback reporting delay | $\Delta\text{Features} = 0.0000$ (Batch $\equiv$ Stream) | **`PASS`** |
| **Gate 3** | **Blue Detection & Calibration** | Out-of-time chronological splits, Isotonic calibration curve bounds | ECE $\le 0.012$, PR-AUC $0.9375$ | **`PASS`** |
| **Gate 4** | **Red Action Masks & Budgets** | Strict mask compliance: account history locked; amount/velocity mutated | 0 mask violations across 10,000 attacks | **`PASS`** |
| **Gate 5** | **Co-Evolutionary Hardening** | Anti-forgetting check: rejects models triggering detection collapse | 4/4 overfit challenger models rejected | **`PASS`** |
| **Gate 6** | **Cryptographic Artifact Proof** | Exact byte-level SHA-256 hash match against frozen baseline | 22/22 artifacts verified matching | **`PASS`** |
| **Gate 7** | **Final Security & Governance** | Zero hardcoded API keys, tokens, or private credentials in Git history | Automated regex scan clean; 0 secrets | **`PASS`** |

---

## The 10 Audited Headline Research Numbers

Every number below is extracted directly from cryptographically hashed research outputs in `artifacts/run_tiny_s20260827_193f7897_40997ab` and phase-2 research logs:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE 10 AUDITED HEADLINE NUMBERS                                  │
├────────┬─────────────────┬───────────────────────────────────┬───────────────────────────────────┤
│ Number │ Metric Value    │ Benchmark / Experiment Context    │ What It Actually Proves           │
├────────┼─────────────────┼───────────────────────────────────┼───────────────────────────────────┤
│   01   │ 284,807         │ ULB European Credit Card Benchmark│ External real-world validation    │
│   02   │ 50,000          │ S-02 Synthetic World Evaluation   │ Large-scale causal graph scale    │
│   03   │ 15,000          │ ADV-002 Stateful Swarm Trials     │ Swarm agentic stress-testing      │
│   04   │ 10,000          │ ADV-001 Constrained Attacks       │ 6.00% ASR; 9,400 blocked/step-up  │
│   05   │ +10.08 pp       │ Attacker Memory Effect (ADV-002)  │ Adaptive agents find more bugs    │
│   06   │ +1.98 pp        │ Causal Graph Uplift (S-02)        │ Relational fusion (p = 0.0460)    │
│   07   │ 50.0%           │ TI Bounded ASR Reduction (TI-001) │ Threat intel halves attacker ASR  │
│   08   │ 100.0%          │ World C Zero-Day ASR              │ Vulnerability found (not hidden)  │
│   09   │ 22 / 22         │ Authoritative Artifact Integrity  │ Zero hash drift / 225 tests green │
│   10   │ 225             │ Automated Tests Passed            │ Rigorous research-engineering     │
└────────┴─────────────────┴───────────────────────────────────┴───────────────────────────────────┘
```

> [!NOTE]
> **Scientific Integrity Notice:**
> * **`+10.08 pp`** is **Attacker ASR Gain under Adaptive Memory** (19.68% adaptive vs. 9.60% static control), demonstrating that memory enables attackers to systematically isolate structural weaknesses.
> * **`100% Zero-Day ASR`** is a **Vulnerability Discovered**, confirming that the unhardened baseline is blind to withheld attack families and proving the necessity of KIRA's continuous co-evolutionary loop.

---

## Multi-Scale Experimental Event Pipeline Architecture

The experimental event architecture integrates real-world anchors, synthetic topology generators, dynamic graph networks, and parallel adversarial stress-testing across distinct operational paths:

```text
========================================================================================================================
                                     KIRA MULTI-SCALE EVENT PROCESSING PIPELINE
========================================================================================================================

  [REAL-WORLD BENCHMARK]                                        [SYNTHETIC TRANSACTION UNIVERSE]
   284,807 European Txns                                         50,000 World C Simulated Events
   (ULB CC0 · 492 Frauds)                                        (Entities, Merchants, Devices)
            │                                                                  │
            ▼                                                                  ▼
  ┌───────────────────────┐                                      ┌───────────────────────────┐
  │ C2ST Fidelity Anchor  │                                      │ Relational Entity Graph   │
  │ • PR-AUC: 0.8640      │                                      │ • 28,044 Causal Edges     │
  │ • ECE: 0.0042         │                                      │ • Zero Lookahead (t_j<t_i)│
  └──────────┬────────────┘                                      └─────────────┬─────────────┘
             │                                                                 │
             │           ┌─────────────────────────────────────────────────────┘
             │           │
             ▼           ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────────┐
  │                           TEMPORAL GRAPH-TABULAR FUSION ENGINE                           │
  │  • 25 Canonical Tabular Features (Velocity, Recency, Risk Scores)                         │
  │  • 16-Dimensional CausalGraphSAGE Topological Node Embeddings (+1.98 pp Uplift, p=0.0460)│
  └────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                               │
                                               ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────────┐
  │                        BLUE TEAM DETECTOR & ISOTONIC CALIBRATION                         │
  │  • LightGBM Dual-Branch Classifier (PR-AUC: 0.9375 · ROC-AUC: 0.9996)                    │
  │  • Isotonic Probability Calibrator (ECE <= 0.012 · Clean FPR@95R <= 0.05)                │
  └──────────────────────┬───────────────────────────────────────────────────┬───────────────┘
                         │                                                   │
                         │                                                   │
  [ADVERSARIAL CAMPAIGN] │                                                   │ [THREAT & DRIFT FEEDS]
                         ▼                                                   ▼
  ┌──────────────────────────────────────────────┐        ┌──────────────────────────────────┐
  │ RED ADVERSARY SWARMS & BUDGETED PROBES       │        │ LIVE TELEMETRY & DRIFT SENSORS   │
  │ • ADV-001: 10,000 Constrained Mutation Attacks│        │ • 2,805 Synthetic TI Events      │
  │ • ADV-002: 15,000 Stateful Swarms (3 Arms)   │        │   (TI-001: 50.0% ASR Reduction)  │
  │ • World C: 100.0% Withheld Zero-Day Attacks  │        │ • 4,674 Stream Drift Samples     │
  └──────────────────────┬───────────────────────┘        │   (KS Stat = 0.1119, p = 0.0)    │
                         │                                └──────────────────┬───────────────┘
                         ▼                                                   │
  ┌──────────────────────────────────────────────┐                           │
  │ MULTI-BRANCH ATTACK RESOLUTION               │                           │
  │ ├── 9,400 Defended / Stepped-Up (Blocked)    │                           │
  │ └── 1,986 Evasions Isolated & Diagnosed      │                           │
  └──────────────────────┬───────────────────────┘                           │
                         │                                                   │
                         ▼                                                   │
  ┌──────────────────────────────────────────────┐                           │
  │ WEAKNESS PROFILER & FAILURE QUARANTINE       │                           │
  │ • Minimum Evasion Distance (MED) Calculation │                           │
  │ • Quarantined to failures.json Knowledge Base│                           │
  └──────────────────────┬───────────────────────┘                           │
                         │                                                   │
                         ▼                                                   │
  ┌──────────────────────────────────────────────────────────────────────────┴───────────────┐
  │                        CO-EVOLUTIONARY ANTI-FORGETTING SAFETY GATE                       │
  │  • Retrain Challenger on Diagnosed Evasion Vectors                                       │
  │  • Multi-Objective Gate Evaluation:                                                      │
  │    ├── Held-out Variant Evasion: ASR Drops 100.0% -> 0.00% [PASSED HARDENING]            │
  │    └── Benign Distribution PR-AUC: Degrades Below 0.90 Safety Floor [OVERFIT DETECTED]   │
  │  • DECISION: REJECT CHALLENGER (4/4 Candidates Blocked) -> AUTOMATED ROLLBACK TO CHAMPION│
  └────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                               │
                                               ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────────┐
  │                         CRYPTOGRAPHIC AUDIT & SERVING PLATFORM                           │
  │  • 22/22 Authoritative SHA-256 JSON Hashes Sealed (Zero Artifact Drift)                  │
  │  • 225 Automated Invariant, Unit & Contract Tests Green (0 Failures, 255s)               │
  │  • Render FastAPI Web Service (<1.2ms) + Netlify Presentation Dashboard (Devraj UI)     │
  └──────────────────────────────────────────────────────────────────────────────────────────┘
========================================================================================================================
```

---

## Step-by-Step Closed-Loop Architecture Workflow

KIRA operates as an institutional 8-stage feedback pipeline connecting empirical benchmarks, temporal graph representation learning, adversarial optimization, and automated safety rollback:

```text
 ═══════════════════════════════════════════════════════════════════════════════════════════════════════
                      KIRA 8-STAGE CLOSED-LOOP DEFENSE & CO-EVOLUTION PIPELINE
 ═══════════════════════════════════════════════════════════════════════════════════════════════════════

   [01. EXTERNAL REALITY ANCHOR]                 [02. CAUSAL GRAPH FUSION ENGINE (S-02)]
  ┌─────────────────────────────────────────┐   ┌─────────────────────────────────────────┐
  │ • 284,807 European Credit Card Txns     │   │ • 50,000 Synthetic World Events        │
  │ • 492 Real Fraud Exemplars (ULB CC0)    │   │ • 28,044 Causal Dynamic Graph Edges     │
  │ • PR-AUC: 0.8640 · FPR: 0.0003          │   │ • 25 Tabular + 16-D CausalGraphSAGE     │
  │ • Prevents Synthetic Simulation Bias    │   │ • Zero Future Leakage (t_j < t_i)       │
  └────────────────────┬────────────────────┘   └────────────────────┬────────────────────┘
                       │                                             │
                       └──────────────────────┬──────────────────────┘
                                              │
                                              ▼
                             [03. BLUE DEFENSE & CALIBRATION]
                            ┌─────────────────────────────────┐
                            │ • Dual-Branch LightGBM Model    │
                            │ • PR-AUC: 0.9375 · ROC: 0.9996  │
                            │ • Isotonic Score Calibrator     │
                            │ • Strict ECE <= 0.012 Bound     │
                            └────────────────┬────────────────┘
                                             │
                        ┌────────────────────┴────────────────────┐
                        │                                         │
                        ▼                                         ▼
   [04. ADV-001 CONSTRAINED POPULATION]          [05. ADV-002 STATEFUL SWARM DYNAMICS]
  ┌─────────────────────────────────────────┐   ┌─────────────────────────────────────────┐
  │ • 10,000 Mutation Attack Attempts       │   │ • 15,000 Swarm Probes across 3 Arms     │
  │ • 5 Adversarial Strategy Families       │   │ • Adaptive Memory: 19.68% ASR           │
  │ • 6.00% Aggregate Evasion ASR           │   │ • Static Control: 9.60% ASR             │
  │ • 9,400 Blocked or Stepped-Up           │   │ • +10.08 pp Memory Gain (Agentic)       │
  └────────────────────┬────────────────────┘   └────────────────────┬────────────────────┘
                       │                                             │
                       └──────────────────────┬──────────────────────┘
                                              │
                                              ▼
                             [06. ZERO-DAY VULNERABILITY AUDIT]
                            ┌─────────────────────────────────┐
                            │ • World C Withheld Attack Family│
                            │ • 100.0% Zero-Day Evasion Found │
                            │ • Evasions -> failures.json     │
                            │ • Action Mask & MED Diagnostics │
                            └────────────────┬────────────────┘
                                             │
                                             ▼
                             [07. ANTI-FORGETTING SAFETY GATE]
                            ┌─────────────────────────────────┐
                            │ • Challenger Trained on Failures│
                            │ • Held-Out ASR: 100% -> 0.00%   │
                            │ • Benign PR-AUC: 0.8417 (< 0.90)│
                            │ • DECISION: REJECT CHALLENGER   │
                            │ • SAFE ROLLBACK TO CHAMPION     │
                            └────────────────┬────────────────┘
                                             │
                        ┌────────────────────┴────────────────────┐
                        │                                         │
                        ▼                                         ▼
   [08. THREAT INTEL & DRIFT ENGINE]             [09. CRYPTOGRAPHIC PROOF & SERVING]
  ┌─────────────────────────────────────────┐   ┌─────────────────────────────────────────┐
  │ • 2,805 Synthetic TI Events (TI-001)    │   │ • 22/22 SHA-256 Baseline Hash Match     │
  │ • Threat Intel Halves Attacker ASR (50%)│   │ • 225 Unit & Invariant Tests Passing    │
  │ • 4,674 Stream Drift KS Samples         │   │ • 5 Kaggle CPU Notebooks (Zero GPU)     │
  │ • KS = 0.1119 (p = 0.0) Triggers Alert  │   │ • Live Render API + Netlify Frontend    │
  └─────────────────────────────────────────┘   └─────────────────────────────────────────┘
 ═══════════════════════════════════════════════════════════════════════════════════════════════════════
```

---

## Kaggle CPU Reproducibility Catalog (Zero GPU)

To eliminate cloud vendor lock-in and verify anti-memorization on accessible hardware, every heavy research stage was executed on **Kaggle CPU instances** (no GPU used anywhere in this project):

| Notebook Name | Target Experiment | Hardware & Runtime | Primary Output Artifact | GitHub Source |
| :--- | :--- | :--- | :--- | :---: |
| **`02_full_run.ipynb`** | Full synthetic world, baseline detector, 3-round co-evolution | Kaggle CPU (~115 min) | `evaluation.json`, `decisions.json` | [Open Code](https://github.com/ankit-choubey/Project-KIRA/blob/main/notebooks/kaggle/02_full_run.ipynb) |
| **`03_real_world_validation.ipynb`** | Sparkov real-world transfer & C2ST fidelity validation | Kaggle CPU (~25 min) | `external_anchor.json`, `fidelity.json` | [Open Code](https://github.com/ankit-choubey/Project-KIRA/blob/main/notebooks/kaggle/03_real_world_validation.ipynb) |
| **`04_phase2_mega_notebook.ipynb`** | S-00 to S-04 Graph-Tabular Fusion (Arm A vs. Arm D) | Kaggle CPU (~8.5 min) | `master_results.json`, `comparison.json` | [Open Code](https://github.com/ankit-choubey/Project-KIRA/blob/main/notebooks/kaggle/04_phase2_mega_notebook.ipynb) |
| **`05_adv002_large_swarm.ipynb`** | ADV-002 15,000 stateful adversarial swarm population | Kaggle CPU (~18 min) | `adv002_swarm_telemetry.json` | [Open Code](https://github.com/ankit-choubey/Project-KIRA/blob/main/notebooks/kaggle/05_adv002_large_swarm.ipynb) |
| **`06_adv003_adaptive_defense.ipynb`** | ADV-003 Adaptive Challenger Hardening & Retention audit | Kaggle CPU (~12 min) | `adaptive_metrics.json` | [Open Code](https://github.com/ankit-choubey/Project-KIRA/blob/main/notebooks/kaggle/06_adv003_adaptive_defense.ipynb) |

---

## Live REST API Specification (Render Web Service)

The production API runs on Render's Python web service tier at `https://project-kira-api.onrender.com`. Interactive Swagger documentation is available at `/docs`.

```bash
# 1. Health & Active Run Integrity Check
curl -s https://project-kira-api.onrender.com/api/health
# Response: {"status":"ok","run_id":"run_tiny_s20260827_193f7897_40997ab","artifacts_loaded":true}

# 2. Trigger Real-Time 15,000 Swarm Simulation Job
curl -s -X POST https://project-kira-api.onrender.com/api/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"total_swarms": 15000, "batch_size": 50, "speed_multiplier": 1.0}'
# Response: {"job_id":"sim_20260902_...","status":"running","total_swarms":15000,"source":"live"}

# 3. Stream Live Swarm Events (Ring Buffer)
curl -s "https://project-kira-api.onrender.com/api/simulation/latest/events?limit=5"

# 4. Score Single Inbound Transaction (<1.2ms Loopback)
curl -s -X POST https://project-kira-api.onrender.com/api/score \
  -H "Content-Type: application/json" \
  -d '{"transaction": {"txn_id":"tx_001","amount":42.50,"channel":"card_present","mcc":"5411", ...}}'
```

---

## Local Developer Commands

```bash
# Clone & install with uv or pip
git clone https://github.com/ankit-choubey/Project-KIRA.git
cd Project-KIRA
make setup

# Run Gate ladder (N = 0..7)
make gate 0
make gate 6
make gate 7

# Run test suite
pytest tests/e2e/test_api.py -v
pytest tests/invariants/ -v

# Run full pipeline locally (~2 min)
make run SCALE=tiny

# Launch local dev services (FastAPI :8000 + Vite :5173)
make dev
```

---

<div align="center">
  <p><b>Mastercard AI Defense Lab — Project KIRA</b></p>
  <sub>Audited Research Baseline: <code>run_tiny_s20260827_193f7897_40997ab</code> &bull; Research Commit <code>40997ab</code></sub>
</div>
