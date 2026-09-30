# app/main.py
import re
import hmac
import uuid
import asyncio
import logging

import httpx
from collections import OrderedDict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.schemas import (
    ChatRequest, ChatResponse, PredictRequest, PredictResponse,
    ModelListResponse, FineTuneRequest, FineTuneStatusResponse, DatasetDownloadRequest,
    BatchPredictRequest, BatchPredictResponse
)
from app.prompts import build_agent_context, build_chat_messages
from app.services.llm import ollama_client, OllamaUnavailable
from app.services.voice import synthesize
from app.services.marine.sea_alerts import get_sea_alerts, find_place_in_text, nearest_alert_point
from app.services.marine.marine_news import get_marine_news
from app.agents.satellite import run_satellite_agent
from app.agents.weather import run_weather_agent
from app.agents.routing import run_routing_agent
from app.agents.safety import run_safety_agent
from app.agents.scidl import run_scidl_agent
from app.services.scidl.model_registry import scidl_registry
from app.services.scidl.finetune_engine import finetune_engine
from app.services.scidl.data_downloader import data_downloader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("orca.api")

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

app = FastAPI(
    title="ORCA Marine Engine & SciDL Predictor",
    version="1.0.0",
    description="Production Scientific Deep Learning (SciDL) API serving SFNO, FourCastNet v3, GraphCast, Aurora, and PINN model inference & fine-tuning."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def no_stale_frontend(request, call_next):
    # Browsers must re-check index.html / app.js / css after an update, so phones
    # and other PCs never keep running an old copy of the frontend.
    response = await call_next(request)
    if not request.url.path.startswith(("/api", "/predict", "/docs", "/openapi", "/gateway", "/healthz")):
        response.headers["Cache-Control"] = "no-cache"
    return response

@app.on_event("startup")
async def warmup_llm():
    asyncio.create_task(ollama_client.warmup())

# session_id -> list of {"user", "bot"} turns; oldest sessions evicted past MAX_SESSIONS
SESSION_STORE: "OrderedDict[str, list]" = OrderedDict()

@app.get("/api/health")
async def health():
    return {
        "status": "ORCA Backend Active",
        "scidl_engine": "NVIDIA Earth2Studio / SciDL Operational",
        "llm": await ollama_client.status(),
    }

@app.get("/healthz")
def healthz():
    """Lightweight liveness check for hosting platforms (Render)."""
    return {"status": "ok"}

# --------------------------------------------------------------------------
# Ollama gateway: lets a remote ORCA (e.g. on Render) use THIS PC's Ollama.
# Only enabled when ORCA_GATEWAY_KEY is set, requires that key, and only
# forwards model listing, chat and warm-up. Ollama itself is never exposed.
# --------------------------------------------------------------------------
GATEWAY_MAX_MESSAGES = 40
GATEWAY_MAX_CHARS = 30000

def _check_gateway_key(request: Request):
    key = settings.ORCA_GATEWAY_KEY
    if not key:
        raise HTTPException(status_code=404, detail="Not Found")
    auth = request.headers.get("authorization", "")
    if not hmac.compare_digest(auth.encode(), f"Bearer {key}".encode()):
        raise HTTPException(status_code=401, detail="Invalid gateway key")

async def _forward_to_ollama(method: str, path: str, payload: dict = None, timeout: float = 10.0):
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=5.0)) as client:
            resp = await client.request(method, f"{settings.OLLAMA_BASE_URL.rstrip('/')}{path}", json=payload)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Local Ollama unreachable: {exc}")
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")

@app.get("/gateway/api/tags")
async def gateway_tags(request: Request):
    _check_gateway_key(request)
    return await _forward_to_ollama("GET", "/api/tags")

@app.post("/gateway/api/chat")
async def gateway_chat(request: Request):
    _check_gateway_key(request)
    body = await request.json()
    messages = body.get("messages") or []
    if (not isinstance(messages, list) or len(messages) > GATEWAY_MAX_MESSAGES
            or sum(len(str(m.get("content", ""))) for m in messages) > GATEWAY_MAX_CHARS):
        raise HTTPException(status_code=413, detail="Chat request too large")
    payload = {
        "model": body.get("model"),
        "messages": [{"role": m.get("role"), "content": m.get("content")} for m in messages],
        "stream": False,
        "keep_alive": body.get("keep_alive", settings.OLLAMA_KEEP_ALIVE),
        "options": body.get("options") or {},
    }
    return await _forward_to_ollama("POST", "/api/chat", payload, timeout=settings.OLLAMA_TIMEOUT)

@app.post("/gateway/api/generate")
async def gateway_warmup(request: Request):
    _check_gateway_key(request)
    body = await request.json()
    # Warm-up only: load the model, never run arbitrary prompts
    payload = {"model": body.get("model"), "keep_alive": body.get("keep_alive", settings.OLLAMA_KEEP_ALIVE)}
    return await _forward_to_ollama("POST", "/api/generate", payload, timeout=settings.OLLAMA_TIMEOUT)

@app.get("/api/alerts")
def sea_alerts_endpoint():
    """Live coastal sea-state alerts (Open-Meteo forecast, refreshed every 10 min)."""
    return get_sea_alerts()

@app.get("/api/news")
def marine_news_endpoint(lang: str = "en"):
    """Recent marine / fishermen / cyclone news headlines (Google News RSS, refreshed every 30 min)."""
    return get_marine_news(lang)

class TTSRequest(BaseModel):
    text: str
    lang: str = "en"

@app.post("/api/tts")
async def tts_endpoint(payload: TTSRequest):
    """Speaks ORCA's answer in the user's language (MP3). Used by the voice assistant."""
    try:
        audio = await synthesize(payload.text, payload.lang)
    except Exception as exc:
        logger.warning(f"TTS failed ({payload.lang}): {exc}")
        raise HTTPException(status_code=503, detail=f"Speech service unavailable: {exc}")
    return Response(content=audio, media_type="audio/mpeg", headers={"Cache-Control": "no-store"})

@app.get("/api/llm/status")
async def llm_status():
    """Reports whether the local Ollama server is reachable and which model ORCA is using."""
    return await ollama_client.status()

@app.get("/api/models", response_model=ModelListResponse)
def get_available_models():
    """
    List primary deep learning models for oceanography and weather forecasting.
    Includes SFNO, FourCastNet v3, GraphCast, Microsoft Aurora, Swin-UNet, and PINNs.
    """
    return scidl_registry.list_models()

@app.post("/predict", response_model=PredictResponse)
@app.post("/api/predict", response_model=PredictResponse)
def predict_endpoint(payload: PredictRequest):
    """
    Core Deep Learning Scientific Prediction Endpoint (POST /predict).
    Executes live or tensor-based SFNO, FourCastNet v3, GraphCast, Aurora, or PINN inference.
    """
    res = scidl_registry.predict(
        lat=payload.lat,
        lon=payload.lon,
        forecast_hours=payload.forecast_hours,
        variables=payload.variables,
        model_name=payload.model_name or "SFNO",
        data_source=payload.data_source or "GFS",
        timestamp=payload.time or "latest"
    )
    return PredictResponse(**res)

@app.post("/api/predict/batch", response_model=BatchPredictResponse)
def predict_batch_endpoint(payload: BatchPredictRequest):
    """
    Batch Scientific Prediction Endpoint (POST /api/predict/batch).
    Executes deep learning inference across multiple lat/lon trajectory points in a single request.
    """
    model_name = payload.model_name or "SFNO"
    results = []
    for pt in payload.points:
        res = scidl_registry.predict(
            lat=pt.lat,
            lon=pt.lon,
            forecast_hours=payload.forecast_hours,
            variables=payload.variables,
            model_name=model_name
        )
        results.append(PredictResponse(**res))

    return BatchPredictResponse(
        status="success",
        model_name=model_name,
        total_points=len(results),
        results=results
    )

@app.post("/api/finetune/start", response_model=FineTuneStatusResponse)
def start_finetuning_endpoint(payload: FineTuneRequest):
    """
    Triggers regional fine-tuning loop on pre-trained surrogate models.
    Freezes backbone layers and retrains predictor-corrector output layers with FP16 AMP.
    """
    res = finetune_engine.run_fine_tuning(
        base_model_name=payload.base_model_name or "SFNO",
        dataset_path=payload.dataset_path or "data/indian_ocean_training.nc",
        epochs=payload.epochs,
        learning_rate=payload.learning_rate,
        batch_size=payload.batch_size,
        use_amp=payload.use_amp
    )
    return FineTuneStatusResponse(**res)

@app.get("/api/finetune/status", response_model=FineTuneStatusResponse)
def get_finetuning_status_endpoint():
    """
    Gets active fine-tuning job metrics, epoch progress, and loss history.
    """
    status = finetune_engine.get_status()
    return FineTuneStatusResponse(**status)

@app.post("/api/data/download")
def download_dataset_endpoint(payload: DatasetDownloadRequest):
    """
    Downloads regional Copernicus Marine NetCDF slice, ARGO Float profiles, or synthetic Indian Ocean slice.
    """
    source_upper = (payload.source or "COPERNICUS").upper()
    if source_upper == "ARGO":
        return data_downloader.fetch_argo_profiles(
            bbox=[payload.min_lon, payload.max_lon, payload.min_lat, payload.max_lat]
        )
    elif source_upper == "SYNTHETIC":
        return data_downloader.create_synthetic_netcdf()
    else:
        return data_downloader.fetch_copernicus_subset(
            dataset_id=payload.dataset_id or "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
            variables=payload.variables or ["thetao", "so", "uo", "vo"],
            min_lon=payload.min_lon,
            max_lon=payload.max_lon,
            min_lat=payload.min_lat,
            max_lat=payload.max_lat
        )


SCRIPT_LANGUAGES = [
    ("ta", re.compile(r"[஀-௿]")),  # Tamil
    ("te", re.compile(r"[ఀ-౿]")),  # Telugu
    ("ml", re.compile(r"[ഀ-ൿ]")),  # Malayalam
    ("gu", re.compile(r"[઀-૿]")),  # Gujarati
    ("kn", re.compile(r"[ಀ-೿]")),  # Kannada
    ("bn", re.compile(r"[ঀ-৿]")),  # Bengali
    ("hi", re.compile(r"[ऀ-ॿ]")),  # Devanagari -> Hindi (pick Marathi explicitly in the language menu)
]

def resolve_language(requested: str, message: str) -> str:
    """Frontend sends 'auto', 'en' or 'ta'; 'auto' is resolved from the message script."""
    requested = (requested or "auto").lower().strip()
    if requested != "auto":
        return requested
    for code, pattern in SCRIPT_LANGUAGES:
        if pattern.search(message):
            return code
    return "en"

def build_offline_reply(lang: str, has_warning: bool, warning_text: str, weather_res: dict,
                        sat_res: dict, scidl_res: dict, routing_res: dict) -> str:
    """Honest reply used when the Ollama model is not reachable: raw agent data, no invented numbers."""
    lines = []
    if has_warning:
        lines.append(f"EMERGENCY WARNING: {warning_text or 'High risk weather detected.'} "
                     "Return to harbor / seek shelter immediately. Coast Guard: 1554.")
    if lang == "ta":
        lines.append("ORCA மொழி மாதிரி (Ollama) தற்போது இயங்கவில்லை. கீழே நேரடி முகவர் தரவு உள்ளது:")
    else:
        lines.append("ORCA's language model (Ollama) is offline right now. Here is the raw agent data:")
    lines.append(f"- Weather: {weather_res['info']}")
    lines.append(f"- Satellite: {sat_res['info']}")
    lines.append(f"- SciDL estimate: {scidl_res['info']}")
    lines.append(f"- Route: {routing_res['info'].strip()}")
    return "\n".join(lines)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    session_id = payload.session_id or str(uuid.uuid4())

    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = []
        while len(SESSION_STORE) > settings.MAX_SESSIONS:
            SESSION_STORE.popitem(last=False)
    SESSION_STORE.move_to_end(session_id)

    # A coastal place named in the message ("near Kanyakumari") overrides the
    # location pill, so the answer uses that place's data, not Chennai's.
    lat, lon, location_name = payload.lat, payload.lon, None
    named_place = find_place_in_text(payload.message)
    if named_place:
        lat, lon = named_place["lat"], named_place["lon"]
        location_name = f"{named_place['name']}, {named_place['state']}"

    # Network-bound agents run concurrently in worker threads so one user's
    # slow INCOIS / Open-Meteo call never blocks other users of the server.
    sat_res, weather_res, scidl_res, alert_point = await asyncio.gather(
        asyncio.to_thread(run_satellite_agent, lat, lon),
        asyncio.to_thread(run_weather_agent, lat, lon),
        asyncio.to_thread(run_scidl_agent, lat, lon),
        asyncio.to_thread(nearest_alert_point, lat, lon),
    )
    # Same live forecast the Alerts panel shows, so chat and alerts never disagree
    alert_info = None
    if alert_point:
        alert_info = (f"{alert_point['name']} sea alert level: {alert_point['level'].upper()}. {alert_point['headline']} "
                      f"Wind now {alert_point['wind_speed_ms']} m/s ({round((alert_point['wind_speed_ms'] or 0) * 3.6, 1)} km/h), "
                      f"24 h max wind {alert_point['wind_speed_max_24h_ms']} m/s, 24 h max waves {alert_point['wave_height_max_24h_m']} m.")
    routing_res = run_routing_agent(
        lat,
        lon,
        weather_data=weather_res,
        satellite_data=sat_res
    )
    routing_info = routing_res["info"]
    if named_place and named_place["id"] != "chennai":
        # The Routing agent only plans to its fixed Chennai fishing-ground waypoint
        routing_info = (f"No route planned for {named_place['name']}: the route agent currently only plans "
                        f"to the Chennai offshore fishing ground. Do not give route or distance advice.")
    safety_res = run_safety_agent(payload.message)

    has_warning = safety_res["has_warning"] or scidl_res["has_warning"]
    # Only take warning text from agents that actually raised a warning
    warning_parts = [r["warning_text"] for r in (safety_res, scidl_res) if r["has_warning"] and r["warning_text"]]
    warning_text = " ".join(warning_parts) if has_warning else None

    invoked_agents = [
        sat_res["agent_name"],
        weather_res["agent_name"],
        scidl_res["agent_name"],
        routing_res["agent_name"],
        safety_res["agent_name"],
        "Ollama LLM Synthesis",
    ]
    citations = [sat_res["source"], weather_res["source"], scidl_res["source"], routing_res["source"]]
    if alert_point:
        citations.append("Open-Meteo Forecast (coastal sea alerts)")

    lang = resolve_language(payload.language, payload.message)

    history = SESSION_STORE[session_id][-settings.CHAT_HISTORY_TURNS:]
    context_block = build_agent_context(
        user_message=payload.message,
        target_language=lang,
        lat=lat,
        lon=lon,
        location_name=location_name,
        alert_info=alert_info,
        sat_info=sat_res["info"],
        weather_info=weather_res["info"],
        scidl_info=scidl_res["info"],
        routing_info=routing_info,
        safety_warning=warning_text,
        has_warning=has_warning,
        wind_speed_ms=(scidl_res.get("predictions") or {}).get("wind_speed_ms"),
        voice=bool(payload.voice),
    )

    try:
        llm_res = await ollama_client.chat(build_chat_messages(history, context_block))
        llm_reply = llm_res["content"]
        citations.append(f"Ollama ({llm_res['model']})")
    except OllamaUnavailable as exc:
        logger.warning(f"LLM unavailable, returning raw agent data: {exc}")
        llm_reply = build_offline_reply(lang, has_warning, warning_text, weather_res, sat_res, scidl_res,
                                        {**routing_res, "info": routing_info})
        invoked_agents.remove("Ollama LLM Synthesis")

    SESSION_STORE[session_id].append({"user": payload.message, "bot": llm_reply})

    return ChatResponse(
        reply=llm_reply,
        session_id=session_id,
        detected_language=lang,
        has_warning=has_warning,
        warning_message=warning_text,
        trigger_peer_call=safety_res["trigger_peer_call"],
        invoked_agents=invoked_agents,
        citations=citations
    )

# Serve the ORCA frontend (index.html, app.js, style.css) from the same origin,
# so its relative fetch('/api/chat') / fetch('/predict') calls reach this API.
# Mounted last so every API route above takes priority.
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    logger.warning(f"Frontend directory not found at {FRONTEND_DIR}; only the API will be served.")
