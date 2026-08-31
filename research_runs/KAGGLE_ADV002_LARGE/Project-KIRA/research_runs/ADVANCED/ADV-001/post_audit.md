# ADV-001 Final Post-Implementation Scientific Audit

**Experiment ID**: `ADV-001`  
**Population ID**: `ADV001_ATTACK_POPULATION_10K`  
**Evaluation Scope**: 10,000 Constrained Adversarial Attack Attempts  
**Audit Date**: 2026-08-31T16:50:00Z  

---

## 1. Exact Attempt Semantics

The experiment consists of **10,000 attack attempts**, formally defined as:
> **10,000 deterministic budgeted adversarial search invocations across 200 distinct `(source_transaction, attack_family, query_budget)` grid configurations, with 50 independent seeded search trajectories per grid configuration.**

- **Naming Convention**: The dataset is strictly designated as **10,000 attack attempts** (budgeted search invocations) rather than 10,000 distinct source transactions or 10,000 real-world human actors.
- **Search Execution**: Each attempt executes `RedSearchEngine.attack()` with a dedicated deterministic RNG seed, generating up to $B \in \{1, 5, 20, 100\}$ candidate mutations subject to mutability masks, physical credit/balance invariants, and Blue detector evaluation under temporal context.

---

## 2. Uniqueness & Population Composition

Empirical uniqueness counts extracted directly from `attack_memory.jsonl` (and mirrored in `attempt_semantics.json`):

| Entity / Dimension | Count | Description |
| :--- | ---: | :--- |
| **Total Evaluated Attempts** | `10,000` | Total records in `attack_memory.jsonl` |
| **Unique Attack IDs** | `10,000` | `atk_adv001_000001` through `atk_adv001_010000` |
| **Unique Deterministic Seeds** | `10,000` | Generated via `int((base_seed + idx * 7919 + fam_idx * 31 + budget * 101) % (2**31 - 1))` |
| **Unique Source Transactions** | `10` | 10 candidate transactions from the test split (1,000 attempts each) |
| **Unique Grid Points `(txn, family, budget)`** | `200` | $10 \text{ txns} \times 5 \text{ families} \times 4 \text{ budgets} = 200$ distinct configurations |
| **Repetitions per Grid Point** | `50` | 50 distinct random-walk seed trajectories per grid point ($200 \times 50 = 10,000$) |
| **Duplicate Grid Combinations** | `9,800` | Total attempts minus unique grid points ($10,000 - 200 = 9,800$) |
| **Total Valid Candidate Mutations Scored** | `197,900` | Total physical / mask-valid mutations evaluated against Blue |
| **Invalid Mutations Generated** | `0` | Zero mask/physical violations across all 10k attempts |
| **Unique Evasion Distances Observed** | `598` | Distinct Euclidean perturbation distances across 600 successful evasions |

---

## 3. Family & Budget Distributions

The population follows an exact balanced stratified grid design across all families, budgets, and transactions:

### Family Distribution (Exact Counts)
- `burst_drain`: **2,000** attempts (20.0%)
- `slow_siphon`: **2,000** attempts (20.0%)
- `geo_hop`: **2,000** attempts (20.0%)
- `agent_subversion`: **2,000** attempts (20.0%)
- `cross_merchant_fanout`: **2,000** attempts (20.0%)
- **Total**: **10,000** attempts

### Query Budget Distribution (Exact Counts)
- Budget `1`: **2,500** attempts (25.0%)
- Budget `5`: **2,500** attempts (25.0%)
- Budget `20`: **2,500** attempts (25.0%)
- Budget `100`: **2,500** attempts (25.0%)
- **Total**: **10,000** attempts

### `(Family, Budget)` Stratified Grid
- Each of the 20 `(family, budget)` pairs contains **exactly 500 attempts** ($20 \times 500 = 10,000$).

### Source Transaction Distribution
- Each of the 10 source transactions (`tx_00008161`, `tx_00008275`, `tx_00008408`, `tx_00008428`, `tx_00008768`, `tx_00008791`, `tx_00009014`, `tx_00009125`, `tx_00009290`, `tx_00009337`) contains **exactly 1,000 attempts** ($10 \times 1,000 = 10,000$).

---

## 4. Evasion-Definition Validation

The outcome taxonomy in `src/mcdl/research/advanced/adv001/evaluator.py` has been semantically hardened and tested.

`evasion == True` is possible **ONLY** when all of the following conditions hold simultaneously:
1. The source transaction was in a protected/blocked state (`orig_decision != Decision.ALLOW`).
2. Candidate mutations satisfied all mutability masks and Layer-1 physical constraints (`valid_mutations > 0`, `invalid_mutations == 0`).
3. Perturbation distance is defined and non-zero (`med > 0`).
4. Blue detector returned a final decision of `ALLOW` (`blue_decision == "ALLOW"`).
5. The underlying Red provenance success state is `prov.success == True` and consistent with `Decision.ALLOW`.

### Negative Consistency Guarantees (Proven via Unit Tests)
- If `prov.success == True` but `final_decision != Decision.ALLOW` (e.g. `BLOCK` or `STEP_UP`), `is_evasion` is forced to `False` and `outcome` matches the detector decision (`BLOCKED` or `STEP_UP`).
- If `source_txn` was already `ALLOW` (`SOURCE_ALREADY_ALLOWED` in rejection reasons), `prov.success` is `False`, `evasion` is `False`, and `outcome` defaults to `BLOCKED`.
- If generation failed due to mask violations (`IMMUTABLE`), `outcome` is strictly `INVALID_MUTATION` (`evasion == False`).
- If generation failed due to physical constraint violations, `outcome` is strictly `FAILED_MUTATION` (`evasion == False`).

---

## 5. Attack-Memory Completeness for Future Swarm Work

Every record in `attack_memory.jsonl` was audited for field completeness without relying on hidden state:

| Field Name | Type | Completeness | Description |
| :--- | :--- | :---: | :--- |
| `attack_id` | `str` | **100%** (10,000 / 10,000) | Unique attempt identifier (`atk_adv001_XXXXXX`) |
| `family` | `str` | **100%** (10,000 / 10,000) | Canonical attack family name |
| `strategy` | `str` | **100%** (10,000 / 10,000) | Mutation operator strategy name |
| `seed` | `int` | **100%** (10,000 / 10,000) | Deterministic RNG seed |
| `parent_attack_id` | `str \| null` | **100%** (10,000 / 10,000) | Lineage pointer for swarm/evolutionary work |
| `query_budget` | `int` | **100%** (10,000 / 10,000) | Maximum query allowance ($B \in \{1, 5, 20, 100\}$) |
| `queries_used` | `int` | **100%** (10,000 / 10,000) | Actual queries consumed before stopping/exhaustion |
| `mutation_count` | `int` | **100%** (10,000 / 10,000) | Total mutations attempted |
| `perturbation_distance` | `float \| null` | **100%** (10,000 / 10,000) | Euclidean distance in scaled space (populated for evasions) |
| `target_transaction_id` | `str` | **100%** (10,000 / 10,000) | Identifier of the source transaction |
| `blue_model_version` | `str` | **100%** (10,000 / 10,000) | Version hash of the evaluated Blue detector |
| `blue_score` | `float` | **100%** (10,000 / 10,000) | Calibrated risk score of the best/final candidate |
| `blue_decision` | `str` | **100%** (10,000 / 10,000) | Final Blue decision (`ALLOW`, `STEP_UP`, `BLOCK`) |
| `evasion` | `bool` | **100%** (10,000 / 10,000) | Strict boolean flag indicating successful allowed evasion |
| `outcome` | `str` | **100%** (10,000 / 10,000) | Outcome classification from taxonomy |
| `timestamp` | `str` | **100%** (10,000 / 10,000) | ISO UTC execution timestamp |
| `provenance` | `dict` | **100%** (10,000 / 10,000) | Detailed provenance dict including Red `attack_instance_id` |

**Gap Audit Result**: **0 missing fields**. `attack_memory.jsonl` contains complete self-contained state for future research and swarm memory.

---

## 6. Outcome Accounting Proof

All 10,000 attempts map into mutually exclusive and collectively exhaustive taxonomy states:

$$\begin{aligned}
\text{Total Attempts} &= \text{ALLOWED\_EVASION} + \text{BLOCKED} + \text{STEP\_UP} + \text{FAILED\_MUTATION} \\
&\quad + \text{INVALID\_MUTATION} + \text{ERROR} + \text{TIMEOUT} \\
10,000 &= 600 + 9,100 + 300 + 0 + 0 + 0 + 0 \\
10,000 &= 10,000 \quad (\mathbf{100.0\%})
\end{aligned}$$

- `ALLOWED_EVASION`: **600** (6.00%) — all from `geo_hop` at budget $\ge 5$
- `BLOCKED`: **9,100** (91.00%)
- `STEP_UP`: **300** (3.00%)
- `FAILED_MUTATION`: **0** (0.00%)
- `INVALID_MUTATION`: **0** (0.00%)
- `ERROR`: **0** (0.00%)
- `TIMEOUT`: **0** (0.00%)
- `UNCLASSIFIED / UNKNOWN`: **0** (0.00%)

---

## 7. Limitations & Scientific Caveats

1. **Stratified Weighting**: The aggregate 6.00% ASR is a population-weighted average over an artificial 20% per-family split, not a measurement of natural real-world attacker frequency.
2. **Source Population Diversity**: 10 source transactions were evaluated across 50 seed trajectories each ($10 \times 1,000 = 10,000$). Evasion properties reflect the geometry around these 10 candidate points.
3. **Agent Subversion Mandate Coverage**: The 0% ASR in `agent_subversion` was driven by unlinked customer mandates in the test set, defaulting to fallback limits that the detector flagged.
4. **Trajectory Granularity**: The search engine returns aggregate attempt provenance (`AttackProvenance`) and the optimal candidate rather than logging intermediate rejected queries per attempt. Intermediate per-query step logging is not required for population memory but should be noted as a design choice.

---

## 8. Final Verdict

**`CONDITIONAL_PASS`**

- **Rationale**: ADV-001 is a verified, mathematically sound, complete, and fully reproducible evaluation of 10,000 constrained attack attempts. All evasion semantics, accounting closures, and memory schemas pass strict audit. Claims must explicitly state the balanced stratified grid design (200 configurations $\times$ 50 trajectories) and family-specific evasion boundaries.
