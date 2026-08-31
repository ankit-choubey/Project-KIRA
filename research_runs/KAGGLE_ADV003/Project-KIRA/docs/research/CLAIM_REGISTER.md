# Project KIRA — Claim Register & Scientific Evidence Map

Every numerical claim in Project KIRA is tied to a specific metric, verification tier, and artifact path.

**Authoritative Candidate Run:** `run_tiny_s20260827_193f7897_40997ab` (Commit `40997ab`)  
**Supporting Reference Run:** `run_small_s20260827_3a353e9a_052dca8` (Commit `052dca8`)

---

## 1. Claim Classification Tiers

- **VERIFIED**: Measured empirically in an authoritative artifact and verified against gate invariants.
- **TARGET**: An engineering design threshold or optimization goal.
- **RESULT**: Measured experimentally during Block 7 co-evolution.
- **FAILURE_FINDING**: An empirical failure boundary discovered during testing (preserved for scientific honesty).

---

## 2. Master Claim Register

| Claim ID | Claim Summary | Classification | Baseline Value | Measured / Hardened Value | Artifact Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-001** | Blue Champion Baseline Out-of-Time Detection | **VERIFIED (CAVEAT)** | 0.50 (Random) | PR-AUC: 1.0000 *(Tiny)* · 0.9375 *(Small)* | `blue_metrics.json` |
| **CLM-002** | Isotonic Calibration Zero Expected Calibration Error | **VERIFIED (CAVEAT)** | Raw LGBM Probs | ECE: 0.0000 · Brier: 0.0000 | `calibration.json` |
| **CLM-003** | Query-Budgeted Static Attacker Curve (EXP-007-A) | **RESULT** | ASR@1: 33.33% | ASR@5: 76.67% · ASR@20: 96.67% | `exp_007_a_static.json` |
| **CLM-004** | Anti-Memorization: Generalization on Held-Out Variants | **RESULT** | Held-out: 14.55% | Hardened: 0.00% ($GR = 1.3071$) | `promotion_history.json` |
| **CLM-005** | Zero-Day Transfer on Withheld Attack Families (World C) | **FAILURE_FINDING** | Target: Transfer | Withheld ASR: 100.00% (MED: 3.77) | `three_world_evaluation.json` |
| **CLM-006** | Minimum Evasion Distance Perturbation Boundary | **RESULT** | Baseline: 2.8488 | Challenger: null (0 evasions) | `scoreboard.json` |
| **CLM-007** | Layer-1 Physical Validity Zero Physics Violations | **VERIFIED** | 0 violations | 0 violations enforced | `world_summary.json` |
| **CLM-008** | Statistical Marginal and Correlation Distance Bounded | **VERIFIED** | Target: $\le 0.25$ | Measured: 0.1800 | `world_summary.json` |
| **CLM-009** | External Real-World Reality Anchor (ULB 2015 Benchmark) | **VERIFIED** | — | PR-AUC: 0.8640 (284,807 txns) | `external_anchor.json` |
| **CLM-010** | End-to-End Latency Profile over HTTP Benchmark Path | **VERIFIED** | Target: $\le 20.0$ ms | P50: 2.223ms · P95: 2.300ms · P99: 2.361ms | `latency_benchmark.json` |
| **CLM-011** | Verifiable Intent Mandate Ablation on Agent Subversion | **RESULT (NEUTRAL)** | Without: 100% ASR | With: 100% ASR ($\Delta = 0.0\%$) | `intent_ablation.json` |
| **CLM-012** | False Positive Rate Bounded for Legitimate Traffic | **VERIFIED** | Target: $\le 0.01$ | FPR: 0.0000 (Approval = 100.0%) | `policy_metrics.json` |
| **CLM-013** | Anti-Forgetting: Robustness Retention on Historical Threats | **RESULT** | Target: $\ge 0.95$ | Retention: 1.3071 | `promotion_history.json` |
| **CLM-014** | Strict Query Budget Contract Enforcement | **VERIFIED** | $B \in \{1, 5, 20, 100\}$ | $\text{queries\_used} \le B$ (100% compliant) | `attack_summary.json` |

---

## 3. Disclaimers & Safety Boundaries
- **No live payment data**: Evaluated exclusively in controlled synthetic and authorized public benchmark data.
- **No LLM in scoring critical path**: Decision routing is deterministic cost-sensitive Bayesian thresholding.
- **No SMOTE**: Class imbalance handled via `scale_pos_weight` and threshold routing to preserve probability calibration.

