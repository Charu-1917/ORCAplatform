# ORCA Backend (FastAPI + Ollama)

One server on port **8000** serves both the ORCA frontend (`../frontend`) and the API.
The chat answer is written by a **local Ollama model** (no cloud key needed).

## 1. One-time setup

1. Install Python 3.10+ and Ollama (https://ollama.com/download).
2. Pull a model (pick one):
   ```
   ollama pull gemma3:4b      # default - better Tamil
   ollama pull llama3.2:3b    # lighter / faster alternative
   ```
   If the configured model is not pulled, the backend automatically uses the first
   pulled model from `OLLAMA_FALLBACK_MODELS` (see `.env.example`).
3. Install backend packages:
   ```
   cd ocra-platform/backend
   python -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   ```
   `requirements-scidl.txt` (torch, earth2studio, copernicusmarine...) is optional and heavy;
   without it the SciDL engines use their built-in fallback engines.

## 2. Run

Double-click `start-orca.bat`, or:
```
.venv\Scripts\python run.py
```
It prints the URLs to open:

| Where | URL |
|---|---|
| This PC | http://localhost:8000 |
| Other PCs / phone on the same Wi-Fi | http://<this-PC-IP>:8000 (printed at startup) |
| API docs | http://localhost:8000/docs |

### Other PCs / phone on the same network
Windows Firewall blocks incoming connections by default. Run once as Administrator:
```
powershell -ExecutionPolicy Bypass -File allow-firewall.ps1
```

### Phone over USB (port forwarding, no Wi-Fi needed)
Android, USB debugging on, then on the PC:
```
adb reverse tcp:8000 tcp:8000
```
Open http://localhost:8000 in the phone browser.

### From anywhere (outside your network)
Use a tunnel such as Tailscale, `ngrok http 8000` or `cloudflared tunnel --url http://localhost:8000`.

## Public link on Render (AI runs on this PC)

Render hosts the website + API 24/7 (free plan, `render.yaml` at the repo root). Render has no GPU and
512 MB RAM, so the model stays on this PC: Render calls this PC's ORCA **gateway** (`/gateway/*`),
which forwards only model listing, chat and warm-up to the local Ollama and requires a secret key.
Ollama itself is never exposed.

1. **PC:** `ocra-platform/backend/.env` contains `ORCA_GATEWAY_KEY=...` (random secret, never committed).
   Start ORCA with `start-orca.bat`.
2. **PC:** give the PC a fixed public address with ngrok's free static domain:
   ```
   ngrok config add-authtoken <your-token>
   ngrok http --url=<your-static-domain>.ngrok-free.app 8000
   ```
3. **Render:** New → Blueprint → pick this repo/branch. Set the two secret variables:
   - `OLLAMA_BASE_URL` = `https://<your-static-domain>.ngrok-free.app/gateway`
   - `OLLAMA_API_KEY` = the same value as `ORCA_GATEWAY_KEY` in the PC's `.env`
4. Open `https://<service>.onrender.com`. `GET /api/llm/status` shows `"online": true` when the PC is reachable.

If the PC or tunnel is off, the site still works; chat replies show the raw live agent data and say the model is offline.
Free Render services sleep after 15 min without visitors (first visit then takes ~1 min).

## API used by the frontend

| Method | Path | Used by |
|---|---|---|
| POST | `/api/chat` | chat box (`message, session_id, lat, lon, language`) |
| POST | `/predict` | Ocean Map drawer (`lat, lon, forecast_hours, model_name`) |
| POST | `/api/finetune/start` | Fine-Tuning modal (`base_model_name, epochs`) |

| GET | `/api/alerts` | 🔔 Alerts panel + pop-ups: live sea alerts for 17 coastal points (Open-Meteo, cached 10 min) |
| GET | `/api/news?lang=en\|ta` | 📰 Marine News tab + pop-ups: Google News RSS headlines (cached 30 min, duplicates merged) |

| POST | `/api/tts` | 🎙️ Voice assistant: speaks ORCA's answer (MP3) in en/ta/hi/te/ml/kn/gu/mr/bn via online neural voices (`edge-tts`, needs internet) |

**Voice assistant:** tap *Voice Mode*, talk, ORCA answers aloud in the chosen language and listens again.
Speech recognition runs in the browser (Chrome/Edge) and needs a secure page: `http://localhost:8000`
on this PC, or `adb reverse tcp:8000 tcp:8000` / an HTTPS tunnel on a phone.

Chat history is stored in each browser (localStorage), so it stays private per device.

Extra: `GET /api/health`, `GET /api/llm/status`, `GET /api/models`, `POST /api/predict/batch`,
`GET /api/finetune/status`, `POST /api/data/download`.

## How a chat answer is made
1. Weather (Open-Meteo, live), Satellite (INCOIS ERDDAP, live) and SciDL agents run in parallel.
2. Routing and Safety agents add route / emergency flags.
3. Ollama writes the reply in the requested language (`auto` detects Tamil/Telugu/Malayalam/Gujarati script).
4. If Ollama is not running, the reply shows the raw agent data instead and says the model is offline.

## Tests
```
.venv\Scripts\python -m pytest tests
```
