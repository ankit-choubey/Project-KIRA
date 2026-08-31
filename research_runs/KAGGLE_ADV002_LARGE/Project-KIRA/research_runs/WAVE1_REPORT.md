# Project KIRA — Phase 1 Research Expansion Report (Wave 1 CPU)

**Execution Date:** 2026-08-30 21:42:33 UTC  
**Authoritative Baseline Run:** `run_tiny_s20260827_193f7897_40997ab`  
**Baseline Commit:** `40997ab`  
**Execution Mode:** CPU Only (Wave 1 Infrastructure & Bounded Validation)  
**Dry Run:** `False`  

---

## 1. Environment Profile (S-00)
- **Platform:** macOS-26.6.2-arm64-arm-64bit-Mach-O
- **Python Version:** 3.14.0
- **CPU Cores:** 10
- **RAM:** 16.0 GB
- **GPU Detected:** False (GPU usage explicitly disabled for Phase 1)
- **Sparkov Local Status:** `REMOTE_DATA_REQUIRED` (Heavy download avoided on local laptop)

## 2. Baseline Cryptographic Integrity (S-01)
- **Verified Artifacts:** 22 / 22 (100% SHA-256 match)
- **Integrity Status:** `PASS_22_OF_22`
- **Champion PR-AUC:** 1.0
- **Champion ECE / FPR:** 0.0 / 0.0

## 3. L3 Behavioral Fidelity (S-02)
- **Status:** `MEASURED_SYNTHETIC_ONLY`
- **Synthetic Transactions Evaluated:** 9348
- **Inter-Event Timing (P1 Mean Δt):** 277.25s
- **Burstiness Coefficient (P2):** -0.1033
- **Shared Device Ratio (P3):** 0.0203
- **Velocity Rule Trigger Rate (P4):** 0.063222

## 4. Classifier Two-Sample Test (S-03)
- **Status:** `COMPLETE`
- **C2ST Test AUC:** `0.5025` (95% CI: [0.4745, 0.5318])
- **Samples Evaluated:** 9348
- **Top Discriminative Features:** time_of_day (319.00), log_amount (295.00), is_agent (0.00)

## 5. TSTR Transfer Evaluation (S-04)
- **Status:** `COMPLETE`
- **TSTR Test PR-AUC:** `0.013`
- **TSTR Test ROC-AUC:** `0.7442`
- **TSTR Brier Score:** `0.00551`

## 6. Graph Topology & Causal Leakage Audit (S-05)
- **Status:** `PASS`
- **Audit Outcome:** `ALL 5 CHECKS PASSED`
- **Total Entities:** {'customer': 198, 'merchant': 80, 'device': 345, 'agent': 15, 'transaction': 9348}
- **Total Edges:** 28044
- **Chronological Isolation:** Verified (`train < valid < test`)
- **Future Edge / Node Leakage:** 0 Violations

---

## 7. Wave-1 Stage Summary Table

| Stage | Track | Status | Wall-Clock | Decision Signal |
| :--- | :--- | :---: | :---: | :--- |
| **S-00** | Environment & Safety | `COMPLETE` | 0.41s | Ready |
| **S-01** | Baseline Integrity | `COMPLETE` | 0.01s | Verified (22/22 SHA-256) |
| **S-02** | L3 Behavioral Fidelity | `COMPLETE` | 0.01s | RESEARCH ONLY |
| **S-03** | C2ST Discriminator | `COMPLETE` | 0.19s | RESEARCH ONLY |
| **S-04** | TSTR Transfer | `COMPLETE` | 0.08s | RESEARCH ONLY |
| **S-05** | Graph Causal Audit | `COMPLETE` | 0.02s | ELIGIBLE FOR GPU G-01 |

---

## 8. Safety & Policy Compliance
- **Zero GPU Compute:** Confirmed (Phase 1 strictly executed on CPU).
- **Zero Heavy Dataset Download:** Confirmed (Sparkov full dataset remote requirement preserved).
- **Zero Baseline Mutation:** Confirmed (Authoritative baseline `40997ab` remains completely untouched).
