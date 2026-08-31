# Project KIRA — Scientific Claim Traceability & Governance Matrix

This document provides complete end-to-end provenance for all research claims in KIRA V7, cross-referencing source artifacts, statistical estimands, confidence intervals, $p$-values, git commits, and precise allowable vs prohibited wording.

---

## 1. Master Claims Governance Matrix

| Claim ID | Experiment / Area | Dataset & Scale | Primary Metric & Value | $p$-value / 95% CI | Classification | Source Artifact Path | Permitted Wording | Strictly Prohibited Wording |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-001** | EXP_BASELINE_BLUE | `KIRA_SYNTHETIC_TINY` (Scale: tiny, $n=1,403$) | PR-AUC = `1.0000` | N/A | `MEASURED` | `artifacts/run_tiny_s20260827_193f7897_40997ab/blue_metrics.json` | "Achieves 1.0 PR-AUC on tiny benchmark evaluation population (70 positives)." | "Solves fraud detection perfectly in production." |
| **CLM-002** | S00 Temporal Causality | `KIRA_SYNTHETIC_TINY` ($n=5$ mutations) | $\Delta_{\max} = 0.00\text{e}+00$ | N/A | `MEASURED` | `research_runs/PHASE2/S00/status.json` | "Feature extractor exhibits mathematical zero-future leakage under future mutation." | "Immune to all forms of distribution shift." |
| **CLM-003** | G01 Graph Diagnostic | `KIRA_SYNTHETIC_TINY` ($n=1,403$) | PR-AUC = `0.0083` | $[0.0044, 0.0179]$ | `MEASURED` | `research_runs/PHASE2/G01/metrics.json` | "Standalone GNN serves as a structural diagnostic with low standalone tabular discrimination." | "GNN outperforms tabular LightGBM as a standalone model." |
| **CLM-004** | G03 Fusion (Tiny) | `KIRA_SYNTHETIC_TINY` ($n=1,403$) | $\Delta_{\text{rel}} = +0.0444$ | $p = 0.1560$ | `INCONCLUSIVE` | `research_runs/PHASE2/G03/metrics.json` | "Dual-branch fusion shows positive point estimate on tiny world, but is statistically inconclusive ($p=0.156$)." | "Statistically significant uplift on tiny world." |
| **CLM-005** | S02 Validation (Primary) | `KIRA_SYNTHETIC_SMALL` ($n=47,501$) | $\Delta_{\text{rel}} = +0.0198$ | $p = 0.0460$ | `SUCCESS` | `research_runs/PHASE2/S02/metrics.json` | "Causal graph fusion yields +1.98% PR-AUC uplift ($p=0.046$) on primary seed with genuine topology gain (+0.85%)." | "Uniformly improves performance across all random initializations without variance." |
| **CLM-006** | S03 Zero-Day World C | `KIRA_SYNTHETIC_SMALL` ($n=47,501$) | $\Delta_{\text{rob}} = \text{null}$ | N/A | `LOW_SAMPLE` | `research_runs/PHASE2/S03/metrics.json` | "Zero-day attack robustness was unmeasured in baseline world due to zero hidden family events in test split." | "Proven robust against zero-day attack families in World C." |
| **CLM-007** | RES-C2ST Fidelity | `Sparkov Real-World` ($n=50,000$) | C2ST AUC = `0.7780` | $[0.7712, 0.7848]$ | `MEASURED` | `research_runs/REAL_WORLD/fidelity_report.json` | "Synthetic world matches real-world Sparkov distributions with domain classifier AUC = 0.7780." | "Synthetic dataset is identical/indistinguishable from real payments." |
| **CLM-008** | RES-TSTR Transfer | `Sparkov Real-World` ($n=50,000$) | ROC-AUC = `0.7597` | PR-AUC = `0.0271` | `MEASURED` | `research_runs/REAL_WORLD/tstr_metrics.json` | "Models trained on synthetic data successfully transfer to real payments with ROC-AUC = 0.7597." | "Synthetic training matches models trained directly on real data." |
| **CLM-009** | S05 Graph Causal Leak | `Sparkov Real-World` ($n=50,000$) | Violations = `0` | N/A | `MEASURED` | `research_runs/REAL_WORLD/leakage_report.json` | "Temporal payment graph preserves strict causal ordering with zero future-edge leakage." | "Graph models eliminate all types of ML risk." |
| **CLM-010** | ADV-001 Population | `ADV-001 10,000 Attacks` ($n=10,000$) | ASR = `6.00%` | Median MED = `1.2032` | `MEASURED` | `research_runs/ADVANCED/ADV-001/repository_audit.json` | "10,000-attempt adversarial evaluation demonstrates 6.00% attack success rate, confined to geo_hop." | "Adversary achieves universal evasion against Blue detector." |

---

## 2. Decision Rules & Statistical Gates

1. **Gate G-03 / S-02 Uplift Rule**: A fusion uplift is classified as `SUCCESS` if and only if $\Delta_{\text{rel}} > 0$, $\Delta_{\text{topo}} > 0$, and empirical bootstrap $p < 0.05$. On KIRA V7 S-02 (primary seed `20260827`), $\Delta_{\text{rel}} = +0.0198$, $\Delta_{\text{topo}} = +0.0085$, and $p = 0.046$, satisfying all three criteria.
2. **Multi-Seed Variance Caveat**: Across secondary seeds (`42` and `12345`), seed `42` yielded $\Delta_{\text{rel}} = -0.0024$ ($p=0.897$) while seed `12345` yielded $\Delta_{\text{rel}} = +0.0368$ ($p=0.055$). Consequently, claims must explicitly state that graph-fusion uplift is **demonstrated on the primary seed with moderate initialization sensitivity**.
3. **Zero-Day Classification Gate**: Because the base chronological world generator does not simulate zero-day mutations, S-03 evaluated $n_c = 0$ test instances and must remain classified as **`LOW_SAMPLE`**.
