# Project KIRA — Complete Render Free FastAPI Deployment Guide

**Target Service:** `project-kira-api`  
**Host Platform:** Render (Free Web Service)  
**FastAPI Application Path:** `api.main:app`  
**Authoritative Baseline:** `run_tiny_s20260827_193f7897_40997ab` (SHA-256 Verified 22/22)  

---

## 1. Architecture Topology

```text
               EXISTING NETLIFY FRONTEND (DEVRAJ)
                     [PROTECTED - UNCHANGED]
                                │
                                │ HTTPS Requests
                                ▼
               ┌─────────────────────────────────┐
               │    RENDER FREE WEB SERVICE      │
               │   https://<app>.onrender.com    │
               │   FastAPI Gateway (api.main:app)│
               └────────────────┬────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
   LIVE SIMULATION         LIVE SCORING            LIVE ATTACKS
   /api/simulation/*       /api/score              /api/attack
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
                       VERIFIED ARTIFACTS
                 (artifacts/run_tiny_s20260827_...)
```

---

## 2. 1-Click Render Blueprint Deployment (`render.yaml`)

The repository includes a root [`render.yaml`](file:///Users/theankit/Documents/AK/Projects/Project-KIRA/render.yaml) blueprint:

```yaml
services:
  - type: web
    name: project-kira-api
    runtime: python
    plan: free
    region: oregon
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /api/health
    envVars:
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: CORS_ORIGINS
        value: "*"
      - key: MCDL_SCALE
        value: "tiny"
```

### Deploying via Render Dashboard:
1. Log into [dashboard.render.com](https://dashboard.render.com).
2. Click **New + → Blueprint** (or **New + → Web Service**).
3. Connect repository: **`ankit-choubey/Project-KIRA`**.
4. Select branch: **`main`**.
5. Render detects `render.yaml` automatically and configures:
   * **Name:** `project-kira-api`
   * **Runtime:** `Python`
   * **Plan:** `Free` ($0.00 / mo)
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   * **Health Check Path:** `/api/health`
6. Click **Apply** or **Create Web Service**.

---

## 3. Environment Variables Configuration

| Variable | Value | Description |
| :--- | :--- | :--- |
| `PYTHONUNBUFFERED` | `1` | Stream python logs directly to Render console |
| `CORS_ORIGINS` | `*` or `https://<your-netlify-site>.netlify.app` | Allows cross-origin requests from Devraj's Netlify frontend |
| `MCDL_SCALE` | `tiny` | Lightweight serving mode |

---

## 4. Connecting Netlify to Render

Once Render assigns your public URL (e.g., `https://project-kira-api.onrender.com`):

1. Go to your **Netlify Dashboard** → Select the KIRA site.
2. Navigate to **Site configuration → Environment variables**.
3. Set:
   ```ini
   VITE_API_BASE=https://project-kira-api.onrender.com
   VITE_DATA_MODE=live
   ```
4. Trigger a new deploy on Netlify.
5. Devraj's frontend immediately communicates with the Render FastAPI backend with zero UI changes!

---

## 5. Free-Tier Behavior & Cold Starts

* **Inactivity Sleep:** Render free web services spin down after 15 minutes of inactivity.
* **Wake-Up Time:** Cold start takes ~20–30 seconds upon the first incoming request.
* **Resilience:** If Render is waking up, the frontend displays its non-blocking loading state or uses baked artifact fallbacks.
* **Cost:** Guaranteed $0.00 / month forever.

---

## 6. Automated Post-Deploy Smoke Test

Execute this curl sequence to verify your live Render deployment:

```bash
# Set your assigned Render URL
RENDER_URL="https://project-kira-api.onrender.com"

# 1. Health check (returns 200 OK)
curl -s "$RENDER_URL/api/health"

# 2. Interactive Swagger Docs
curl -s -o /dev/null -w "%{http_code}\n" "$RENDER_URL/docs"

# 3. Start Live Simulation
curl -s -X POST "$RENDER_URL/api/simulation/start" \
  -H "Content-Type: application/json" \
  -d '{"total_swarms": 15000, "batch_size": 50, "speed_multiplier": 1.0}'

# 4. Score Transaction
curl -s -X POST "$RENDER_URL/api/score" \
  -H "Content-Type: application/json" \
  -d '{"transaction": {"txn_id": "tx_00000000", "amount": 54.20, "channel": "card_present", ...}}'
```
