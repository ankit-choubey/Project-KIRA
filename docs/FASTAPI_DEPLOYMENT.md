# Project KIRA — FastAPI Backend Deployment Guide

**Target Application:** Mastercard AI Defense Lab (Project KIRA) API  
**Runtime:** Python 3.11 / FastAPI / Uvicorn  
**Authoritative Baseline:** `run_tiny_s20260827_193f7897_40997ab`  

---

## 1. Quick Deploy Overview

The KIRA FastAPI backend is designed for zero-compute, high-throughput evidence and transaction serving. It can be deployed on any free or container hosting platform (Render, Railway, Fly.io, Koyeb, or a cloud VM) independently of the Netlify frontend.

```text
Build Command: pip install -e .
Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

---

## 2. Environment Variables

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `PORT` | Optional | `8000` | Port for Uvicorn web server |
| `CORS_ORIGINS` | Optional | `*` | Comma-separated allowed frontend origins (e.g. `https://your-app.netlify.app,http://localhost:5173`) |
| `MCDL_SCALE` | Optional | `tiny` | Scale mode (`tiny`, `small`, `full`) |
| `PYTHONUNBUFFERED` | Optional | `1` | Stream logging output directly to stdout |

---

## 3. Step-by-Step Deployment (Render Free Web Service)

Render provides free Web Services for Python/Docker applications:

1. **Log in to Render** ([render.com](https://render.com)) and click **New + → Web Service**.
2. **Connect Repository:** Select `ankit-choubey/Project-KIRA`.
3. **Configure Service:**
   * **Name:** `project-kira-api`
   * **Environment:** `Python 3`
   * **Region:** Oregon (US West) or Frankfurt (EU)
   * **Branch:** `main`
   * **Build Command:** `pip install -e .`
   * **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   * **Plan:** Free
4. **Environment Variables:**
   * `CORS_ORIGINS` = `*` (or your Netlify URL: `https://<your-site>.netlify.app`)
5. **Click "Create Web Service"**.
6. Once deployed, Render provides a public HTTPS URL: `https://project-kira-api.onrender.com`.

---

## 4. Operational Behavior & Free Tier Considerations

1. **Cold Start Behavior:**
   * Free-tier web services on Render / Railway idle after 15 minutes of inactivity.
   * Cold start takes ~15–30 seconds on initial wake-up.
   * `GET /api/health` will return `200 OK` as soon as the service wakes up.
2. **Storage Assumptions:**
   * Read-only artifact access: reads from `artifacts/run_tiny_s20260827_193f7897_40997ab/`.
   * In-memory simulation: `api/simulation.py` maintains an active ring buffer of the latest 500 events without disk writes.
3. **Timeout Considerations:**
   * Decision latency: P95 is ~1.18ms in-process. All REST queries complete within <50ms.

---

## 5. Verifying the Deployment

Run the following smoke tests against your deployed HTTPS URL:

```bash
# 1. Health check
curl -s https://<YOUR_DEPLOYED_URL>/api/health

# 2. Config & Families
curl -s https://<YOUR_DEPLOYED_URL>/api/config

# 3. Live Simulation Trigger
curl -s -X POST https://<YOUR_DEPLOYED_URL>/api/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"total_swarms": 15000, "batch_size": 50}'

# 4. Stream Sample
curl -s "https://<YOUR_DEPLOYED_URL>/api/stream?offset=0&limit=10"
```
