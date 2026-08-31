# ADV-002 Scientific Evidence & System Status

**Experiment ID**: `ADV-002`  
**Title**: Stateful Multi-Agent Adversarial Swarm Foundation  
**Audit Timestamp**: 2026-08-31T17:20:00Z  
**Base Commit**: `9a47f35419b7874319d720f255db048684b56f41`  

---

## 1. System Implementation & Execution Status Matrix

| Component | Status | Verification Reference | Notes |
| :--- | :---: | :--- | :--- |
| **Module Isolation** | `IMPLEMENTED` | `src/mcdl/research/advanced/adv002/` | 100% isolated from `src/mcdl/red/` and `src/mcdl/blue/` |
| **Agent Swarm Architecture** | `IMPLEMENTED` | `agents.py` | 5 specialized agents with deterministic private state |
| **Shared Attack Memory** | `IMPLEMENTED` | `memory.py` | Read-only ingestion of ADV-001 (10k items), append-only for ADV-002 |
| **Deterministic Adaptive Policy** | `IMPLEMENTED` | `policy.py` | Non-RL, inspectable, $\epsilon$-decay exploration, memory-weighted |
| **Campaign Manager** | `IMPLEMENTED` | `campaign.py` | Multi-round state tracking, sequential adaptation events |
| **Swarm Scheduler** | `IMPLEMENTED` | `scheduler.py` | Coordinated execution, immediate cross-agent memory synchronization |
| **Multi-Objective Reward** | `IMPLEMENTED` | `evaluator.py` | Explicit formula ($R_{\text{evasion}} - P_{\text{dist}} - P_{\text{query}} - P_{\text{decision}}$) |
| **Atomic Storage & Checkpointing**| `IMPLEMENTED` | `storage.py` | Resumability, zero duplicate rounds |
| **Unit Test Suite** | `TESTED` | `tests/unit/research/test_adv002.py` | 11 / 11 tests passing (100% green) |
| **Authoritative ADV-001 Ingestion** | `TESTED` | `test_adv002_adv001_memory_immutable` | 10,000 records read, 0 bytes mutated |
| **Phase-2 / V6 Isolation** | `TESTED` | `test_adv002_phase2_untouched` | All Phase-2 paths and notebooks frozen |
| **Smoke Execution** | `TESTED` | `ADV002Runner(scale='smoke')` | Verified functional loop |
| **Standard Swarm Run (5x20)** | `MEASURED` | `runner.py --scale standard` | 500 attempts executed, 30.00% ASR, 515 adaptation events |
| **Large Swarm Run (5x100)** | `NOT YET MEASURED` | Large execution CLI | Queued for subsequent execution |

---

## 2. Standard Scale (500 Attempts) Empirical Findings

- **Total Campaigns**: `5`
- **Total Agents**: `5` (`agent_velocity_01`, `agent_geo_01`, `agent_merchant_01`, `agent_subversion_01`, `agent_hybrid_01`)
- **Total Rounds**: `20` rounds per agent/target
- **Total Executed Attempts**: `500` ($5 \text{ targets} \times 20 \text{ rounds} \times 5 \text{ agents}$)
- **Aggregate Evasion Rate (ASR)**: **30.00%** (150 / 500)
- **Outcome Distribution**:
  - `ALLOWED_EVASION`: **150** (30.00%)
  - `BLOCKED`: **256** (51.20%)
  - `STEP_UP`: **94** (18.80%)
  - `FAILED_MUTATION` / `INVALID_MUTATION` / `ERROR` / `TIMEOUT`: **0** (0.00%)
- **Adaptation Dynamics**:
  - `Initial Round ASR (Round 1)`: **60.00%** (15 / 25)
  - `Final Round ASR (Round 20)`: **12.00%** (3 / 25)
  - `Total Adaptation Events`: **515**
  - `Family Switches`: **60**
  - `Budget Adjustments`: **455**
  - `Memory Retrievals`: **1,410**
  - `Memory Reuse Rate`: **94.00%** (470 / 500)
  - `Successful-Memory Reuse Rate`: **100.00%** (150 / 150 evasions utilized retrieved memory)
  - `Failed-Pattern Avoidance Rate`: **100.00%** (Swarm systematically shifted parameters when blocked)
- **Efficiency**:
  - `Runtime`: **5.945 seconds**
  - `Throughput`: **84.10 attempts/sec**
  - `Mean Scoring Latency`: **11.89 ms**
  - `Median Queries`: **4.0** (P95: **100.0**)
  - `Median Perturbation Distance`: **1.2033** (P95: **1.2514**, Best: **1.1303**)

---

## 3. Scientific Safety & Boundary Verifications

- **No RL Attacker**: 100% deterministic rule-based adaptive weighting. Zero neural network or gradient-based attacker learning.
- **No Real-World Contamination**: All interactions execute strictly against local synthetic payment ledger.
- **Memory Immutability**: `attack_memory.jsonl` from ADV-001 SHA-256 (`7f37b59333a82d8fd04ab4e3582435cb798fa6e97cbcd1dc248122967e8087f7`) is 100% unchanged before and after run.
- **Scientific Classification**: **`ADAPTATION_DEMONSTRATED`**
