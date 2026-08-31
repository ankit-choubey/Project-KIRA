# Kaggle Phase-2 V6 File Inventory & Provenance

**Execution Run ID**: `theankitchoubey/project-kira-phase2-mega-notebook` (V6)  
**Execution Platform**: Kaggle Cloud (4-Core CPU, 30 GB RAM, Linux-x86_64)  
**Execution Timestamp**: 2026-08-31T06:57:51Z – 2026-08-31T10:54:18Z (~3.9 hours)  
**Git Commit at Launch**: `f9ad563ca867f2524ac499bb0ecca49af4134575`  
**Master Seed**: `20260827` (Multi-seeds: `[20260827, 42, 12345]`)  
**Status**: `KernelWorkerStatus.COMPLETE`

---

## 1. Directory Structure

```
research_runs/KAGGLE_PHASE2_V6/
├── project-kira-phase2-mega-notebook.log
└── Project-KIRA/
    ├── output/
    │   └── research_runs/
    │       ├── PHASE1_REAL_WORLD_REPORT.md
    │       ├── RES-C2ST/
    │       │   ├── dataset_manifest.json
    │       │   ├── metrics.json
    │       │   └── status.json
    │       ├── RES-TSTR/
    │       │   ├── dataset_manifest.json
    │       │   ├── metrics.json
    │       │   └── status.json
    │       ├── S-02/
    │       │   ├── dataset_manifest.json
    │       │   ├── metrics.json
    │       │   └── status.json
    │       └── S-05/
    │           ├── graph_manifest.json
    │           ├── leakage_audit.json
    │           └── status.json
    └── research_runs/
        ├── MASTER_COMPARISON.json
        ├── PHASE1_REAL_WORLD_REPORT.md
        ├── WAVE1_REPORT.md
        ├── global_config.json
        ├── PHASE2/
        │   ├── state.json
        │   ├── S00/ (config.json, status.json)
        │   ├── S01/ (config.json, status.json)
        │   ├── A01/ (config.json, metrics.json, provenance.json, status.json)
        │   ├── A02/ (config.json, metrics.json, provenance.json, status.json)
        │   ├── G01/ (config.json, metrics.json, provenance.json, status.json)
        │   ├── G02/ (config.json, metrics.json, provenance.json, status.json)
        │   ├── G03/ (config.json, metrics.json, provenance.json, status.json)
        │   ├── G04/ (config.json, metrics.json, provenance.json, status.json)
        │   ├── G05/ (config.json, metrics.json, provenance.json, status.json)
        │   ├── LLM01/ (status.json)
        │   ├── R01/ (status.json)
        │   └── S04/ (comparison_table.json, evidence_report.md, integrity.json, master_results.json, provenance.json, status.json)
        ├── RES-C2ST/
        ├── RES-L3/
        ├── RES-TSTR/
        ├── S-00/
        ├── S-01/
        ├── S-02/
        └── S-05/
```

---

## 2. Inventory of Primary Artifacts

| Category | Relative Path | Size | Description |
| :--- | :--- | ---: | :--- |
| **Execution Log** | `project-kira-phase2-mega-notebook.log` | 33.5 KB | Raw stream log of V6 execution |
| **Phase 2 Master** | `research_runs/PHASE2/S04/master_results.json` | 5.0 KB | Final reconciled claims registry across all Phase 2 stages |
| **Phase 2 Evidence** | `research_runs/PHASE2/S04/evidence_report.md` | 1.9 KB | Markdown synthesis of Phase 2 experimental results |
| **Phase 2 State** | `research_runs/PHASE2/state.json` | 3.8 KB | Execution status and tracebacks for S00-S04 |
| **G-03 4-Arm Fusion** | `research_runs/PHASE2/G03/metrics.json` | 9.2 KB | Multi-seed 4-arm fusion metrics and bootstrap hypothesis testing |
| **G-01 Standalone GNN** | `research_runs/PHASE2/G01/metrics.json` | 570 B | CausalGraphSAGE diagnostic metrics |
| **A-01 Label-Delay** | `research_runs/PHASE2/A01/metrics.json` | 818 B | Sensitivity under 1d, 3d, 7d, 14d label feedback latency |
| **A-02 Multi-Seed** | `research_runs/PHASE2/A02/metrics.json` | 629 B | 3-seed statistical stability on tiny world |
| **L3 Fidelity** | `output/research_runs/S-02/metrics.json` | 948 B | P1-P4 behavioral fidelity metrics vs Sparkov |
| **C2ST Test** | `output/research_runs/RES-C2ST/metrics.json` | 737 B | Real-vs-synthetic classifier two-sample test (AUC=0.7780) |
| **TSTR Evaluation** | `output/research_runs/RES-TSTR/metrics.json` | 455 B | Train Synthetic Test Real transfer metrics |
| **Graph Leakage** | `output/research_runs/S-05/leakage_audit.json` | 665 B | Zero-day graph temporal leakage audit (0 violations) |
| **Real-World Report**| `output/research_runs/PHASE1_REAL_WORLD_REPORT.md`| 1.8 KB | Consolidated Sparkov benchmark comparison report |
