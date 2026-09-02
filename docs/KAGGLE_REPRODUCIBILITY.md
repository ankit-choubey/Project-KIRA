# Project KIRA — Kaggle Research Reproducibility Index

**Target Platform:** Kaggle CPU Notebooks (4 Cores / 30 GB RAM / Zero GPU)  
**Authoritative Baseline:** `run_tiny_s20260827_193f7897_40997ab`  

---

## 1. Reproducibility Guarantee

In accordance with KIRA research rules, all heavy compute was executed on standard Kaggle CPU instances. No numbers are fabricated or estimated. Anyone with a verified Kaggle account can re-run these notebooks from scratch to reproduce every artifact and metric.

---

## 2. Notebook Execution Matrix

| Experiment ID | Notebook File | Purpose | Hardware / Scale | Runtime | Output Artifacts | Reproducibility Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`EXP_BLOCK_6`** | [`notebooks/kaggle/02_full_run.ipynb`](file:///Users/theankit/Documents/AK/Projects/Project-KIRA/notebooks/kaggle/02_full_run.ipynb) | Full end-to-end payment world, feature extraction, baseline training, and 3-round co-evolution | Kaggle CPU (Full Scale) | ~115 min | `evaluation.json`, `manifest.json`, `decisions.json`, `attack_summary.json` | **VERIFIED** |
| **`EXP_REAL_WORLD`** | [`notebooks/kaggle/03_real_world_validation.ipynb`](file:///Users/theankit/Documents/AK/Projects/Project-KIRA/notebooks/kaggle/03_real_world_validation.ipynb) | Sparkov real-world transfer, C2ST fidelity validation, and temporal causal invariance tests | Kaggle CPU (50K txns) | ~25 min | `external_anchor.json`, `fidelity_report.json`, `tstr_metrics.json` | **VERIFIED** |
| **`EXP_PHASE2_FUSION`** | [`notebooks/kaggle/04_phase2_mega_notebook.ipynb`](file:///Users/theankit/Documents/AK/Projects/Project-KIRA/notebooks/kaggle/04_phase2_mega_notebook.ipynb) | S-00 to S-04 Graph-Tabular Fusion (Arm A tabular vs. Arm D causal graph fusion) | Kaggle CPU (47,501 txns) | ~8.5 min | `master_results.json`, `comparison_table.json`, `S02/metrics.json` | **VERIFIED** |
| **`EXP_ADV002_SWARM`** | [`notebooks/kaggle/05_adv002_large_swarm.ipynb`](file:///Users/theankit/Documents/AK/Projects/Project-KIRA/notebooks/kaggle/05_adv002_large_swarm.ipynb) | ADV-002 15,000 stateful adversarial swarm attack simulation | Kaggle CPU (15K entities) | ~18 min | `adv002_swarm_telemetry.json`, `population_matrix.json` | **VERIFIED** |
| **`EXP_ADV003_HARDEN`** | [`notebooks/kaggle/06_adv003_adaptive_defense.ipynb`](file:///Users/theankit/Documents/AK/Projects/Project-KIRA/notebooks/kaggle/06_adv003_adaptive_defense.ipynb) | ADV-003 Adaptive Challenger Hardening, retention, and anti-memorization audit | Kaggle CPU | ~12 min | `adaptive_metrics.json`, `retention_matrix.json` | **VERIFIED** |

---

## 3. How to Run on Kaggle

1. Open [Kaggle](https://www.kaggle.com) and click **Code → New Notebook**.
2. Set **Accelerator: None (CPU)**, **Internet: On**, and **Persistence: Files only**.
3. Upload any notebook from `notebooks/kaggle/` or clone the repository:
   ```bash
   !git clone https://github.com/ankit-choubey/Project-KIRA.git
   %cd Project-KIRA
   !pip install -e ".[heavy]"
   ```
4. Click **Run All**. Checkpointed artifacts will be written directly to disk.
