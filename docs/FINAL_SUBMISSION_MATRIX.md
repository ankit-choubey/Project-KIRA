# Project KIRA — Final Submission & Capability Matrix

This matrix provides judges and reviewers with an auditable, evidence-backed evaluation of all capabilities in Project KIRA.

## Capability Matrix

| Tier | Capability | Evidence Artifact | Measured? | Metric | Scope | Limitation / Caveat | Scientific Claim |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **CORE** | Synthetic World Physics | `artifacts/run_tiny_s20260827_193f7897_40997ab/evaluation.json` | Yes | 0 Violations ($N=9,348$) | Synthetic World | Physics only; not behavioural realism | `VERIFIED` |
| **CORE** | Causal Feature Store | `research_runs/PHASE2/S00/status.json` | Yes | Zero Future Leakage ($\Delta=0.0$) | Feature Pipeline | Streaming causal state | `VERIFIED` |
| **CORE** | Tabular Fraud Detection | `artifacts/run_tiny_s20260827_193f7897_40997ab/blue_metrics.json` | Yes | PR-AUC = 1.000 / 0.9375 | Validation Split | Tiny split has 5 test positives | `MEASURED_WITH_CAVEAT` |
| **CORE** | External Reality Anchor | `artifacts/run_tiny_s20260827_193f7897_40997ab/external_anchor.json` | Yes | PR-AUC = 0.8640, FPR = 0.03% | ULB European Dataset | Independent real-world dataset | `MEASURED` |
| **RESEARCH** | Constrained Red Attacks | `research_runs/ADVANCED/ADV-001/metrics.json` | Yes | ASR = 6.00% (600/10,000) | 10k Attack Population | Geo-hop evasions only | `VERIFIED` |
| **RESEARCH** | Swarm Adaptive Memory | `research_runs/ADVANCED/ADV-002-LARGE/cross_arm_metrics.json` | Yes | ASR = 19.68% vs 9.60% (+10.08%) | 15,000 Attempts (3 arms) | Evaluated on Kaggle Cloud CPU | `VERIFIED` |
| **RESEARCH** | Closed-Loop Defense Curve | `research_runs/ADVANCED/ADV-003/adaptive_defense_curve.json` | Yes | `NO_FORGETTING` Status | Multi-Round Co-Evolution | Replay memory prevents regression | `VERIFIED` |
| **RESEARCH** | Zero-Day Attack Defense | `artifacts/run_tiny_s20260827_193f7897_40997ab/three_world_evaluation.json` | Yes | ASR = 100.00% | World C Withheld Families | Explicit failure finding | `FAILURE_FINDING` |
| **RESEARCH** | Cross-Family Transfer | `research_runs/ADVANCED/ADV-004/transferability_matrix.json` | Yes | Transfer Matrix Generated | 5x5 Family Matrix | Evaluated under bounded runner | `VERIFIED` |
| **OPERATIONS** | Degraded Telemetry Fallback | `research_runs/ADVANCED/OPS-002/metrics.json` | Yes | Governed Fallback Step-Up | Missing Device/IP/Graph | Deterministic router fallback | `VERIFIED` |
| **OPERATIONS** | Threat Intel Enrichment | `research_runs/ADVANCED/TI-001/metrics.json` | Yes | Enrichment Pipeline Verified | Synthetic Feed | Synthetic TI rules | `VERIFIED` |
| **OPERATIONS** | API Latency Benchmark | `artifacts/run_tiny_s20260827_193f7897_40997ab/latency_benchmark.json` | Yes | P95 = 2.300 ms | FastAPI /api/score | ASGI in-process loopback | `MEASURED_WITH_CAVEAT` |
| **OPERATIONS** | API Load Capacity | `research_runs/ADVANCED/OPS-001/load_curve.json` | No | 539 req/s @ 1000 req/s load | Local Dev Environment | Local test; not cloud capacity | `NOT_MEASURED` |
| **ADVANCED** | Attack Hypothesis Planner | `research_runs/ADVANCED/AG-001/metrics.json` | Yes | Mask & Physics Validation | Deterministic Heuristic | No live LLM claimed | `MEASURED_WITH_CAVEAT` |
| **ADVANCED** | Distributional Drift Monitor | `research_runs/ADVANCED/DRIFT/metrics.json` | Yes | KS Test ($p < 0.05$) | Amount Shift Stream | Statistical distribution monitor | `VERIFIED` |

---

## Prohibitions & Defensibility Principles

- **No Fabricated Numbers:** Every entry is anchored in an on-disk JSON artifact.
- **Negative Findings Preserved:** Zero-day vulnerability (100% ASR) and Intent ablation ($\Delta=0$) are reported honestly.
- **Scope Discipline:** Local loopback latency is not claimed as production network SLA.
