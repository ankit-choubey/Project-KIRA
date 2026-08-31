# G-03: Causal Graph + Tabular Fusion Evidence Report

- **Authoritative Baseline Run**: `run_tiny_s20260827_193f7897_40997ab`
- **Git Commit**: `f9ad563ca867f2524ac499bb0ecca49af4134575`
- **Execution Backend**: `CPU (NumPy vectorized)`
- **Decision Classification**: `INCONCLUSIVE`

## 1. Primary Estimands (Seed 20260827)
- **Arm A (Tabular Baseline) PR-AUC**: `0.9556`
- **Arm B (Graph Diagnostic) PR-AUC**: `0.0079`
- **Arm C (Real Fusion) PR-AUC**: `1.0000` (95% CI: `[1.0000, 1.0000]`)
- **Arm D (Shuffled Control) PR-AUC**: `0.9222`

### Differences
- $\Delta_{\text{rel}} (C - A)$: `+0.0444` (Bootstrap $p = 0.1560$)
- $\Delta_{\text{topology}} (C - D)$: `+0.0778`
- $\Delta_{\text{diag}} (B - A)$: `-0.9476`

## 2. Automated Scientific Conclusion
> Marginal delta (+0.0444) is statistically indistinguishable from baseline noise (p=0.1560).

## 3. Empirical Topology Verification
- Real Graph: $|V| = 623$, $|E| = 28044$, Mean Deg = 67.25
- Shuffled Graph: $|V| = 623$, $|E| = 28044$, Mean Deg = 67.25
- Degree KS Stat: 0.0000 ($p = 1.0000$)
