---
title: Mastercard AI Defense Lab
emoji: 🛡️
colorFrom: indigo
colorTo: gray
sdk: static
pinned: false
---

<div align="center">

# 🛡️ Project KIRA — Mastercard AI Defense Lab
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

### 🌐 Verified Production Ecosystem Links

| Platform | Production Target | URL | Status |
| :--- | :--- | :--- | :--- |
| **Primary Interactive Dashboard** | **Netlify (Devraj UI)** | [https://kaleidoscopic-quokka-251564.netlify.app/](https://kaleidoscopic-quokka-251564.netlify.app/) | `200 OK · ACTIVE` |
| **Live Scoring & Simulation API** | **Render Web Service** | [https://project-kira-api.onrender.com/docs](https://project-kira-api.onrender.com/docs) | `200 OK · LIVE` |
| **Public Evidence & Showcase Hub** | **Hugging Face Space** | [https://huggingface.co/spaces/ankit-choubey/Project-KIRA](https://huggingface.co/spaces/ankit-choubey/Project-KIRA) | `200 OK · UNPAUSED` |
| **Kaggle CPU Reproducibility** | **5 Research Notebooks** | [github.com/.../notebooks/kaggle](https://github.com/ankit-choubey/Project-KIRA/tree/main/notebooks/kaggle) | `VERIFIED · ZERO GPU` |
| **Authoritative Codebase** | **GitHub Repository** | [https://github.com/ankit-choubey/Project-KIRA](https://github.com/ankit-choubey/Project-KIRA) | `22/22 SHA-256 MATCH` |

</div>

---

## 🎖️ Gate Verification Ladder: Gates 0 Through 7 ALL PASSED

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

## 📊 The 10 Audited Headline Research Numbers

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

## 📈 High-Density Experimental Event Scale

```text
====================================================================================================
                              KIRA EXPERIMENTAL SCALE & EVENT VOLUME
====================================================================================================

  [284,807]  Real-World Credit Card Benchmark Transactions (ULB 2015 · 492 Real Frauds)
     │
  [50,000]   Synthetic World C Transactions (S-02 Relational Graph Evaluation)
     │
  [28,044]   Causal Dynamic Graph Edges (Zero Future-Read Violations Verified)
     │
  [15,000]   Stateful Adversarial Swarm Probes (ADV-002 · 5 Agents · 3 Arms · 100 Rounds)
     │
  [10,000]   Constrained Adversarial Attacks (ADV-001 · 5 Mutation Families)
     │
  [9,400]    Evasion Attacks Blocked or Stepped-Up by Blue Fusion Detector
     │
  [4,674]    Stream Drift Monitoring Samples (KS Statistic = 0.1119, p = 0.0)
     │
  [2,805]    Synthetic Threat Intelligence Enrichment Events (TI-001)
     │
  [1,986]    Adversarial Swarm Evasions Captured and Quarantined into failures.json
     │
  [225]      Automated Tests Passing Cleanly Across Unit, Invariant & API Suites (0 Failures)
     │
  [22]       Authoritative JSON Artifacts Sealed with SHA-256 Signatures (22/22 Match)
     │
  [0]        Catastrophic Degradations Allowed: 4/4 Overfit Challenger Models Rejected

====================================================================================================
```

---

## 🏗️ Step-by-Step Closed-Loop Architecture Workflow

KIRA operates as an integrated, 8-stage feedback pipeline connecting empirical benchmarks, temporal graph representation learning, adversarial optimization, and automated safety rollback:

```text
                 ┌────────────────────────────────────────────────────────┐
                 │          01. EXTERNAL REAL-WORLD REALITY ANCHOR        │
                 │   • 284,807 European Credit Card Transactions (ULB)    │
                 │   • PR-AUC: 0.8640 · FPR: 0.0003 · ECE: 0.0042         │
                 │   • Prevents simulator overfitting to synthetic world  │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │           02. DEFENSIVE GRAPH FUSION ENGINE (S-02)     │
                 │   • 25 Tabular Features + 16-dim CausalGraphSAGE       │
                 │   • Dual-branch fusion yields +1.98 pp PR-AUC uplift   │
                 │   • Strictly enforces t_j < t_i (Zero future leakage)  │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │          03. RED ADVERSARY POPULATION (ADV-001)        │
                 │   • 10,000 constrained mutation attack attempts        │
                 │   • 6.00% aggregate ASR · 30.00% geo_hop ASR           │
                 │   • 9,400 attacks blocked or stepped-up by Blue        │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │          04. STATEFUL SWARM DYNAMICS (ADV-002)         │
                 │   • 15,000 swarm attempts across 3 controlled arms     │
                 │   • Adaptive Memory (19.68%) vs. Static Control (9.60%)│
                 │   • +10.08 pp adaptive gain proves agentic learning    │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │          05. ZERO-DAY VULNERABILITY DISCOVERY          │
                 │   • World C withheld attack family evaluation          │
                 │   • 100.0% ASR against unexposed baseline detector     │
                 │   • Evasions quarantined into failures.json store      │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │          06. ANTI-FORGETTING SAFETY GATE (THE LOOP)    │
                 │   • Challenger retrains on diagnosed failure mutations │
                 │   • Held-out variant ASR drops to 0.00% (Hardened)     │
                 │   • BUT clean PR-AUC degrades below 0.90 safety floor  │
                 │   • GATE REJECTS CHALLENGER: Rollback protects system  │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │          07. THREAT INTELLIGENCE & DRIFT ENGINE        │
                 │   • Synthetic TI feed enrichment (TI-001) cuts ASR 50% │
                 │   • Two-sample KS test detects distribution shift      │
                 │   • KS = 0.1119 (p = 0.0) triggers retraining alerts   │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │          08. CRYPTOGRAPHIC VERIFICATION & EVIDENCE     │
                 │   • 225 automated unit, invariant & API tests passed   │
                 │   • 22/22 SHA-256 hash match against frozen baseline   │
                 │   • 5 Kaggle CPU research notebooks (100% reproducible)│
                 └────────────────────────────────────────────────────────┘
```

---

## 🔬 Kaggle CPU Reproducibility Catalog (Zero GPU)

To eliminate cloud vendor lock-in and verify anti-memorization on accessible hardware, every heavy research stage was executed on **Kaggle CPU instances** (no GPU used anywhere in this project):

| Notebook Name | Target Experiment | Hardware & Runtime | Primary Output Artifact | GitHub Source |
| :--- | :--- | :--- | :--- | :---: |
| **`02_full_run.ipynb`** | Full synthetic world, baseline detector, 3-round co-evolution | Kaggle CPU (~115 min) | `evaluation.json`, `decisions.json` | [Open Code](https://github.com/ankit-choubey/Project-KIRA/blob/main/notebooks/kaggle/02_full_run.ipynb) |
| **`03_real_world_validation.ipynb`** | Sparkov real-world transfer & C2ST fidelity validation | Kaggle CPU (~25 min) | `external_anchor.json`, `fidelity.json` | [Open Code](https://github.com/ankit-choubey/Project-KIRA/blob/main/notebooks/kaggle/03_real_world_validation.ipynb) |
| **`04_phase2_mega_notebook.ipynb`** | S-00 to S-04 Graph-Tabular Fusion (Arm A vs. Arm D) | Kaggle CPU (~8.5 min) | `master_results.json`, `comparison.json` | [Open Code](https://github.com/ankit-choubey/Project-KIRA/blob/main/notebooks/kaggle/04_phase2_mega_notebook.ipynb) |
| **`05_adv002_large_swarm.ipynb`** | ADV-002 15,000 stateful adversarial swarm population | Kaggle CPU (~18 min) | `adv002_swarm_telemetry.json` | [Open Code](https://github.com/ankit-choubey/Project-KIRA/blob/main/notebooks/kaggle/05_adv002_large_swarm.ipynb) |
| **`06_adv003_adaptive_defense.ipynb`** | ADV-003 Adaptive Challenger Hardening & Retention audit | Kaggle CPU (~12 min) | `adaptive_metrics.json` | [Open Code](https://github.com/ankit-choubey/Project-KIRA/blob/main/notebooks/kaggle/06_adv003_adaptive_defense.ipynb) |

---

## ⚡ Live REST API Specification (Render Web Service)

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

## 🛠️ Local Developer Commands

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
