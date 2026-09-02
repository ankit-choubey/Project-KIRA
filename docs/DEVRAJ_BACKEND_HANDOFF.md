# Project KIRA — Backend API Integration Guide for Devraj

**Date:** 2026-09-02  
**Target:** Devraj (Frontend Lead)  
**Backend Status:** Fully operational, tested, and ready for Netlify integration  

---

## 1. Quick Integration Summary

Devraj, **you do NOT need to modify your UI, redesign components, or rewrite any page logic.**

To connect your Netlify frontend to the live FastAPI backend:

1. In your Netlify dashboard (**Site configuration → Environment variables**), set:
   ```ini
   VITE_API_BASE=https://project-kira-api.onrender.com
   VITE_DATA_MODE=live
   ```
2. Trigger a deploy on Netlify.
3. Your UI will automatically communicate with the live Render backend with full CORS support!

---

## 2. API Endpoints Reference

All endpoints return standard JSON and support cross-origin requests (`CORS`).

### 🩺 System & Configuration
* `GET /api/health` — Returns runtime status, active run ID, and artifact status.
* `GET /api/config` — Returns attack families, hidden zero-day families, and query budgets.
* `GET /api/runs` — Returns list of evaluated runs.

### ⚡ Live Simulation Engine
* `POST /api/simulation/start` — Start a live simulation job:
  ```json
  // Request Body (Optional)
  { "total_swarms": 15000, "batch_size": 50, "speed_multiplier": 1.0 }
  ```
* `GET /api/simulation/latest` — Get live progress, detections, evasions, and current round.
* `GET /api/simulation/{job_id}` — Get specific simulation status.
* `GET /api/simulation/{job_id}/events?limit=50` — Stream latest real-time transaction events.
* `POST /api/simulation/{job_id}/stop` — Stop ongoing simulation.
* `GET /api/simulation/swarm/{swarm_id}` — Inspect individual swarm entity (e.g. `SWARM-000042`).

### 🎯 Live Scoring & Attacks
* `POST /api/score` — Score a live transaction against the model:
  ```json
  { "transaction": { "txn_id": "tx_00000000", "amount": 84.50, ... } }
  ```
* `POST /api/attack` — Run/replay a constrained adversarial Red attack:
  ```json
  { "family": "burst_drain", "budget": 20, "mutation_strength": 0.3, "seed": 20260827 }
  ```

### 📊 Verified Evidence & Artifacts
* `GET /api/stream?offset=0&limit=100` — Paginated transaction stream with Blue decisions.
* `GET /api/transaction/{txn_id}` — Inspect detailed feature breakdown of a transaction.
* `GET /api/coevolution` — Multi-round co-evolution results and per-family ASR metrics.
* `GET /api/evidence` — Full multi-layer evaluation result (L1-L5 fidelity, metrics, manifest).
* `GET /api/artifacts` — List of all 22 available JSON artifacts.
* `GET /api/artifact/{name}` — Raw JSON content of any artifact (e.g. `scoreboard`, `weakness_profile`).

---

## 3. Local Development

To test locally with the backend running on port 8000:

```bash
# Terminal 1: Backend
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

Vite proxies `/api` requests to `http://localhost:8000` automatically.
