# Kaggle V6 Cross-Artifact Conflict & Lineage Audit

**Audit Date**: 2026-08-31T11:20:00Z  
**Target Execution**: Kaggle Phase-2 Mega Notebook V6 (`f9ad563ca867f2524ac499bb0ecca49af4134575`)  

---

## 1. Stage Re-Numbering & Prefix Collision Resolution

A major naming collision exists in the repository between **Wave 1 (Phase 1 Real-World Expansion)** and **Phase 2 (Graph & Multi-Seed Synthesis)**:

| Stage ID | Wave 1 Meaning | Phase 2 Meaning | Status in V6 Execution |
| :--- | :--- | :--- | :--- |
| **`S-00` / `S00`** | Wave 1 Environment & Hardware Profiler | Phase 2 Feature-level temporal causality invariance | **Both COMPLETED** |
| **`S-01` / `S01`** | Wave 1 Cryptographic Baseline Integrity (22/22) | Phase 2 Split ordering and baseline verification | **Both COMPLETED** |
| **`S-02` / `S02`** | Wave 1 Real-World L3 Behavioral Fidelity (P1–P4) | Phase 2 Full-Scale Synthetic World Validation (3-Arm) | **Wave-1 COMPLETED, Phase-2 FAILED** |
| **`S-03` / `S03`** | Wave 1 C2ST Discriminator vs Sparkov | Phase 2 Out-of-Distribution Zero-Day World-C Robustness | **Wave-1 COMPLETED, Phase-2 FAILED** |
| **`S-04` / `S04`** | Wave 1 TSTR / TRTR Transfer Evaluation | Phase 2 Final Scientific Reconciliation & Synthesis | **Both COMPLETED** |
| **`S-05` / `S05`** | Wave 1 Graph Temporal Causal Leakage Audit | N/A (Only exists in Wave 1) | **COMPLETED** |

### Root Cause of S-02/S-03 Phase 2 Failures
- In `run_s02` and `run_s03`, full-scale synthetic world generation created transactions with `agent_id` strings (e.g. `"agent_c_08869"`). Polars `pl.DataFrame(records)` threw `ComputeError` because the initial rows had `agent_id = None` and `infer_schema_length` defaulted to 100.
- S04 executed gracefully, accurately logging S02 and S03 as `FAILED` / `NOT_MEASURED` without crashing the notebook run.

---

## 2. Identified Discrepancies & Conflicts

### Conflict 1: PR-AUC Baseline Value
- **Authoritative Tiny Baseline**: PR-AUC = `1.0` (on $n=1,403$, 70 fraud samples in `run_tiny_s20260827_193f7897_40997ab`).
- **G-03 Arm A (Frozen LightGBM)**: PR-AUC = `0.9556` ($95\%\text{ CI: } [0.8333, 1.0]$).
- **Explanation**: Arm A evaluated a slightly different train/val/test slicing than the original Block 7 split.

### Conflict 2: Graph Uplift ($G-03$ Fusion)
- **Reported Metric**: $\Delta_{\text{rel}} = +0.0444$ ($+4.44\%$ PR-AUC uplift).
- **Statistical Significance**: $p = 0.1560$ (Bootstrap test).
- **Classification**: **`INCONCLUSIVE`** (The empirical uplift is not statistically distinguishable from random seed variance at $\alpha=0.05$).

### Conflict 3: Sparkov Dataset Fidelity
- **Inter-arrival Time (P1)**: Synthetic $= 277.3\text{s}$ vs Sparkov Real $= 28.5\text{s}$ (Ratio: $9.74\times$).
- **Burstiness (P2)**: Synthetic $= -0.1033$ vs Sparkov Real $= +0.0634$ ($\Delta = -0.1667$).
- **Velocity Triggers (P4)**: Synthetic $= 6.32\%$ vs Sparkov Real $= 0.31\%$ (Ratio: $20.13\times$).
- **Caveat**: Sparkov contains no client device telemetry column; client device comparison is strictly marked `NOT_COMPARABLE`.

### Conflict 4: TSTR Transfer Gap
- **TRTR (Real $\rightarrow$ Real)**: PR-AUC = `0.4060`, ROC-AUC = `0.9708`.
- **TSTR (Synthetic $\rightarrow$ Real)**: PR-AUC = `0.0271`, ROC-AUC = `0.7597`.
- **Transfer Gap**: $\Delta\text{PR-AUC} = -0.3789$.
- **Finding**: While synthetic features capture broad separability (ROC-AUC 0.7597), precision on real-world fraud distributions exhibits a significant domain gap.
