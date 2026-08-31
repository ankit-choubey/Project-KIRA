# LIMITATIONS

Technical report asset detailing system constraints, empirical generalization boundaries, and measured limitations.

Stating what was measured, what failed, and what was cut demonstrates scientific integrity. Silence about limitations reads as ignorance.

---

## 1. What this system is

A controlled adversarial payment-security laboratory. It identifies attack families, generates constrained synthetic attacks, evaluates their fidelity and evasion, detects them with a multi-signal defense, records failure lineages, and evaluates whether subsequent challenger models measurably improve generalisation over memorisation.

## 2. What this system is not

- Not a production fraud system, and not benchmarked against live cardholder traffic
- Not connected to any real payment rail
- Not trained on real cardholder data or PII
- Not an official implementation of Mastercard's Verifiable Intent, Agent Pay, AP2, or EMV 3DS
- Not a theoretical guarantee against arbitrary unknown attack topologies

---

## 3. Data & Scale Limitations

**The world is synthetic.** Our simulator is calibrated against public reference datasets (Sparkov CC0), but it is our own model of payment behavior. Behaviors not modeled in the generative ledger cannot be detected by the fitted models.

**Scale and Positive Sample Density.** Authoritative demonstration runs were executed on `tiny` scale (9,348 transactions, 53 total frauds) and `small` scale. In the `tiny` validation split, only 5 positive fraud cases exist among 1,398 benign transactions. Consequently, the observed **PR-AUC = 1.0000** on `tiny` is an empirical artifact of near-perfect separability on a small positive slice, and **must not be interpreted as representative of real-world production performance**. Representative higher-statistical-power performance is captured on `small` scale (**PR-AUC = 0.9375**).

**Behavioral Fidelity Filter (L3 P1–P4) & L4 C2ST.** While Layer 1 physical validity (0 violations) and Layer 2 correlation distance (0.18) were strictly measured, Layer 3 behavioral degradation ratios (P1 interarrival, P2 burstiness, P3 graph motif, P4 velocity trigger) and Layer 4 Classifier 2-Sample Test (C2ST) were **not measured** in the final bounded experiment and remain reported as `null`.

---

## 4. Modeling & Intent Layer Limitations

**Single detector family.** LightGBM champion with isotonic calibration. Deep learning, Transformer architectures, and Graph Neural Networks (GNNs) were intentionally cut in favor of simple, causal, explainable features.

**Verifiable Intent Ablation is Inconclusive at Tiny Scale.** Controlled 2-arm ablation (EXP-007-H) comparing `WITH_INTENT` (model trained on 28 features with mandate verification) versus `WITHOUT_INTENT` (model trained on 27 features without `is_agent_initiated` and with `mandates={}`) showed $\Delta\text{PR-AUC} = 0.0000$ and $\Delta\text{ASR} = 0.00\%$. The intent verification engine is a functional capability, but static mandate checks did not provide measurable evasion reduction against unadapted agent subversion at tiny scale.

**Calibration on Limited Positives.** Fraud is rare (0.567% base rate), so isotonic calibration is fitted on relatively few positive examples. ECE = 0.0000 reflects zero measured calibration error on this benchmark partition, not a mathematical proof across all distributions.

---

## 5. Adversarial Red Team & Zero-Day Findings

**Threat model is explicit and constrained.** Red attackers operate under strict query budgets ($B \in \{1, 5, 20, 100\}$) and mutate only fields permitted by the declarative mutability mask. We do not model insider compromise, model extraction, or physical point-of-sale tampering.

**Zero-Day Defensive Boundary (World C).** In EXP-007-E, when the hardened Champion was evaluated against entirely withheld attack families (`agent_subversion` and `cross_merchant_fanout`), attackers achieved **100.00% ASR at budget 20** (MED = 3.7706). **This is a valid empirical failure finding**: hardening against velocity-based adaptation families fails to generalize to novel multi-merchant fanout or agent credential drift topologies.

**Minimum Evasion Distance (MED) Semantics.** Baseline static Red achieves MED = 2.8488. In rounds where the hardened Challenger caught 100% of candidate attacks (0 evasions), MED is mathematically undefined and recorded as `null` (never converted to 0.0).

---

## 6. Latency & Infrastructure Limitations

**In-Process HTTP Loopback Measurement.** Scoring latency was measured via high-resolution in-process ASGI TestClient requests over `/api/score` (P50 = 2.223 ms, P95 = 2.300 ms, P99 = 2.361 ms across 200 measured requests). These figures reflect local endpoint parsing, feature extraction, policy routing, and JSON serialization. They **do not include production internet network hops, WAN latency, or distributed database synchronization**.

**External Reality Anchor.** The external anchor uses 284,807 European cardholder transactions (ULB 2013, Dal Pozzolo et al., DOI: 10.1109/SSCI.2015.33; PR-AUC = 0.8640). Because the ULB benchmark uses PCA-transformed features, performance on this dataset provides contextual validation only and is not directly comparable to KIRA's synthetic feature representation.

---

## 7. Components Deliberately Not Built

| Component | Rationale for Cut |
| :--- | :--- |
| **Graph Neural Networks (GNN)** | Causal graph features (`device_cust_count`, merchant fraud lag) provided sufficient relational signal without deep learning overhead. |
| **Reinforcement Learning / Diffusion** | Heuristic constrained search provided faster, reproducible, falsifiable perturbation bounds within query budgets. |
| **Generative Replay / Distillation** | Prioritized replay buffer with strict lineage grouping was sufficient to prevent catastrophic forgetting. |
| **Real-world Payment Rail Integration** | Out of scope; synthetic stateful ledger guarantees zero PII exposure. |

---

## 8. Responsible Disclosure

All algorithms operate on synthetic data and open-access public benchmarks. No proprietary Mastercard cardholder records, card numbers, or live banking credentials were used or exposed.

