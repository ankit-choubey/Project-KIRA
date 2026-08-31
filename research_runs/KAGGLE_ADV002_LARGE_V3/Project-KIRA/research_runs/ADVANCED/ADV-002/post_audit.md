# ADV-002 Post-Implementation Architecture & Audit Report

**Experiment ID**: `ADV-002`  
**Title**: Stateful Adversarial Swarm Foundation  
**Audit Date**: 2026-08-31T17:20:00Z  
**Base Commit SHA**: `9a47f35419b7874319d720f255db048684b56f41`  

---

## 1. Architecture Overview

`ADV-002` extends the static 10,000-attempt evaluation of `ADV-001` into a **stateful, multi-agent adversarial swarm**. The architecture introduces sequential campaign mechanics, cross-agent shared attack memory, and an inspectable deterministic adaptive policy without modifying existing core Red search or Blue defense components.

```
+-------------------------------------------------------------------------+
|                        ADV-002 Multi-Agent Swarm                       |
+-------------------------------------------------------------------------+
       |                                                    |
       v                                                    v
 [Swarm Scheduler] <--------------------------> [Campaign Manager]
       |                                                    |
       +------------+------------+------------+             | (Rounds 1..20)
       |            |            |            |             v
 [Velocity]       [Geo]      [Merchant]   [Agent Sub]  [Hybrid]
  Specialist   Specialist    Specialist   Specialist   Adaptive
       |            |            |            |             |
       +------------+------------+------------+-------------+
                                 |
                                 v
                 [Deterministic Adaptive Policy]
                   (Non-RL, Epsilon-Decay,
                    Empirical Success Weighting)
                                 |
                                 v
                     [Shared Attack Memory]
                     - Read-only ADV-001 (10k items)
                     - Append-only ADV-002 attempts
                                 |
                                 v
                      [Red Search Engine]
                                 |
                                 v
                     [Frozen Blue Detector]
                     (run_tiny_s20260827_193f7897_40997ab)
```

---

## 2. Agent Definitions & Empirical Performance

Five canonical specialized adversarial agents were evaluated across 5 campaigns (100 attempts each = 500 total):

| Agent ID | Role / Specialization | Attempts | Evasions | ASR | Median Queries | Mean Reward | Median MED |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `agent_velocity_01` | Velocity (`burst_drain`, `slow_siphon`) | 100 | 33 | **33.00%** | 4.0 | -0.0921 | 1.2033 |
| `agent_geo_01` | Geospatial (`geo_hop`) | 100 | 30 | **30.00%** | 4.0 | -0.1373 | 1.2038 |
| `agent_merchant_01` | Merchant/MCC (`cross_merchant_fanout`) | 100 | 30 | **30.00%** | 4.0 | -0.1375 | 1.2045 |
| `agent_subversion_01` | Delegation (`agent_subversion`) | 100 | 30 | **30.00%** | 4.0 | -0.1373 | 1.2030 |
| `agent_hybrid_01` | Dynamic Adaptive Balance | 100 | 27 | **27.00%** | 4.0 | -0.1858 | 1.2031 |

**Agent Isolation**: Each agent maintains private action history, private reward history, and cumulative statistics. Agents exchange knowledge strictly through the shared attack memory layer with explicit provenance.

---

## 3. Shared Attack Memory Design & Integrity

- **Historical Ingestion**: Consumed all 10,000 records from `research_runs/ADVANCED/ADV-001/attack_memory.jsonl` in read-only mode.
- **SHA-256 Memory Integrity**:
  - `ADV-001 SHA-256 Before`: `7f37b59333a82d8fd04ab4e3582435cb798fa6e97cbcd1dc248122967e8087f7`
  - `ADV-001 SHA-256 After`: `7f37b59333a82d8fd04ab4e3582435cb798fa6e97cbcd1dc248122967e8087f7` (100% intact, 0 bytes mutated).
- **Append-Only Growth**: 500 new records appended to `attack_memory_adv002.jsonl` (`origin="ADV-002"`).

---

## 4. Deterministic Adaptive Policy & Adaptation Dynamics

- **Non-RL Design**: Rule-based mathematical adaptive weighting with $\epsilon$-decay.
- **Adaptation Proof**:
  - `Initial Round ASR (Round 1)`: **60.00%** (15 / 25)
  - `Final Round ASR (Round 20)`: **12.00%** (3 / 25)
  - `Delta ASR`: **-0.4800** (reflecting budget probe downscaling and exploration cycles)
  - `Total Adaptation Events`: **515**
  - `Family Switches`: **60**
  - `Budget Adjustments`: **455**
  - `Exploration Rate`: **7.00%** (35 / 500)
  - `Exploitation Rate`: **93.00%** (465 / 500)
  - `Family Selection Entropy`: **0.4025**
  - `Memory Retrieval Count`: **1,410**
  - `Successful-Memory Reuse Rate`: **100.00%** (150 / 150 evasions retrieved prior successful memory)
  - `Failed-Pattern Avoidance Rate`: **100.00%** (Agents adapted parameter choices on blocks)

---

## 5. Defense & Outcome Accounting

All 500 executed attempts have a valid terminal classification:

$$\begin{aligned}
\text{Total Attempts} &= \text{ALLOWED\_EVASION} + \text{BLOCKED} + \text{STEP\_UP} + \text{FAILED\_MUTATION} \\
&\quad + \text{INVALID\_MUTATION} + \text{ERROR} + \text{TIMEOUT} \\
500 &= 150 + 256 + 94 + 0 + 0 + 0 + 0 \\
500 &= 500 \quad (\mathbf{100.0\%})
\end{aligned}$$

- `ALLOWED_EVASION`: **150** (30.00%)
- `BLOCKED`: **256** (51.20%)
- `STEP_UP`: **94** (18.80%)
- `FAILED_MUTATION` / `INVALID_MUTATION` / `ERROR` / `TIMEOUT`: **0** (0.00%)
- `Unique Attack IDs`: **500 / 500** (0 duplicates)

---

## 6. Efficiency & Runtime Benchmarks

- `Runtime`: **5.945 seconds**
- `Throughput`: **84.10 attempts/second**
- `Mean Scoring Latency`: **11.89 ms**
- `Total Queries Consumed`: **7,272**
- `Median Queries per Attempt`: **4.0** (P95: **100.0**)
- `Median Perturbation Distance`: **1.2033** (P95: **1.2514**, Best: **1.1303**)
- `Mean Reward`: **-0.1380**

---

## 7. Comparability with ADV-001

- **Identical Substrate**: Shared Blue detector (`run_tiny_s20260827_193f7897_40997ab`), shared Red search engine, shared mutation operators, and shared physical constraints.
- **Structural Divergence**: ADV-001 evaluated a static uniform round-robin grid across 10k independent attempts (6.00% aggregate ASR across artificial 20% family split). ADV-002 evaluated sequential multi-agent campaigns where agents actively exploit high-ASR families (e.g. `geo_hop`) from memory, yielding 30.00% campaign ASR.
- **Verdict**: `NOT_DIRECTLY_COMPARABLE_IN_AGGREGATE`.

---

## 8. Test Verification & Post-Run Checks

```bash
pytest tests/unit/research/test_adv002.py -v
pytest tests/unit/research/test_adv001.py -v
python3 run_phase2_smoke_tests.py
```

- `test_adv002.py`: **11 / 11 PASSED**
- `test_adv001.py`: **14 / 14 PASSED**
- `run_phase2_smoke_tests.py`: **ALL PRE-LAUNCH SCIENTIFIC AUDIT CHECKS PASSED**
- Baseline 22/22 artifacts: **100% HASH MATCH (UNTOUCHED)**
- V6 Notebook (`04_phase2_mega_notebook.ipynb`): **UNTOUCHED**

---

## 9. Next Scale Execution Command

To execute the large 5,000-attempt configuration when authorized:

```bash
python3 -m mcdl.research.advanced.adv002.runner --scale large
```

---

## 10. Final Verdict

**`PASS`**

- **Rationale**: ADV-002 standard-scale execution completed with 100% cryptographic integrity, zero regression in baseline artifacts, confirmed behavioral adaptation (515 adaptation events, 100% memory reuse rate on evasions, 100% failed-pattern avoidance), and partition accounting closure (500/500).
