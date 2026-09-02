# Project KIRA — Comprehensive Deployment & Architecture Audit

**Document Version:** 1.0.0  
**Audit Date:** 2026-09-02  
**Audited Target:** `ankit-choubey/Project-KIRA`  
**Auditor:** KIRA Core Engineering  

---

## 1. Executive Summary

This audit establishes the baseline repository state before final deployment hardening. It evaluates the separation of concerns across the **Netlify Frontend (Devraj)**, the **FastAPI Gateway (Ankit)**, the **Frozen Research Baseline**, and the **Hugging Face / Kaggle Infrastructure**.

### Key Architectural Verifications:
1. **Frontend Isolation (Netlify):** Devraj's React 18 + Vite presentation UI is strictly preserved. All visual layouts, routing, 11 research sections, and interaction designs remain 100% intact.
2. **Backend API Readiness:** FastAPI backend (`api/main.py`) provides artifact-backed evidence serving, on-demand attack replays, and transaction scoring. A live simulation engine is designed to supply truthful, real-time transaction event streams.
3. **Research Immutability:** The authoritative baseline (`artifacts/run_tiny_s20260827_193f7897_40997ab`) passes 22/22 SHA-256 cryptographic verification. Core ML code (`src/mcdl/blue/`, `src/mcdl/red/`, `src/mcdl/features/`, `src/mcdl/research/`) is completely frozen.
4. **Hugging Face Decoupling:** Hugging Face Space is configured as an optional static showcase/documentation target and is completely decoupled from Netlify. Netlify communicates directly with the FastAPI backend via HTTPS.

---

## 2. Repository & Branch State

* **Active Branch:** `main`
* **Head Commit:** `b0a6250` (`docs(script): update presentation script with live free HF static space URL`)
* **Remote Sync:** Clean sync with `origin/main` (GitHub) and `space-free/main` (HF Static Space)
* **Authoritative Artifact Pointer:** `artifacts/LATEST` points to `run_tiny_s20260827_193f7897_40997ab`
* **Dependency Management:** `pyproject.toml` (FastAPI, Polars, LightGBM, Pydantic v2) + `package.json` (React 18, Vite 5, TypeScript 5)

---

## 3. Frontend Architecture & Netlify Configuration

* **Source Directory:** `frontend/`
* **Entrypoints:** `frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/App.tsx`
* **Build System:** Vite 5 (`frontend/vite.config.ts`) outputting to `frontend/dist/`
* **Environment Variables:**
  - `VITE_DATA_MODE`: `"live"` (default for Netlify connecting to FastAPI) or `"static"`
  - `VITE_API_BASE`: Configurable backend origin (e.g. `https://<fastapi-host>`)
* **11 Structured Sections:**
  1. `MissionControl.tsx` (01 Mission)
  2. `ClosedLoopSimulation.tsx` (02 See KIRA Think / Closed Loop / 15K Swarm)
  3. `TheLoop.tsx` (03 The Loop)
  4. `GraphFusion.tsx` (04 Graph Fusion)
  5. `AttackConsole.tsx` (05 Attack Engine)
  6. `WeaknessBoard.tsx` (06 Weaknesses)
  7. `ThreeWorlds.tsx` (07 Three Worlds)
  8. `RealWorldValidation.tsx` (08 Real-World & Invariance)
  9. `ExperimentRegister.tsx` (09 Experiments)
  10. `TransactionMonitor.tsx` (10 Monitor)
  11. `EvidenceProvenance.tsx` (11 Evidence)

---

## 4. FastAPI Backend Endpoints Inventory

| Method | Endpoint | Source Mode | Semantic Category | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api` / `/api/` | Live Gateway | `LIVE` | Root API directory and service metadata |
| `GET` | `/api/health` | Live Gateway | `LIVE` | Operational status, active run, commit hash |
| `GET` | `/api/config` | Artifact / Live | `VERIFIED EXPERIMENT` | Attack families, hidden zero-day families, budgets |
| `GET` | `/api/runs` | Artifact Store | `VERIFIED EXPERIMENT` | Available evaluated experiment runs |
| `GET` | `/api/stream` | Artifact Store | `VERIFIED EXPERIMENT` | Paginated transaction stream with decision labels |
| `GET` | `/api/transaction/{txn_id}` | Artifact Store | `VERIFIED EXPERIMENT` | Transaction feature inspection & decision breakdown |
| `POST`| `/api/score` | Model / Artifact | `LIVE` / `ARTIFACT_BACKED` | On-demand transaction risk scoring |
| `POST`| `/api/attack` | Mutator / Artifact| `LIVE` / `ARTIFACT_REPLAY` | Constrained Red mutation search replay |
| `GET` | `/api/coevolution` | Artifact Store | `VERIFIED EXPERIMENT` | Multi-round co-evolution metrics & family breakdown |
| `GET` | `/api/evidence` | Artifact Store | `VERIFIED EXPERIMENT` | Full multi-layer evaluation result |
| `GET` | `/api/artifacts` | Artifact Store | `VERIFIED EXPERIMENT` | Inventory of available JSON artifact files |
| `GET` | `/api/artifact/{name}` | Artifact Store | `VERIFIED EXPERIMENT` | Direct raw JSON payload of specified artifact |

---

## 5. Kaggle Research Notebooks Inventory

| Notebook File | Purpose | Scale / Target | Expected Runtime | Output Artifacts |
| :--- | :--- | :--- | :--- | :--- |
| `notebooks/kaggle/02_full_run.ipynb` | Full end-to-end Block 6 research run | Full synthetic world | ~115 min CPU | `evaluation.json`, `manifest.json`, `decisions.json` |
| `notebooks/kaggle/03_real_world_validation.ipynb` | Sparkov transfer, C2ST fidelity, temporal graph invariance | 50,000 real transactions | ~25 min CPU | `fidelity_report.json`, `tstr_metrics.json`, `leakage_report.json` |
| `notebooks/kaggle/04_phase2_mega_notebook.ipynb` | S-00 to S-04 Graph-Tabular Fusion | 47,501 synthetic transactions | ~8.5 min CPU | `master_results.json`, `comparison_table.json`, `S02/metrics.json` |
| `notebooks/kaggle/05_adv002_large_swarm.ipynb` | ADV-002 15,000 stateful adversarial swarm | 15,000 attack entities | ~18 min CPU | `adv002_swarm_telemetry.json`, `population_matrix.json` |
| `notebooks/kaggle/06_adv003_adaptive_defense.ipynb` | ADV-003 Adaptive Challenger Hardening | Multi-round co-evolution | ~12 min CPU | `adaptive_metrics.json`, `retention_matrix.json` |

---

## 6. Audit Conclusion & Protection Sign-Off

* **Netlify Frontend:** 100% Protected. Zero UI modifications required.
* **FastAPI Backend:** Fully capable of supporting Netlify cross-origin requests with CORS.
* **Truthfulness Contract:** Explicit semantic labels (`LIVE`, `VERIFIED EXPERIMENT`, `REPRODUCIBLE`, `NOT MEASURED`) enforced across all endpoints.
