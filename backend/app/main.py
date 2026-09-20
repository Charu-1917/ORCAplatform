from __future__ import annotations
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import QueryRequest, QueryResponse
from app.orchestrator import run_pipeline
from app.data.mock_data import COASTAL_LOCATIONS, LANGUAGES, HAZARD_DB

app = FastAPI(
    title="ORCA API",
    description="Oceanic Reasoning & Collaborative Agents — ISRO Smart India Hackathon prototype",
    version="1.0.0",
)

frontend_url = os.getenv("FRONTEND_URL", "*")
allowed_origins = [
    origin.strip()
    for origin in frontend_url.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "orca-backend"}


@app.get("/api/locations")
def list_locations():
    return [
        {"key": key, "name": loc["name"], "state": loc["state"], "lat": loc["lat"], "lng": loc["lng"]}
        for key, loc in COASTAL_LOCATIONS.items()
    ]


@app.get("/api/languages")
def list_languages():
    return [{"code": code, "label": label} for code, label in LANGUAGES.items()]


@app.get("/api/hazards")
def list_hazards():
    return HAZARD_DB


@app.post("/api/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")
    return run_pipeline(req)
