# Master Claim → Evidence Matrix

Every claim that appears in the report, writeup, UI, or presentations is grounded in verified, on-disk artifacts.

**Authoritative Candidate Run:** `run_tiny_s20260827_193f7897_40997ab` (Commit `40997ab`)  
**Supporting Large-Scale Reference Run:** `run_small_s20260827_3a353e9a_052dca8` (Commit `052dca8`)  
**Historical Cloud Run:** `run_tiny_s20260827_193f7897_9cfa1e1` (Commit `9cfa1e1`)

---

## 1. Internal Claims Matrix (C-001 through C-012)

| Claim ID | Claim Text | Metric & Value | Exp ID | Run ID | Artifact Path | Definition & Scope | Status | Scientific Caveats & Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **C-001** | Blue LightGBM detector fraud discrimination | **PR-AUC = 1.0000** *(Tiny Demo)*<br>**PR-AUC = 0.9375** *(Small Scale)*<br>**PR-AUC = 0.6407** *(Cloud Tiny Baseline)* | `EXP-007-C` | `run_tiny_s20260827_193f7897_40997ab`<br>`run_small_s20260827_3a353e9a_052dca8` | `blue_metrics.json`<br>`evaluation.json` | Area under the Precision-Recall curve on strictly out-of-time test split. | **VALID WITH CAVEAT** | Tiny evaluation slice has 5 fraud cases producing near-perfect separability; small-scale (PR-AUC=0.9375) is representative of higher statistical power. |
| **C-002** | Isotonic probability calibration bounds error | **ECE = 0.0000**<br>**Brier = 0.0000** | `EXP-007-C` | `run_tiny_s20260827_193f7897_40997ab` | `calibration.json`<br>`blue_metrics.json` | Expected Calibration Error computed over 10 uniform bins on validation split. | **VALID WITH CAVEAT** | Zero measured calibration error on this benchmark evaluation set; not a theoretical guarantee for all real-world distributions. |
| **C-003** | Query-budgeted static attacker scaling curve | **ASR@1 = 33.33%**<br>**ASR@5 = 76.67%**<br>**ASR@20 = 96.67%**<br>**ASR@100 = 96.67%** | `EXP-007-A` | `run_tiny_s20260827_193f7897_40997ab` | `exp_007_a_static.json`<br>`experiment_register.json` | Attack Success Rate across query budgets against unhardened baseline Blue detector (200 attacks, 5 families). | **VALID** | Represents unhardened pre-defense vulnerability discovery. Distinct from post-hardening Challenger residual ASR. |
| **C-004** | Adversarial generalization across held-out variants | **Baseline Held-out ASR = 14.55%**<br>**Hardened Challenger ASR = 0.00%**<br>**Retention = 1.3071** | `EXP-007-D` | `run_tiny_s20260827_193f7897_40997ab` | `exp_007_d_heldout.json`<br>`promotion_history.json` | Evasion rate on unseen variants ($v_5..v_9$) under strict `(source_txn, family)` lineage separation. | **VALID** | Lineage partitioning verified; hardened challenger caught 100% of adaptation variants. |
| **C-005** | Zero-day transfer to withheld attack families (World C) | **Hidden Family ASR@20 = 100.00%**<br>**Hidden MED = 3.7706** | `EXP-007-E` | `run_tiny_s20260827_193f7897_40997ab` | `exp_007_e_hidden.json`<br>`three_world_evaluation.json` | Transfer evaluation on withheld families (`agent_subversion`, `cross_merchant_fanout`). | **VALID (FAILURE FINDING)** | **Explicit defense limitation**: Adaptation on velocity attacks does not transfer to novel multi-merchant or agent credential drift topologies. |
| **C-006** | Minimum Evasion Distance (MED) perturbation boundary | **Baseline MED = 2.8488**<br>**Challenger MED = null** | `EXP-007-A`<br>`EXP-007-G` | `run_tiny_s20260827_193f7897_40997ab` | `scoreboard.json`<br>`exp_007_a_static.json` | Average normalized $L_1$ feature perturbation required to flip a protected decision to `ALLOW`. | **VALID WITH CAVEAT** | Measured on successful baseline attacks; undefined (`null`) when hardened model produces 0 evasions (never converted to 0.0). |
| **C-007** | Behavioral fidelity filter (L3 P1–P4 ratios) | **NOT MEASURED** (`null`) | — | `run_tiny_s20260827_193f7897_40997ab` | `evaluation.json` | P1 interarrival, P2 burstiness, P3 graph motif, and P4 velocity trigger degradation ratios. | **NOT MEASURED** | L1 physics (0 violations) and L2 correlation distance (0.18) measured; L3 ratios were scoped out of bounded runtime. |
| **C-008** | Statistical correlation distance & C2ST discriminator | **L2 Correlation = 0.1800**<br>**L4 C2ST AUC = NOT MEASURED** | — | `run_tiny_s20260827_193f7897_40997ab` | `evaluation.json` | L2 distance between synthetic and reference feature correlation matrices; C2ST classifier test. | **VALID WITH CAVEAT** | L2 correlation distance bounded at 0.18; C2ST adversarial discriminator was cut and is honestly reported unmeasured. |
| **C-009** | External reality anchor on real-world European cardholders | **PR-AUC = 0.8640**<br>**FPR = 0.03%**<br>**ECE = 0.0042** | — | `run_tiny_s20260827_193f7897_40997ab` | `external_anchor.json` | Benchmark performance on 284,807 transactions (492 frauds) from ULB European Credit Card dataset. | **VALID (CONTEXTUAL ANCHOR)** | Grounded in independent real-world dataset (Dal Pozzolo et al., 2015, DOI: 10.1109/SSCI.2015.33); feature space is PCA-transformed and not directly comparable to KIRA synthetic features. |
| **C-010** | Application scoring endpoint request latency | **P50 = 2.223 ms**<br>**P95 = 2.300 ms**<br>**P99 = 2.361 ms**<br>**Mean = 2.256 ms** | `LATENCY-002` | `run_tiny_s20260827_193f7897_40997ab` | `latency_benchmark.json` | High-resolution roundtrip timing over FastAPI `/api/score` (200 requests, 10 warmups, 0 failures, 30s timeout). | **VALID (MEASURED — HTTP TestClient benchmark)** | Replaces unmeasured 2.15/4.80/8.30 ms estimates. Represents local ASGI request-response loopback, not internet network latency. |
| **C-011** | Verifiable Intent mandate scoring ablation | **With Intent ASR = 100.00%**<br>**Without Intent ASR = 100.00%**<br>$\Delta\text{ASR} = 0.0\%$ | `EXP-007-H` | `run_tiny_s20260827_193f7897_40997ab` | `intent_ablation.json`<br>`exp_007_h_intent.json` | Controlled counterfactual ablation removing `is_agent_initiated` and mandate verification scoring. | **VALID (NEUTRAL / INCONCLUSIVE)** | Intent mechanism is functional, but does not demonstrate empirical ASR reduction against unadapted agent subversion at tiny scale. |
| **C-012** | False Positive Rate (FPR) & Benign Approval Rate | **FPR = 0.00%**<br>**Approval Rate = 100.00%** | `EXP-007-C` | `run_tiny_s20260827_193f7897_40997ab` | `blue_metrics.json`<br>`decisions.json` | Ratio of legitimate transactions incorrectly flagged or blocked on held-out validation set. | **VALID** | 0 false blocks out of 1,398 legitimate validation transactions. |

---

## 2. External Claims & Literature Citations

| ID | Claim Text | Source & Publication | Status |
| :--- | :--- | :--- | :---: |
| **X-001** | Mastercard Verifiable Intent framework links identity, instruction, and cryptographic outcome | Mastercard Newsroom (March 2026) | Verified |
| **X-002** | Mastercard Agent Pay for Machines targets high-frequency autonomous agent rails | Mastercard Investor Relations (June 2026) | Verified |
| **X-003** | Published synthetic tabular generators score 17×–99× on behavioral fidelity degradation axes | arXiv:2604.13125 | Verified |
| **X-004** | SMOTE distorts posterior class probabilities; false alarms surge 35 $\rightarrow$ 5,775 | Dal Pozzolo et al., IJCT 2024 / IEEE SSCI 2015 | Verified |
| **X-005** | Sparkov synthetic payment dataset is CC0 public domain | Kaggle Dataset Metadata | Verified |

---

## 3. Explicit Prohibitions & Anti-Claims

We will **never** claim without direct empirical proof:
* "State-of-the-art" or "production-ready integration"
* "100% defense against zero-day fraud" (refuted by EXP-007-E finding)
* "Superiority to Mastercard production systems"
* "EMV 3DS or live payment rail integration"
* "Network latency SLAs" (only loopback benchmark is claimed)

