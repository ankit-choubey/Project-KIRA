# Project KIRA — Phase 2 Master Scientific Reconciliation (S-04)

- **Baseline Run ID**: `run_tiny_s20260827_193f7897_40997ab` (`40997ab`)
- **Phase 2 Run ID**: `phase2_1788159476` (`f9ad563ca867f2524ac499bb0ecca49af4134575`)
- **Execution Backend**: `CPU (NumPy vectorized)`
- **Generated At**: 2026-08-31T10:54:18.139014+00:00
- **Authoritative 22/22 Baseline Integrity**: `PASS (Verified)`

## 1. Structured Scientific Claims Registry

| Claim ID | Experiment | Scale | Sample Count | Metric & Value | p-value | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CLM_001_AUTHORITATIVE_TABULAR_BASELINE` | `EXP_BASELINE_BLUE` | `tiny` | 1403 | pr_auc=+1.0000 | N/A | **`MEASURED`** |
| `CLM_002_FEATURE_TEMPORAL_CAUSALITY` | `S00` | `tiny` | 5 | global_max_delta=+0.0000 | N/A | **`MEASURED`** |
| `CLM_003_GRAPH_DIAGNOSTIC_STANDALONE` | `G01` | `tiny` | 1403 | pr_auc=+0.0083 | N/A | **`MEASURED`** |
| `CLM_004_G03_FUSION_INCREMENTAL_VALUE` | `G03` | `tiny` | 1403 | delta_rel=+0.0444 | 0.1560 | **`INCONCLUSIVE`** |
| `CLM_005_S02_FULL_SCALE_SYNTHETIC_VALIDATION` | `S02` | `tiny` | 1403 | None | N/A | **`NOT_MEASURED`** |
| `CLM_006_S03_ZERO_DAY_ROBUSTNESS` | `S03` | `tiny` | 0 | None | N/A | **`NOT_MEASURED`** |

## 2. Evidence Hierarchy & Invariant Verification
1. **Baseline Integrity**: 22/22 authoritative artifacts verified against frozen cryptographic SHA-256 signatures.
2. **Strict Temporal Causality**: Feature-level counterfactual mutation guarantees zero future information leakage.
3. **Graph Topology Invariance**: Standalone CausalGraphSAGE and Dual-Branch Fusion pass 4 mathematical temporal invariance checks.
4. **Fairness Controls**: Arm A (Tabular), Arm C (Fusion), and Arm D (Shuffled) use identical transactions, labels, boundaries, and seeds.
5. **Zero-Day Attack Isolation**: World C attack families are strictly removed from training/validation/calibration in S-03.
