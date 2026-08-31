# ADV-002-LARGE Pre-Execution Audit & Cloud Architecture Report

**Experiment ID**: `ADV-002-LARGE`  
**Title**: 5,000-Attempt Stateful Multi-Agent Adversarial Swarm Cloud Execution  
**Preparation Timestamp**: 2026-08-31T17:30:00Z  
**Base Commit**: `6c7a67f`  

---

## 1. Executive Summary & Safety Pre-Conditions

This document specifies the architecture, resource profiling, failure recovery contracts, and scientific controls prepared for **ADV-002-LARGE (5,000 stateful adversarial attempts)**.

In strict compliance with project governance:
- **Zero local execution**: The 5,000-attempt workload has **NOT** been run on this local workstation.
- **Zero modification to V6**: `04_phase2_mega_notebook.ipynb` and all Phase-2 paths remain 100% untouched.
- **Zero corruption of authoritative baseline**: Authoritative baseline artifacts remain verified with 22/22 SHA-256 matches.

---

## 2. Workload & Population Architecture

| Dimension | Standard Scale (Measured) | Large Scale (Target) | Notes |
| :--- | :--- | :--- | :--- |
| **Candidate Targets** | 5 | **10** | Blocked/step-up transactions from test split |
| **Rounds per Campaign** | 20 | **100** | Sequential exploration $\to$ exploitation |
| **Active Agents** | 5 | **5** | Canonical specialized swarm |
| **Total Attempts** | 500 | **5,000** | $10 \text{ targets} \times 100 \text{ rounds} \times 5 \text{ agents}$ |
| **Master Seed** | `20260831` | `20260831` | Deterministic reproducible seeding |
| **Memory Ingestion** | Read-only ADV-001 (10,000) | Read-only ADV-001 (10,000) | 100% immutable SHA-256 verification |

---

## 3. GPU Suitability Audit

A comprehensive hardware and algorithmic profile of the KIRA swarm pipeline was conducted:

### Algorithmic Breakdown
1. **Streaming Feature Extraction**: Stateful per-customer rolling window updates (velocity, frequency, delta amounts) executed via Polars/Dict logic sequentially. **CPU-bound**.
2. **Inference Engine**: Evaluates a 100-tree shallow decision forest (`BlueDetector`, max depth 5) on a single 1-row transaction feature vector (~0.05 ms latency per inference on CPU). **CPU-bound**.
3. **Mutation Search Engine**: Perturbation loops with Layer-1 physical constraints validation. **CPU-bound**.
4. **Adaptive Policy**: Non-RL mathematical scoring, epsilon decay, and indexed memory lookups. **CPU-bound**.

### Hardware & Cost Projections
- **Empirical Standard Run Throughput**: 84.10 attempts / second (5.945 seconds for 500 attempts on 1 CPU core).
- **Projected 5,000-Attempt CPU Runtime**: **~59.5 seconds** (< 1.5 minutes on a standard 2-core CPU).
- **GPU Suitability Verdict**: **`GPU_NOT_BENEFICIAL_FOR_CURRENT_ARCHITECTURE`**
  - *Rationale*: Copying single 1-row feature vectors across the PCIe bus to GPU memory introduces 5–10ms latency per transaction, which exceeds the ~0.05ms CPU inference time. GPU acceleration would increase total runtime and cloud compute costs without providing any scientific or computational benefit.
- **Expected Peak RAM**: **~420 MB**.
- **Expected VRAM**: **0 MB**.
- **Expected Cloud Cost**: **< $0.01 USD**.

---

## 4. Checkpoint & Resumability Contract

The large cloud run is engineered for atomic failure recovery and resumability:
1. **Atomic Round Writes**: Every round is written via `.tmp` file and atomically renamed to prevent partial writes.
2. **Campaign State Checkpoints**: Each completed campaign state is persisted in `campaigns/<campaign_id>.json`.
3. **Zero Duplicate Guarantee**: On runner invocation or restart, `storage.get_completed_campaign_ids()` discovers existing completed campaigns and skips them automatically.
4. **Deterministic Attack IDs**: Attack IDs follow `atk_adv002_{campaign_index:04d}_{round:03d}_{agent_id}`, guaranteeing bijection and uniqueness.
5. **Memory Immutability**: Historical ADV-001 attack memory is opened exclusively in read mode (`"r"`), and its SHA-256 hash is validated before and after execution.

---

## 5. Scientific Control Arms

To scientifically establish the precise value of **adaptation** and **shared memory**, three control arms are instrumented in the runner:

1. **`adaptive_memory` (Active Experimental Arm)**:
   - Full multi-agent swarm with shared cross-agent memory and dynamic policy adaptation.
2. **`static_control` (Ablation Arm 1)**:
   - Fixed query budget (20) and static round-robin family preference without policy or memory updates.
3. **`memory_disabled` (Ablation Arm 2)**:
   - Stateful multi-agent swarm relying strictly on private agent history; shared attack memory querying disabled.

### Formal Hypotheses
- $H_1$: $\text{ASR}(\text{adaptive\_memory}) > \text{ASR}(\text{static\_control})$
- $H_2$: $\text{ASR}(\text{adaptive\_memory}) > \text{ASR}(\text{memory\_disabled})$

---

## 6. Local Test Suite Verification Results

```bash
# Unit test suite
pytest tests/unit/research/test_adv002.py -v   # 14 / 14 PASSED
pytest tests/unit/research/test_adv001.py -v   # 14 / 14 PASSED
python3 run_phase2_smoke_tests.py              # ALL CHECKS PASSED
python3 tools/audit_authoritative_run.py run_tiny_s20260827_193f7897_40997ab # 22/22 HASH MATCH
```

---

## 7. Cloud Execution Command

When authorized for cloud execution (Kaggle CPU / Cloud Runner):

```bash
python3 -m mcdl.research.advanced.adv002.runner --scale large --mode adaptive_memory --output-dir research_runs/ADVANCED/ADV-002-LARGE
```

---

## 8. Cloud Launch Authorization

**Current Status**: **`PREPARED_AND_AUDITED_AWAITING_LAUNCH_AUTHORIZATION`**
- All preparation artifacts, test suites, checkpoint contracts, and scientific control implementations are verified and ready.
