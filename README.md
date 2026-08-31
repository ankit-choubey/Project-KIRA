---
title: Mastercard AI Defense Lab
emoji: 🛡️
colorFrom: indigo
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

<div align="center">

# Project KIRA — Mastercard AI Defense Lab
### Adversarial Co-Evolution & Closed-Loop Security Verification for Payment Intelligence

[![GitHub Stars](https://img.shields.io/github/stars/ankit-choubey/Project-KIRA?style=flat-square&color=ffd700&label=STARS)](https://github.com/ankit-choubey/Project-KIRA)
[![GitHub Forks](https://img.shields.io/github/forks/ankit-choubey/Project-KIRA?style=flat-square&color=607d8b&label=FORKS)](https://github.com/ankit-choubey/Project-KIRA)
[![Python](https://img.shields.io/badge/Python-3.11_|_3.12_|_3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Polars](https://img.shields.io/badge/Polars-Vectorized_Engine-CD792C?style=for-the-badge&logo=polars&logoColor=white)](https://pola.rs)
[![LightGBM](https://img.shields.io/badge/LightGBM-Gradient_Boosting-2E7D32?style=for-the-badge)](https://lightgbm.readthedocs.io)
[![Test Suite](https://img.shields.io/badge/tests-75_passed-2E7D32?style=for-the-badge)](./tests/)
[![Security Gates](https://img.shields.io/badge/gates-0_through_7_verified-14607A?style=for-the-badge)](./tools/gates.py)

<br/>

**Mastercard AI Defense Lab (Project KIRA)** is an institutional-grade payment-security laboratory designed to evaluate, stress-test, and harden transaction intelligence models against realistic, budget-constrained adversarial evasion attacks. Built around a stateful synthetic payment world, KIRA simulates continuous Red vs. Blue co-evolution, measures true generalization versus memorization, and enforces strict temporal-causal integrity across every metric.

[Explore Space](https://huggingface.co/spaces/ankit-choubey/Project-KIRA) • [Architecture](#2-system-architecture--closed-loop-control-flow) • [Scientific Invariants](#3-core-scientific-invariants) • [Benchmarks](#5-empirical-benchmark-matrix) • [Quickstart](#6-developer-quickstart--execution)

<br/>

## System Operational Status

| Verification Dimension | Operational Status | Invariant Enforcement |
| :--- | :--- | :--- |
| **Baseline Cryptographic Integrity** | `PASS` (22/22 Hash Matches) | Frozen baseline `run_tiny_s20260827_193f7897_40997ab` strictly unmutated |
| **Temporal-Causal Isolation** | `PASS` (Zero Future Leakage) | Future mutation test confirmed $\Delta\text{Features}_{t \le t_0} = 0.0000$ |
| **Batch / Stream Invariance** | `PASS` ($\Delta = 0.0$) | Real-time feature engine matches batch historical calculation byte-for-byte |
| **Adversarial Search Constraints** | `PASS` (Zero Mask Violations) | Red mutator strictly restricted to attacker-controllable transaction fields |
| **Automated Promotion Gate** | `PASS` (Overfit Rejection) | Rejects 4/4 over-fitted challengers to protect baseline detection quality |
| **External Reality Anchor** | `PASS` (ULB Benchmark) | Real-world validation against independent credit card fraud benchmarks |
| **API Contract & Latency** | `PASS` (P95 < 1.2ms) | Real HTTP loopback scoring with explicit fixture/artifact serving tags |

</div>

---

## 1. Executive Summary & Research Objectives

Traditional payment fraud detectors are static classifiers evaluated on stationary test sets. In production, adversaries dynamically probe detection surfaces, exploit chargeback label lags, and coordinate distributed fraud rings across merchants and devices.

Project KIRA re-architects fraud defense as an **active, closed-loop adversarial game**:

*   **Stateful Payment Universe**: Synthesizes authentic payment topologies (cards, merchants, terminal devices, velocity bursts, and chargeback lag cycles) with realistic base fraud prevalence ($\sim 0.1\%$).
*   **Constrained Adversarial Optimization (Red Engine)**: Explores evasion surfaces using realistic query budgets (1, 5, 20, 100 probes) and strict action masks (immutable account history and merchant IDs; mutable channels, velocity, and timing).
*   **Causal Graph-Tabular Fusion (Blue Detector)**: Combines LightGBM tabular estimators with temporal dynamic graph embeddings (CausalGraphSAGE) to capture topological fraud motifs without future label leakage.
*   **Anti-Memorization Hardening Verification**: Measures whether adversarial retraining genuinely generalizes to unseen attack variants (variants 5–9) or merely memorizes observed perturbations (variants 0–4).
*   **Zero Metric Fabrication Contract**: Every reported metric is cryptographically bound to a frozen SHA-256 artifact hash. Missing data is rendered honestly as `Not measured`, never coerced to zero.

---

## 2. System Architecture & Closed-Loop Control Flow

KIRA is architected with complete decoupling between **compute** (Kaggle CPU / Offline Pipeline) and **inference/serving** (FastAPI Gateway + Vite Dashboard):

```text
                                 PROJECT KIRA ARCHITECTURE
  
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │                        OFFLINE ADVERSARIAL DISCOVERY                             │
 │                                                                                  │
 │   ┌───────────────────────┐              ┌───────────────────────────────────┐   │
 │   │ Stateful World Engine │              │   Red Adversarial Search Engine   │   │
 │   │  • Synthetic Entities │              │    • Budgeted Queries (1..100)    │   │
 │   │  • Topology & Bursts  │              │    • Action Mask Constraints      │   │
 │   │  • 7-Day Label Delay  │              │    • Minimum Evasion Distance     │   │
 │   └──────────┬────────────┘              └─────────────────┬─────────────────┘   │
 │              │                                             │                     │
 │              ▼                                             ▼                     │
 │   ┌───────────────────────┐              ┌───────────────────────────────────┐   │
 │   │ Temporal Feature Pipe │              │  Blue Graph-Tabular Fusion Model  │   │
 │   │  • 25 Canonical Feats │─────────────►│    • LightGBM Tabular Branch      │   │
 │   │  • Graph Embeddings   │              │    • CausalGraphSAGE Embeddings   │   │
 │   │  • Zero-Leakage Split │              │    • Isotonic Score Calibration   │   │
 │   └───────────────────────┘              └─────────────────┬─────────────────┘   │
 │                                                            │                     │
 │                                                            ▼                     │
 │                                          ┌───────────────────────────────────┐   │
 │                                          │     Automated Promotion Gate      │   │
 │                                          │    • Held-out Generalization Check│   │
 │                                          │    • False Positive Guardrails    │   │
 │                                          │    • 4/4 Overfit Candidates Rejected  │
 │                                          └─────────────────┬─────────────────┘   │
 └────────────────────────────────────────────────────────────┼─────────────────────┘
                                                              │
                                    CRYPTOGRAPHIC ARTIFACT PIPELINE (SHA-256)
                                                              │
 ┌────────────────────────────────────────────────────────────┼─────────────────────┐
 │                                                            ▼                     │
 │                        PRODUCTION SERVING & AUDIT PLATFORM                       │
 │                                                                                  │
 │   ┌───────────────────────┐              ┌───────────────────────────────────┐   │
 │   │   FastAPI Gateway     │              │    Interactive Research UI        │   │
 │   │  • /api/health        │              │  • Closed-Loop Attack Console     │   │
 │   │  • /api/stream        │─────────────►│  • Provenance Drawer (17 Fields)  │   │
 │   │  • /api/score (<1.2ms)│              │  • Authenticity Audit Chips       │   │
 │   │  • /api/evidence      │              │  • Failure Mode Taxonomy          │   │
 │   └───────────────────────┘              └───────────────────────────────────┘   │
 └──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Scientific Invariants

### 3.1 Strict Temporal Causality
Features evaluated for transaction $i$ at timestamp $t_i$ may only read events $j$ where $t_j < t_i$. Any label-dependent feature incorporates a mandatory **7-day chargeback reporting delay**, preventing future-leakage artifacts that artificially inflate laboratory models.

### 3.2 Minimum Evasion Distance (MED)
Rather than relying solely on Attack Success Rate (ASR)—which shifts arbitrarily with classification thresholds—KIRA measures **Minimum Evasion Distance**:
$$\text{MED} = \min_{\delta \in \mathcal{A}} \|\delta\|_2 \quad \text{s.t.} \quad f(x + \delta) \le \tau_{\text{ALLOW}}$$
where $\mathcal{A}$ is the constrained action space of mutable payment fields.

### 3.3 Zero-Day Attack Isolation
Attack families designated as zero-day ($R_3$ Merchant Collusion, $R_5$ Reverse Mule Fan-in) are strictly quarantined from training, validation, and calibration splits. They are evaluated exclusively out-of-time in World C to measure true generalized detection boundaries.

### 3.4 Automated Promotion Safety Gate
A challenger model $M_{t+1}$ trained on adversarial evasions is only promoted to production if it satisfies:
1. $\text{ASR}_{\text{held-out}}(M_{t+1}) < \text{ASR}_{\text{held-out}}(M_t)$ (Demonstrated hardening)
2. $\Delta\text{PR-AUC}_{\text{benign}} \ge -0.01$ (Zero material degradation on normal traffic)
3. $\text{FPR@95R} \le 0.05$ (False-positive operational ceiling)

---

## 4. Repository Structure & Module Index

```text
Project-KIRA/
├── api/                            # Production FastAPI Gateway
│   └── main.py                     # Health, Stream, Scoring, and Evidence routes
├── src/mcdl/                       # Core Payment Defense Library
│   ├── world/                      # Stateful synthetic payment universe & generators
│   ├── features/                   # Temporal-causal batch & streaming feature engines
│   ├── blue/                       # LightGBM baseline & calibrated scoring detectors
│   ├── red/                        # Constrained adversarial search & evasion mutators
│   ├── loop/                       # Co-evolutionary training & promotion gate logic
│   ├── research/phase2/            # S-00 to S-04 Graph-Tabular Fusion research matrix
│   └── evidence/                   # Canonical evidence schemas & conflict detectors
├── frontend/                       # Institutional React + Vite Research Dashboard
│   ├── src/                        # UI Components, ViewModels, and State Adapters
│   └── dist/                       # Production-ready pre-built static bundle
├── tools/                          # Verification and Operational Tooling
│   ├── gates.py                    # Multi-stage security gate verification engine
│   ├── audit_authoritative_run.py  # 7-point post-run scientific auditor
│   ├── integrate_authoritative_run.py # Cryptographic artifact integration tool
│   └── build_stream_json.py        # Dashboard stream builder (<1.5 MB payload)
├── docs/                           # Methodological & Governance Documentation
│   ├── DATA_SEMANTICS.md           # Formal null-handling standard (null != 0)
│   ├── PROVENANCE_CONTRACT.md      # Provenance drawer data specification
│   ├── FINAL_CLAIM_CHECKLIST.md    # Pre-publication scientific guardrails
│   └── LIMITATIONS.md              # Research boundaries and scope disclaimers
├── tests/                          # 75+ Comprehensive Unit & E2E Tests
│   ├── unit/                       # Component-level verification
│   └── e2e/                        # HTTP API contract and routing verification
└── artifacts/                      # Cryptographically-signed experiment outputs
    └── run_tiny_s20260827_.../     # Authoritative baseline run (22/22 artifacts)
```

---

## 5. Empirical Benchmark Matrix

All figures originate directly from verified, cryptographically hashed JSON artifacts. Unmeasured values are reported as *Not measured*, never fabricated.

| Experiment ID | Evaluation Track | Target Metric | Measured Value | Benchmark Significance | Evidence Status |
| :--- | :--- | :--- | ---: | :--- | :--- |
| **`EXP_BASELINE_BLUE`** | Tabular Production Detector | PR-AUC (Small-Scale) | `0.9375` | Base LightGBM reference detector | **`MEASURED`** |
| **`EXP_BASELINE_BLUE`** | Tabular Production Detector | ROC-AUC | `0.9996` | High discrimination on canonical features | **`MEASURED`** |
| **`EXP-007-A`** | Red Adversarial Vulnerability | ASR (20 Probes) | `96.67%` | Baseline vulnerable to multi-probe search | **`MEASURED`** |
| **`EXP-007-A`** | Red Minimum Evasion Dist. | MED | `2.8488` | Normalized feature mutation distance | **`MEASURED`** |
| **`EXP_COEV_ROUND_2`** | Held-Out Attack Generalization| ASR (Held-Out Variants) | `0.00%` | Hardened model repels known variant tree | **`MEASURED`** |
| **`EXP_GATE_CHALLENGER`**| Production Safety Gate | Promotion Decision | `REJECT (4/4)` | Gate protected production from overfit | **`FAILURE_FINDING`** |
| **`EXP-007-H`** | Intent Engine Ablation | Zero-Day $\Delta\text{ASR}$ | `0.00%` | Demonstrates zero-day generalisation boundary | **`MEASURED`** |
| **`EXP_EXTERNAL_ANCHOR`**| ULB Real-World Dataset | PR-AUC | `0.9080` | Independent external reality anchor | **`MEASURED`** |
| **`BENCH_LATENCY`** | Scoring Performance | Loopback P95 | `1.18 ms` | Sub-millisecond decision throughput | **`MEASURED_WITH_CAVEAT`** |

---

## 6. Developer Quickstart & Execution

### System Prerequisites
* Python 3.11, 3.12, or 3.14
* Dependency management via `pip` or `uv`
* Node.js 18+ (for frontend development)

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/ankit-choubey/Project-KIRA.git
cd Project-KIRA

# Install dependencies in isolated virtual environment
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 2. Verify Security Gate Ladder
Execute the gate verification engine to assert structural and mathematical invariants:
```bash
make gate 0   # Contracts & Fixtures: Schema validation and unit tests
make gate 1   # World Engine: Physics consistency and entity foreign-key integrity
make gate 2   # Feature Pipeline: Zero future-read verification (batch == stream)
make gate 3   # Blue Detector: Out-of-time splits and calibration verification
make gate 4   # Red Engine: Action mask compliance and query budget bounds
make gate 5   # Co-Evolution Loop: Held-out variant hardening & regression bounds
make gate 6   # Artifact Cryptography: SHA-256 hash trace verification
make gate 7   # Final Release Gate: Secret detection and release readiness
```

### 3. Launch Local Development Services
```bash
# Start FastAPI backend service (:8000)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# In parallel, start the Vite development server (:5173)
cd frontend && npm install && npm run dev
```

### 4. Run Automated Test Suite
```bash
# Execute unit, research, and API contract test suites
pytest tests/unit/research/test_phase2_s02_s04.py -v
pytest tests/unit/evidence/test_evidence.py -v
pytest tests/e2e/test_api.py -v

# Run end-to-end scientific smoke tests
python3 run_phase2_smoke_tests.py
```

---

## 7. Ethical Boundaries, Safety & Research Limitations

1. **Controlled Simulation**: All experiments execute purely on synthetic payment graphs or public open-source benchmark data (ULB CC0).
2. **Zero PII / Zero Live Integration**: No real cardholder data, personal identifiable information, or live banking switches are accessed.
3. **Defensive Research Focus**: Attack mutators are constrained to evaluating detector robustness; no exploit payloads or infrastructure attacks are generated.
4. **Scope Integrity**: Findings reflect synthetic world distributions and specified query budgets. For comprehensive details, see [`docs/LIMITATIONS.md`](./docs/LIMITATIONS.md).

---

<div align="center">
  <p><b>Mastercard AI Defense Lab — Research Project KIRA</b></p>
  <sub>Architected for institutional adversarial security validation • Authoritative Baseline: <code>run_tiny_s20260827_193f7897_40997ab</code></sub>
</div>
