# ADV-001: Large-Scale Adversarial Population Evaluation Report

- **Experiment ID**: `ADV-001`
- **Population ID**: `ADV001_ATTACK_POPULATION_10K`
- **Total Evaluated Attempts**: `10,000`
- **Master Seed**: `20260831`
- **Blue Model Version**: `run_tiny_s20260827_193f7897_40997ab`
- **Total Runtime**: `2.87s` (`3484.32 attempts/sec`)
- **Classification**: **`MEASURED`**

---

## 1. Primary Empirical Findings

| Metric | Measured Value | 95% Bootstrap CI | Baseline (EXP-007-A) |
| :--- | :--- | :--- | :--- |
| **Total Attempts** | **`10,000`** | N/A | `200` |
| **Aggregate ASR** | **`6.00%`** | `(0.0554, 0.0646)` | `N/A` |
| **ASR @ Budget 1** | **`0.00%`** | `(0.0, 0.0)` | `33.33%` |
| **ASR @ Budget 5** | **`8.00%`** | `(0.0696, 0.0908)` | `76.67%` |
| **ASR @ Budget 20** | **`8.00%`** | `(0.0696, 0.0908)` | `96.67%` |
| **ASR @ Budget 100** | **`8.00%`** | `(0.0696, 0.0908)` | `96.67%` |
| **Median MED** | **`1.2032`** | `(1.2017, 1.2067)` | `2.8488` |

---

## 2. Attack Family Breakdown

| Family | Attempted | Evasions | ASR | 95% CI | Median Queries | Median MED |
| :--- | ---: | ---: | ---: | :--- | ---: | ---: |
| `burst_drain` | 2,000 | 0 | 0.00% | (0.0, 0.0) | 5.0 | None |
| `slow_siphon` | 2,000 | 0 | 0.00% | (0.0, 0.0) | 5.0 | None |
| `geo_hop` | 2,000 | 600 | 30.00% | (0.28, 0.3205) | 4.0 | 1.2032 |
| `agent_subversion` | 2,000 | 0 | 0.00% | (0.0, 0.0) | 5.0 | None |
| `cross_merchant_fanout` | 2,000 | 0 | 0.00% | (0.0, 0.0) | 5.0 | None |

---

## 3. Outcome Taxonomy Distribution

- **ALLOWED_EVASION**: `600`
- **BLOCKED**: `9,100`
- **STEP_UP**: `300`
- **GENERATION_FAILURES**: `0`
- **ERRORS**: `0`

---

## 4. Scientific Limitations & Boundaries
1. **Synthetic Population Context**: The 10,000 attempts represent simulated mutation trajectories against a fixed world state, not 10,000 independent real-world adversaries.
2. **Deterministic Mutation Grid**: Diversity is parameterized over canonical mutation operators within defined mutability masks.
3. **No Dynamic Defender Adaptation**: ADV-001 measures evasion across an unhardened baseline detector without online retraining during the test sequence.
