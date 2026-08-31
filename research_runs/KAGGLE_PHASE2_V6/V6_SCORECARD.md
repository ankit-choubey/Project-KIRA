# KIRA Master Scientific Scorecard (V6 Post-Audit)

| Capability | Evidence Artifact | Measured Result | Classification | Confidence | Main Caveat |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Tabular Fraud Detection** | `artifacts/run_tiny_.../blue_metrics.json` | PR-AUC: `1.0`, ROC-AUC: `1.0`, FPR: `0.00%` | `MEASURED` | High | Small sample size ($n=1,403$, 70 fraud). |
| **Adaptive Red** | `artifacts/run_tiny_.../red_metrics.json` | Round-0 ASR: `15.15%` $\rightarrow$ Round-1: `15.15%` | `MEASURED` | High | Evaluated on fixed tiny test set. |
| **Blue Hardening** | `artifacts/run_tiny_.../coevolution_metrics.json` | Seen ASR: `0.00%`, Replay Generalization: PASS | `MEASURED` | High | Measured against canonical mutation grid. |
| **Held-out Generalization** | `artifacts/run_tiny_.../experiment_register.json` | Held-out variant ASR: `0.00%` | `MEASURED` | High | Parameterized over 5 canonical families. |
| **Zero-Day Robustness** | `research_runs/PHASE2/G04/metrics.json` | World-C test samples: `0` | `LOW_SAMPLE` | Low | Full-scale S-03 world generation failed. |
| **Intent Verification** | `artifacts/run_tiny_.../intent_ablation.json` | Intent drift detection: `PASS` | `MEASURED` | High | Evaluated on simulated agent transactions. |
| **Graph Modelling** | `research_runs/PHASE2/G01/metrics.json` | Standalone GNN PR-AUC: `0.0083` | `MEASURED` | High | Graph topology alone has weak stand-alone signal. |
| **Graph Fusion** | `research_runs/PHASE2/G03/metrics.json` | $\Delta_{\text{rel}} = +0.0444$, $p = 0.156$ | `INCONCLUSIVE` | Medium | Uplift not statistically significant vs baseline noise. |
| **Temporal Causality** | `output/research_runs/S-05/leakage_audit.json` | `0` future edge / label violations across 28k edges | `MEASURED` | Very High | Cryptographically and temporally verified. |
| **Behavioral Fidelity** | `output/research_runs/S-02/metrics.json` | Interarrival ratio: `9.74x`, Burstiness diff: `-0.1667` | `MEASURED_WITH_CAVEAT` | High | Sparkov schema lacks client device telemetry. |
| **C2ST Discriminator** | `output/research_runs/RES-C2ST/metrics.json` | Discriminator AUC: `0.7780` (95% CI: `[0.764, 0.792]`) | `MEASURED` | High | Indicates synthetic and real domains are distinguishable. |
| **TSTR Transfer** | `output/research_runs/RES-TSTR/metrics.json` | TSTR ROC-AUC: `0.7597` (TRTR: `0.9708`), $\Delta$PR-AUC: `-0.3789` | `MEASURED` | High | Feature ranking transfers; precision shows domain gap. |
| **Calibration** | `artifacts/run_tiny_.../calibration.json` | Isotonic Calibrator ECE: `0.000` | `MEASURED` | High | Calibrated strictly on out-of-time validation. |
| **Scoring Latency** | `artifacts/run_tiny_.../latency_benchmark.json` | Tabular P95: `0.85ms`, Fusion: `2.49ms` | `MEASURED` | Very High | Well within < 10ms real-time SLA. |
| **Provenance Integrity**| `artifacts/run_tiny_.../provenance.json` | 22 / 22 artifacts cryptographically matched | `MEASURED` | Very High | 100% SHA-256 integrity preserved. |
