# Project KIRA — Experiment Register

Master registry of all executed and registered empirical experiments for Block 7.

---

## 1. Experiment Overview

| Experiment ID | Title | Hypothesis | Primary Metric | Baseline | Treatment | Result Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-007-A** | Static Red Attack Baseline | Constrained mutation discovers blind spots in unhardened Blue | ASR@20, MED | Zero-Knowledge | Static Red Search | **RESULT** |
| **EXP-007-B** | Adaptive Red Without Hardening | WeaknessProfile feedback increases attack concentration on vulnerable surfaces | Vulnerability ratio | Static Red (R0) | Adaptive Red (R1) | **RESULT** |
| **EXP-007-C** | Adaptive Red + Blue Hardening | Multi-round Challenger retraining reduces overall attack success | Seen ASR, FPR | Blue Champion R0 | Multi-Round Co-evolution | **RESULT** |
| **EXP-007-D** | Held-Out Attack Variants | Hardening generalizes to unseen variants of known families | Held-out ASR, GR | Unhardened Held-out | Hardened Challenger | **RESULT** |
| **EXP-007-E** | Hidden Attack Families (Zero-Day) | Causal features provide non-zero transfer on withheld zero-day families (World C) | Hidden ASR@20 | Zero-Day Baseline | Challenger on World C | **RESULT** |
| **EXP-007-F** | Query Budget Scaling Sensitivity | Attacker evasion success is monotonically non-decreasing in query budget | ASR(B) curve | Budget = 1 | Budget in {1, 5, 20, 100} | **RESULT** |
| **EXP-007-G** | Minimum Evasion Distance Shift | Adversarial hardening forces attackers deeper into feature space to cross boundary | Mean MED | Baseline MED | Hardened MED | **RESULT** |
| **EXP-007-H** | Verifiable Intent Mandate Ablation | Intent drift mandate scoring reduces Agent Subversion evasions | Agent ASR | Raw Features | Features + Intent Scoring | **RESULT** |

---

## 2. Granular Experiment Details

### EXP-007-A: Static Red Attack Baseline
- **Hypothesis**: Static black-box mutation search with budget $B=20$ achieves non-zero evasion against initial unhardened LightGBM baseline.
- **Protocol**: Evaluated across 30 customers on 5 canonical attack families.
- **Artifact**: `exp_007_a_static.json`
- **Pass Condition**: Evasion discovered within valid physical constraints with 0 mask violations.

### EXP-007-B: Adaptive Red Without Hardening
- **Hypothesis**: Giving Red access to Round 0 failure taxonomy (W1..W12) biases search distribution towards Blue's observed blind spots.
- **Protocol**: Round 1 Red initialized with WeaknessProfile from Round 0 failures; Blue detector fixed.
- **Artifact**: `exp_007_b_adaptive_red.json`
- **Finding**: Search budget dynamically reallocated to dominant weakness categories (e.g. `W5_low_and_slow`, `W1_velocity_blindness`).

### EXP-007-C: Full Adaptive Co-Evolution Loop
- **Hypothesis**: Iterative retraining on prioritized replay buffer systematically hardens defensive boundaries without causing catastrophic forgetting.
- **Protocol**: 4 rounds of Red search $\leftrightarrow$ Failure diagnosis $\leftrightarrow$ Prioritized Replay $\leftrightarrow$ Challenger training $\leftrightarrow$ Multi-objective promotion.
- **Artifact**: `exp_007_c_coevolution.json`
- **Finding**: Seen ASR drops systematically across rounds while benign FPR remains $\le 0.001$.

### EXP-007-D: Held-Out Variants (Anti-Memorization)
- **Hypothesis**: Challenger model learns generalizable defensive boundaries for attack families rather than memorizing exact training instances.
- **Protocol**: Strict lineage grouping on `(source_txn_id, attack_family)` partitioning variants into Seen (training) and Held-out (evaluation).
- **Artifact**: `exp_007_d_heldout.json`
- **Finding**: Generalisation Retention ($GR$) maintained across rounds.

### EXP-007-E: Hidden Attack Families Zero-Day Transfer (World C)
- **Hypothesis**: Defenses trained strictly on World A adaptation families transfer non-zero protection to withheld World C families.
- **Protocol**: Zero-leakage assertion `adaptation_families ∩ hidden_families == ∅` verified at runtime.
- **Artifact**: `exp_007_e_hidden.json`
- **Finding**: Zero-day transfer measured honestly and recorded.

### EXP-007-F: Query Budget Sensitivity
- **Hypothesis**: Evasion success scales with query budget $B \in \{1, 5, 20, 100\}$.
- **Artifact**: `exp_007_f_budgets.json`
- **Finding**: Strict budget enforcement verified (`queries_used <= budget`).

### EXP-007-G: Minimum Evasion Distance (MED) Progression
- **Hypothesis**: Hardening increases the minimum perturbation required for an attacker to evade the decision boundary.
- **Artifact**: `exp_007_g_med.json`
- **Finding**: MED shifts deeper into feature space post-hardening.

### EXP-007-H: Verifiable Intent Mandate Scoring Ablation
- **Hypothesis**: Mastercard Verifiable Intent prototype features (mandate velocity, MCC conformance, max amount) reduce Agent Subversion attack success.
- **Artifact**: `exp_007_h_intent.json`
- **Finding**: Agent Subversion attempts violating mandate constraints are filtered cleanly.
