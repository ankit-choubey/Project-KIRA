# Project KIRA — Claim Register & Scientific Evidence Map

Every numerical claim in Project KIRA is tied to a specific metric, verification tier, and artifact path.

---

## 1. Claim Classification Tiers

- **VERIFIED**: Measured empirically in an authoritative artifact and verified against gate invariants.
- **TARGET**: An engineering design threshold or optimization goal.
- **RESULT**: Measured experimentally during Block 7 co-evolution.
- **TARGET_NOT_MET**: A hypothesis that was tested and failed (preserved for scientific integrity).

---

## 2. Master Claim Register

| Claim ID | Claim Summary | Classification | Baseline Value | Measured / Hardened Value | Artifact Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-001** | Blue Champion Baseline Out-of-Time Detection | **VERIFIED** | 0.50 (Random) | PR-AUC: 0.6407 · ROC-AUC: 0.9412 | `blue_metrics.json` |
| **CLM-002** | Isotonic Calibration Zero Expected Calibration Error | **VERIFIED** | 0.12 (Raw LGBM) | ECE: 0.0000 · Brier: 0.0051 | `calibration.json` |
| **CLM-003** | Adaptive Co-evolution Reduces Attack Evasion Rate | **RESULT** | Seen ASR: ~80.0% | Seen ASR: ~0.0% · Held-out: ~1.6% | `coevolution_metrics.json` |
| **CLM-004** | Anti-Memorization: Generalization on Held-Out Variants | **RESULT** | Held-out: 83.6% | Held-out: 1.62% ($GR \approx 1.00$) | `coevolution_metrics.json` |
| **CLM-005** | Zero-Day Transfer on Withheld Attack Families (World C) | **RESULT** | Unseen ASR | Measured on Isolated World C | `three_world_evaluation.json` |
| **CLM-006** | Minimum Evasion Distance Shifts Feature Perturbations | **RESULT** | MED: ~2.72 | MED: ~1.33 | `attack_summary.json` |
| **CLM-007** | Layer-1 Physical Validity Zero Physics Violations | **VERIFIED** | 0 violations | 0 violations enforced | `world_summary.json` |
| **CLM-008** | Statistical Marginal and Correlation Distance Bounded | **VERIFIED** | Target: $\le 0.25$ | Measured: 0.1800 | `world_summary.json` |
| **CLM-009** | External Real-World Reality Anchor (ULB 2015 Benchmark) | **VERIFIED** | — | PR-AUC: 0.8640 (284,807 txns) | `external_anchor.json` |
| **CLM-010** | End-to-End Latency Profile over Realistic Pipeline | **VERIFIED** | Target: $\le 20.0$ ms | P50: 2.15ms · P95: 4.80ms · P99: 8.30ms | `blue_metrics.json` |
| **CLM-011** | Verifiable Intent Mandate Features Filter Agent Subversion | **RESULT** | Raw ASR | Mandate Violations Caught | `exp_007_h_intent.json` |
| **CLM-012** | False Positive Rate Bounded for Legitimate Traffic | **VERIFIED** | Target: $\le 0.01$ | FPR: 0.000715 (Approval $\ge 99.6\%$) | `policy_metrics.json` |
| **CLM-013** | Anti-Forgetting: Robustness Retention on Historical Threats | **RESULT** | Target: $\ge 0.95$ | Retention: 1.0000 (No regression) | `scoreboard.json` |
| **CLM-014** | Strict Query Budget Contract Enforcement | **VERIFIED** | $B \in \{1, 5, 20, 100\}$ | $\text{queries\_used} \le B$ (100% compliant) | `attack_summary.json` |

---

## 3. Disclaimers & Safety Boundaries
- **No live payment data**: Evaluated exclusively in controlled synthetic and authorized public benchmark data.
- **No LLM in scoring critical path**: Decision routing is deterministic cost-sensitive Bayesian thresholding.
- **No SMOTE**: Class imbalance handled via `scale_pos_weight` and threshold routing to preserve probability calibration.
