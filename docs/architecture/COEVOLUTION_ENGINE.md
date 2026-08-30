# Architecture Document: Adaptive Red/Blue Co-Evolution Engine

## 1. Executive Summary

The **Adaptive Red/Blue Co-Evolution Engine** transforms static payment fraud detection into an iterative, failure-driven adversarial laboratory. 

Rather than training a static classifier on fixed fraud examples, Project KIRA orchestrates multi-round adversarial competition between:
1. **Adaptive Red Team**: Uses diagnosed defensive weaknesses (`WeaknessProfile`) to re-seed search distributions and perturb transactions along vulnerable decision boundaries under strict physical constraints and query budgets.
2. **Failure Analyzer**: Classifies successful evasions into a 12-class payment security taxonomy (`W1`–`W12`), computing hardness, boundary proximity, novelty, and priority scores.
3. **Prioritized Replay Buffer**: Retains high-value evasions and translates them into observable feature rows without metadata leakage.
4. **Blue Challenger & Multi-Objective Promotion Gate**: Hardens defender models via controlled retraining, evaluating Detection (PR-AUC), Robustness (Held-out ASR), Calibration (ECE), Anti-Forgetting (Retention), Latency, and Expected Financial Loss.

---

## 2. Component Diagram

```text
                               ┌───────────────────────────┐
                               │   Synthetic Payment World │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │  Causal Streaming Features│
                               └─────────────┬─────────────┘
                                             │
                                             ▼
    ┌──────────────────────────────► Blue Champion ◄───────────────────────────┐
    │                                        │                                 │
    │                                        ▼                                 │
    │                            Adaptive Red Search Engine                    │
    │                                        │                                 │
    │                                        ▼                                 │
    │                            Budget & Mask Enforcement                     │
    │                                        │                                 │
    │                                        ▼                                 │
    │                             Failure Diagnosis (W1..W12)                  │
    │                                        │                                 │
    │                                        ▼                                 │
    │                             Prioritized Replay Buffer                    │
    │                                        │                                 │
    │                   ┌────────────────────┴────────────────────┐            │
    │                   ▼                                         ▼            │
    │            Weakness Profile                        Challenger Trainer    │
    │                   │                                         │            │
    │                   ▼                                         ▼            │
    │            Adaptive Reseeding                      Challenger Evaluation │
    │                   │                               (Three-World Suite)    │
    │                   │                                         │            │
    │                   │                                         ▼            │
    │                   │                                  Promotion Gate ─────┤ (Rollback on Fail)
    │                   │                                         │            │
    │                   │                                         ▼ (PASS)     │
    └───────────────────┴─────────────────────────────────── New Champion ─────┘
```

---

## 3. The 12-Class Failure Taxonomy (`W1`–`W12`)

| Code | Name | Description |
| :--- | :--- | :--- |
| **W1** | Velocity Blindness | Rapid transactions within rolling windows evading rate limits. |
| **W2** | Device Novelty Blindness | First-seen devices mimicking legitimate device migrations. |
| **W3** | Geographic Camouflage | Physical locations altered within realistic travel speed tolerances. |
| **W4** | Merchant Collusion | Spending routed through fraudulent or collusive merchant categories. |
| **W5** | Low-and-Slow Behavior | Micro-transactions staying beneath amount-based alerting thresholds. |
| **W6** | Graph Camouflage | Structurally distributed funds through fan-out networks. |
| **W7** | Intent Drift | Autonomous AI payment agent deviating from user-authorized mandates. |
| **W8** | Coordinated Multi-Account | Sybil accounts coordinating velocity across multiple merchant categories. |
| **W9** | Synthetic Identity | Fabricated identity entities mimicking legitimate credit profiles. |
| **W10** | Agent Swarm Behavior | Multi-agent automated payment swarms coordinating transactions. |
| **W11** | Temporal Camouflage | Exploiting off-peak hours or recurring billing channels. |
| **W12** | Open-Set Anomaly | Novel transaction structures outside standard training distributions. |

---

## 4. Multi-Objective Promotion Criteria

Promotion requires meeting all six thresholds simultaneously:

1. **Security Gain**: $\text{ASR}_{\text{seen}}(\text{Challenger}) < \text{ASR}_{\text{seen}}(\text{Champion})$ or $\text{ASR}_{\text{heldout}}(\text{Challenger}) < \text{ASR}_{\text{heldout}}(\text{Champion})$.
2. **Anti-Memorization**: $\text{ASR}_{\text{heldout}}(\text{Challenger}) \le \text{ASR}_{\text{heldout}}(\text{Champion}) + 0.05$.
3. **Anti-Forgetting**: $\text{Robustness Retention} \ge 0.95$.
4. **Legitimate Traffic Protection**: $\text{FPR} \le 0.05$ (Target $\le 0.001$) and $\text{Approval Rate} \ge 70\%$ (Target $\ge 99\%$).
5. **Calibration Quality**: $\text{ECE} \le 0.08$.
6. **Latency Budget**: $P_{95} \le 25.0$ ms.

If any criterion fails, **Rollback** preserves the existing Champion without disruption.
