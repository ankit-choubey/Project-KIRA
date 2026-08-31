# KIRA Scientific Claim & Publication Checklist

**Purpose**: Guardrail against overstated, unverified, or misleading claims in presentation, documentation, and judging materials.

---

## 1. Strictly Prohibited Claims (WITHOUT DIRECT EMPIRICAL EVIDENCE)

| Prohibited Claim | Reason / Flaw | Permitted Honest Alternative |
| :--- | :--- | :--- |
| **"PR-AUC 1.0000" as a headline capability** | PR-AUC = 1.0 occurred on a tiny validation slice containing only 5 fraud cases. | *"On a restricted tiny slice (n=5 fraud), PR-AUC reached 1.0; on broader datasets and external benchmarks, PR-AUC measured ~0.9375."* |
| **"Intent engine defeats zero-day attacks"** | EXP-007-H measured $\Delta\text{ASR} = 0.00\%$. The intent engine did not generalize to unobserved attack families. | *"Ablation confirmed the intent engine does not generalize to zero-day families ($\Delta\text{ASR}=0.00\%$), demonstrating an honest generalization boundary."* |
| **"Production latency under 1ms"** | The measured latency benchmark is a loopback timing test, not distributed production infrastructure. | *"Loopback scoring latency benchmark achieved P95 < 1.2ms (loopback benchmark, not full production network latency)."* |
| **"Hardened model successfully promoted"** | The promotion gate rejected all 4 challenger models because hardening degraded baseline false-positive / detection trade-offs. | *"The promotion gate functioned strictly as designed, rejecting 4/4 over-fitted challengers to protect production detection quality."* |
| **"Graph fusion universally improves fraud detection"** | Requires statistically significant uplift ($p < 0.05$) and topology control separation ($C - D > 0$). | *"Graph/tabular fusion evaluated under strict temporal-causal controls produced [X uplift / neutral increment] ($p = Y$)."* |
| **"Zero-day robustness validated" when sample size is low** | If hidden family test count is small ($n < 30$), metrics lack statistical power. | *"World C zero-day attacks evaluated descriptively ($n = X$); classified as LOW_SAMPLE / INCONCLUSIVE."* |
| **"Multi-seed cross-world replication proved"** | Evaluating multiple model seeds on a single world seed evaluates model stability, not independent world variance. | *"Multi-model-seed evaluation on a fixed synthetic world (world_seed=20260827, model_seeds=[20260827, 42, 12345])."* |

---

## 2. Permitted Claims (BACKED BY COMMITTED ARTIFACTS)

1. **Adversarial Vulnerability**: Unhardened baseline detector was exploited by the Red Search engine up to 96.67% ASR under 20 query probes (`coevolution_metrics.json` / `EXP-007-A`).
2. **Hardening Efficacy**: Adversarial co-evolution training reduced held-out known-variant attack success to 0.00% (`coevolution_metrics.json`).
3. **Safety Gate Integrity**: The automated promotion gate prevented regression by rejecting over-fitted candidates (`promotion_history.json`).
4. **External Anchor Validation**: Validated on real-world ULB dataset (`external_anchor.json`).
5. **Temporal-Causal Invariance**: Passed 4 temporal invariance and counterfactual mutation tests (`research_runs/PHASE2/S00/status.json`, `S01/status.json`).
