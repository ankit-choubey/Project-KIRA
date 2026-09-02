# Project KIRA — Final Deployment Architecture & Governance

**Date:** 2026-09-02  
**Status:** `DEPLOYMENT_READY`  
**Authoritative Baseline:** `run_tiny_s20260827_193f7897_40997ab` (SHA-256 Verified 22/22)  

---

## 1. System Topology Overview

```text
                    NETLIFY PRODUCTION FRONTEND
                    Owner: Devraj (PROTECTED)
                              │
                              │ HTTPS API (VITE_API_BASE)
                              ▼
                    ┌─────────────────────┐
                    │   FASTAPI BACKEND   │
                    │   Owner: Ankit      │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼──────────────────┐
             ▼                 ▼                  ▼
       LIVE STREAM        LIVE SCORING       LIVE SIMULATION
       /api/stream        /api/score         /api/simulation/*
             │                 │                  │
             └─────────────────┼──────────────────┘
                               │
                               ▼
                       KIRA ENGINE / RUNNER
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
          LIGHTWEIGHT LIVE             HEAVY RESEARCH
         SHOWCASE EXECUTION              EXECUTION
                │                             │
                ▼                             ▼
          REAL TRANSACTIONS             KAGGLE CPU
          RED ATTACK REPLAYS                  │
                │                             ▼
                └──────────────┬──────────────┘
                               ▼
                     VERIFIED ARTIFACTS
                     (artifacts/run_tiny_*)
                               │
                               ▼
                    EVIDENCE & CLAIMS AUDIT
```

---

## 2. Component Ownership & Protection Boundaries

| Component | Target Platform | Lead Owner | Protection Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Presentation Client** | Netlify | Devraj | **PROTECTED (Unchanged)** | React 18 + Vite research UI with 11 structured sections |
| **API Gateway** | FastAPI (Render / VPS) | Ankit | **DEPLOYABLE** | High-throughput evidence server, live simulation runner, and score API |
| **Heavy Computation** | Kaggle CPU | Ankit | **IMMUTABLE EVIDENCE** | Reproducible research notebooks (Phase 2 Mega Notebook, ADV Swarms) |
| **Static Evidence Space** | Hugging Face Static | System | **OPTIONAL SHOWCASE** | Zero-cost static evidence and documentation mirror |

---

## 3. Data Classification & Labeling Standard

Every piece of data exposed across the Netlify UI and FastAPI endpoints adheres strictly to one of the following truthful classifications:

1. **`LIVE`**: Active execution originating from the live Python/FastAPI runner (e.g. active simulation progress, real-time transaction scoring latency, live attack mutation).
2. **`VERIFIED EXPERIMENT`**: Frozen empirical results backed by on-disk JSON artifacts with SHA-256 cryptographic hashes (e.g. baseline PR-AUC 0.9375, 4/4 challenger overfit rejection, EXP-007-A budget curve).
3. **`EXTERNAL ANCHOR`**: Independent real-world benchmark validation (e.g. ULB CC0 credit card fraud benchmark PR-AUC = 0.8640).
4. **`REPRODUCIBLE`**: Previously executed heavy research that can be regenerated on Kaggle CPU using verified notebook scripts.
5. **`NOT MEASURED`**: Metrics unmeasured in a specific run (e.g. zero-evasion challenger MED, uncomputed graph motifs). Rendered as `null`, **never coerced to zero**.

---

## 4. Resilience & Decoupling Guarantees

* **Hugging Face Independence:** Netlify communicates directly with FastAPI. If Hugging Face is paused or down, the Netlify frontend continues operating with 100% functionality.
* **Backend Fallback:** If the FastAPI backend is undergoing a cold restart, the Netlify frontend gracefully uses its built-in static artifact adapter to display verified evidence without crashing or showing blank screens.
