# Project KIRA — Evidence Pack & Audit Report

**Run ID:** `run_tiny_s20260827_193f7897_9cfa1e1`  
**Git Commit:** `9cfa1e1`  
**Configuration Hash:** `193f789727f6`  
**Random Seed:** `20260827`  
**Execution Scale:** `tiny`  

---

## 1. Executive Summary
Project KIRA (Mastercard AI Defense Lab) measures whether adversarial hardening against adaptive
payment fraud generalises rather than memorises. Through a 4-round coevolutionary loop with 5 canonical attack families,
KIRA tracks Seen ASR, Held-out Variant ASR, and Minimum Evasion Distance (MED) while preserving
strictly causal features, zero label leakage, and high benign transaction approval.

## 2. World & Physics Validity (Layer 1 Filter)
- **Total Transactions:** 9348
- **Customers / Merchants / Devices:** 200 / 80 / 1294
- **Base Fraud Count / Rate:** 53 (0.5670%)
- **Physical Validity Violations:** 0 (Zero violations enforced)

## 3. Causal Feature Store Specification
- **Feature Count:** 25 canonical features dynamically registered.
- **Causal Guarantee:** Strictly ordered by `(timestamp, txn_id)` ascending. Zero future event reads.
- **Label-Delay Lag:** 7-day (604,800s) mandatory chargeback confirmation cutoff.

## 4. Blue Detector Baseline & Calibration
- **Model Version:** LightGBM Champion with Isotonic Probability Calibration
- **Test PR-AUC:** 0.640716
- **Test ROC-AUC:** 0.900143
- **Expected Calibration Error (ECE):** 0.0
- **Brier Score:** 0.001282
- **False Positive Rate (FPR):** 0.000715

## 5. Red Team Adversarial Attack Search
- **Attack Families Evaluated:** `burst_drain`, `slow_siphon`, `geo_hop`, `agent_subversion`, `cross_merchant_fanout`
- **Query Budgets:** 1, 5, 20, 100
- **Mask Violations:** 0 (Strict immutable field enforcement)
- **Mean Evasion Distance (MED):** 1.3291

## 6. Coevolution Generalisation Loop

| Round | Champion | Challenger | Seen ASR | Held-out ASR | Generalisation Retention | Promoted |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | blue_r0_baseline | None | 75.00% | 83.64% | 1.0000 | Yes |
| 1 | blue_r1 | challenger_r1 | 0.00% | 0.00% | 1.0203 | Yes |
| 2 | blue_r2 | challenger_r2 | 0.00% | 0.00% | 0.9680 | Yes |
| 3 | blue_r3 | challenger_r3 | 0.87% | 1.62% | 1.0007 | Yes |

**ASR Progression:**
- Baseline Round 0: Seen ASR = `75.00%`, Held-out ASR = `83.64%`
- Final Round: Seen ASR = `0.87%`, Held-out ASR = `1.62%`

## 7. Customer Impact & Policy Distribution
- **ALLOW Count:** 1398
- **STEP_UP Count:** 0
- **BLOCK Count:** 5

## 8. External Real-World Reality Anchor (Namespace: `REAL_WORLD`)
- **Source Organization:** ULB Machine Learning Group (Université Libre de Bruxelles)
- **Dataset Reference:** Credit Card Fraud Detection Benchmark (2015)
- **Citation / DOI:** 10.1109/SSCI.2015.33
- **Real Transactions Evaluated:** 284,807 (492 frauds, 0.1727%)
- **PR-AUC on Real Benchmark:** 0.864
- **ROC-AUC on Real Benchmark:** 0.982

## 9. Reproducibility Guarantee
Every metric and artifact in this run is derived deterministically from the specified configuration hash
and random seed. All generated artifacts are cryptographically hashed using SHA-256 into `provenance.json`.

## 10. Limitations & Scientific Disclaimers
- **Demonstrated:** In a controlled stateful payment simulation, lineage-isolated replay training reduces
  ASR against both seen and held-out attack variants while bounding false positive rates.
- **Simulated:** Agent mandates, autonomous agent transactions, and multi-round mutations reflect synthetic models.
- **Not Demonstrated:** Synthetic performance does not imply direct transference of absolute numbers to live
  production networks without domain adaptation and live production telemetry.
