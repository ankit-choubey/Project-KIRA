# Project KIRA — Phase 1 Real-World Validation Report

**Execution Timestamp:** 2026-08-30 22:00:03 UTC  
**Baseline Run:** `run_tiny_s20260827_193f7897_40997ab`  
**Reference Dataset:** Sparkov Credit Card Fraud Detection (`kartik2112/fraud-detection`, CC0)  
**Execution Platform:** Kaggle Cloud Environment  

---

## 1. Dataset Provenance (REAL_WORLD)
- **Dataset Name:** Sparkov Credit Card Fraud Benchmark
- **Source URL:** https://kaggle.com/datasets/kartik2112/fraud-detection
- **License:** CC0 1.0 Universal
- **SHA-256:** `12d553ab19440c752d2531ee1af44bb64f12cc3d3839f1649f19e81c230545f0`
- **Test Samples:** 50,000 (199 frauds, rate: 0.3980%)

## 2. S-02: L3 Behavioral Fidelity
- **P1 Inter-Event Timing:** Synthetic 277.3s vs Real 28.5s (Ratio: `9.7447`)
- **P2 Burstiness:** Synthetic `-0.1033` vs Real `0.0634`
- **P3 Shared Entity Density:** Shared Merchant Ratio: `1.0` (Shared Device: `NOT_COMPARABLE (Sparkov reference schema contains no client device telemetry column)`)
- **P4 Velocity Trigger Rate:** Synthetic `0.063222` vs Real `0.003140` (Ratio: `20.1344`)

## 3. S-03: Real-vs-Synthetic C2ST
- **C2ST Test AUC:** `0.778` (95% CI: `[0.7641, 0.7918]`)
- **Samples:** 18,696
- **Top Features:** [{'feature': 'log_amount', 'importance': 365.0}, {'feature': 'day_of_week', 'importance': 223.0}, {'feature': 'time_of_day_sec', 'importance': 157.0}]

## 4. S-04: TSTR & TRTR Transfer
- **TSTR (Synthetic -> Real):** PR-AUC = `0.0271`, ROC-AUC = `0.7597`
- **TRTR (Real -> Real):** PR-AUC = `0.406`, ROC-AUC = `0.9708`
- **Transfer Gap:** `-0.3789`

## 5. S-05: Graph Causal Leakage Audit
- **Status:** `PASS` (0 Violations)
- **Total Graph Nodes / Edges:** {'customer': 198, 'merchant': 80, 'device': 345, 'agent': 15, 'transaction': 9348} / 28044
