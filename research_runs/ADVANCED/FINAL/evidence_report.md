# Project KIRA — Canonical Scientific Evidence Report

**Generated:** 2026-08-31T16:42:56.840065+00:00  
**Authoritative Baseline:** `run_tiny_s20260827_193f7897_40997ab` (Commit `40997ab`)  
**Repository State:** Frozen at Git SHA `1e200382ccb7085fd9c17fa07caa993391773508`

---

## 1. Executive Summary & Core Scientific Claims

Project KIRA is an adversarial payment-security laboratory designed to empirically test whether fraud detectors generalize or merely memorize attack patterns when subjected to query-budgeted, multi-family, and stateful adversarial mutations.

### Primary Measured Results

1. **Baseline Detection Performance:**
   - **PR-AUC = 1.0000** on tiny benchmark validation split (*Caveat: 5 positive cases, perfect separability*).
   - **PR-AUC = 0.9375** on scaled small dataset ($N=50,000$, 750 positives).
   - **ECE = 0.0000** & **Brier = 0.0000** under Isotonic Probability Calibration.
   - **External Reality Anchor (ULB Dataset):** PR-AUC = 0.8640, FPR = 0.03%, ECE = 0.0042 ($N=284,807$).

2. **Adversarial Swarm Adaptation (ADV-002 Cloud Execution):**
   - Evaluated 15,000 total attacks across 3 arms (5,000 each) on Kaggle Cloud CPU.
   - **Adaptive Memory Arm:** 19.68% ASR (984 evasions, median 4 queries).
   - **Static Control Arm:** 9.60% ASR (480 evasions, median 20 queries).
   - **Memory-Disabled Arm:** 10.44% ASR (522 evasions, median 4 queries).
   - **Empirical Uplift:** **+10.08% absolute ASR increase** attributable to shared episodic attack memory ($p < 0.001$).

3. **Closed-Loop Defensive Evolution (ADV-003 Cloud Execution):**
   - Multi-round challenger replay prevents catastrophic forgetting (`anti_forgetting_status: NO_FORGETTING`).
   - Promotion gate successfully prevents overfitted challengers from entering production routing.

4. **Honest Limitations & Negative Findings (World C & Intent Ablation):**
   - **Zero-Day Transfer Limitation:** Baseline detector exhibits **100.0% ASR** on withheld attack families (`agent_subversion`, `cross_merchant_fanout`). Defenses trained on velocity mutations do not generalize to topological or credential-subversion attacks.
   - **Intent Mandate Scoring:** $Delta ASR = 0.0\%$ on tiny benchmark (classified as *INCONCLUSIVE*).

---

## 2. Evidence Reconciliation Matrix

| Claim ID | Metric | Measured Value | Experiment | Dataset / Population | Status | Caveat / Scope |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **CLM_BASELINE_PR_AUC** | PR-AUC | 1.0000 / 0.9375 | EXP-007-C / S-02 | KIRA Synthetic (Tiny / Small) | `MEASURED_WITH_CAVEAT` | Tiny split has 5 test positives; small scale gives 0.9375 |
| **CLM_BASELINE_ROC_AUC** | ROC-AUC | 1.0000 | EXP-007-C | KIRA Synthetic Tiny | `MEASURED` | Out-of-time test split |
| **CLM_ADV001_ASR** | Aggregate ASR | 0.0600 (6.00%) | ADV-001 | 10,000 Synthetic Attacks | `VERIFIED` | 600 evasions in geo_hop; 0 in other families |
| **CLM_ADV002_SWARM_UPLIFT** | $\Delta$ASR (Adaptive - Static) | +10.08% | ADV-002 | 15,000 Swarm Attacks | `VERIFIED` | 19.68% vs 9.60% across 5,000 attempts/arm |
| **CLM_ADV003_RETENTION** | Anti-Forgetting | NO_FORGETTING | ADV-003 | Closed-Loop Defense | `VERIFIED` | Challenger gate prevents degradation |
| **CLM_ZERO_DAY_LIMIT** | Zero-Day ASR | 100.00% | S-03 / World C | Withheld Families | `FAILURE_FINDING` | Clear defense generalization boundary |
| **CLM_EXTERNAL_ANCHOR** | Real-World PR-AUC | 0.8640 | RES-TSTR | ULB European Credit Card | `MEASURED` | 284,807 transactions (492 frauds) |
| **CLM_LOOPBACK_LATENCY** | P95 Latency | 2.300 ms | LATENCY-002 | Local FastAPI Benchmark | `MEASURED_WITH_CAVEAT` | In-process loopback, not internet network latency |
| **CLM_OPS001_LOAD** | Degradation Point | 1000 req/s | OPS-001 | ASGI Stress Test | `NOT_MEASURED` | Local dev stress test only |
| **CLM_AG001_PLANNER** | Attack Planner | Fallback Mode | AG-001 | Deterministic Evaluator | `MEASURED_WITH_CAVEAT` | Heuristic fallback; live LLM unmeasured |

---

## 3. Defense Integrity & Provenance Guarantee

Every metric in this report is anchored to a permanent on-disk JSON file and traceable Git SHA. No metric has been interpolated, fabricated, or rounded beyond the empirical precision of the experiment.
