# ORCA — Oceanic Reasoning & Collaborative Agents

A full-stack prototype built for the ISRO Smart India Hackathon problem statement on
AI-driven marine advisory for Indian fishermen — Potential Fishing Zones (PFZ), cyclone
and high-wave safety alerts, and multilingual voice advisories, backed by a simulated
multi-agent orchestrator over mock ISRO Bhuvan / INCOIS-style ocean data.

> All satellite/ocean data in this prototype is **simulated** for demonstration.

## Architecture

```
orca platform/
├── backend/      FastAPI multi-agent orchestrator + mock ISRO/INCOIS datasets
└── frontend/     React + Vite + TypeScript + Tailwind, DeepSeek-style UI
```

### Agents (backend/app/agents)

1. 🧠 **Intent & Multilingual Router Agent** — detects language, coastal location, and intent.
2. 🛰️ **ISRO Satellite & Ocean Data Retrieval Agent** — simulates Oceansat-3 / INCOIS retrieval
   of SST, Chlorophyll-a, current vectors, and PFZ candidates.
3. 🌊 **Spatial-Temporal Reasoning & PFZ Agent** — ranks PFZ zones and computes SST↔Chlorophyll
   correlation over a 7-day window.
4. ⚠️ **Marine Safety & Hazard Advisory Agent** — checks wind/wave/cyclone advisories and
   computes a Green / Yellow / Red alert level.
5. ✨ **Synthesis & Translation Agent** — aggregates everything into markdown + a translated
   spoken advisory for the TTS widget.

## Running locally

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # on Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

### Frontend (Vite + React)

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend reads the backend URL from `VITE_API_URL`
(defaults to `http://localhost:8000`, see `frontend/.env`).

## Key endpoints

| Method | Path             | Description                              |
|--------|------------------|-------------------------------------------|
| GET    | `/health`        | Health check                              |
| GET    | `/api/languages` | Supported languages                       |
| GET    | `/api/locations` | Coastal reference locations               |
| GET    | `/api/hazards`   | Raw mock hazard/advisory database         |
| POST   | `/api/query`     | Runs the full multi-agent pipeline        |

`POST /api/query` body:

```json
{
  "query": "Where is the nearest PFZ in Tamil Nadu today?",
  "language": null,
  "deep_reasoning": true,
  "live_data": false,
  "voice_mode": false
}
```

## Deploying to Render

This repo includes a [`render.yaml`](render.yaml) Blueprint that provisions both services:

- **orca-backend** — Python web service (FastAPI/uvicorn), root dir `backend/`
- **orca-frontend** — Static site (Vite build), root dir `frontend/`

### One-time setup

1. Push this repo to GitHub (already done if you're reading this from the deployed repo).
2. In the Render dashboard: **New +** → **Blueprint** → connect the `ORCAplatform` repo →
   Render detects `render.yaml` and creates both services.
3. Render assigns URLs based on service name: `https://orca-backend.onrender.com` and
   `https://orca-frontend.onrender.com`. The blueprint already wires these into each other via
   `VITE_API_URL` (frontend → backend) and `FRONTEND_URL` (backend CORS allow-list).
   - If either name is already taken on Render, it'll get a random suffix instead
     (e.g. `orca-backend-ab12`). If that happens, update the corresponding env var
     (`VITE_API_URL` on the frontend service, `FRONTEND_URL` on the backend service) in the
     Render dashboard to match the real URL, then manually redeploy both services.
4. Free-tier services spin down after inactivity — the first request after idling can take
   10-30s while the backend cold-starts.

### Manual setup (without the Blueprint)

**Backend** — New Web Service, root directory `backend`, environment `Python 3`:
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Env var: `FRONTEND_URL=https://<your-frontend>.onrender.com`

**Frontend** — New Static Site, root directory `frontend`:
- Build command: `npm install && npm run build`
- Publish directory: `dist`
- Env var: `VITE_API_URL=https://<your-backend>.onrender.com`
- Add a rewrite rule `/*` → `/index.html` (client-side routing fallback)

## Features

- Ethereal glassmorphism UI inspired by DeepSeek's web app, with an animated CSS wave
  background/footer and pill-shaped toggle controls.
- Expandable **Agent Workflow Visualizer** showing per-agent chain-of-thought and timing.
- Leaflet map with PFZ zone circles, a simulated SST heatmap grid, and a safety-boundary ring.
- Recharts dual-axis chart of 7-day SST vs Chlorophyll-a.
- Browser SpeechSynthesis-based text-to-speech for the regional-language advisory
  (English, Hindi, Tamil, Telugu, Malayalam, Bengali, Gujarati, Marathi).
