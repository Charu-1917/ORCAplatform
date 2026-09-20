from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    language: Optional[str] = None
    deep_reasoning: bool = False
    live_data: bool = False
    voice_mode: bool = False


class AgentStep(BaseModel):
    agent: str
    icon: str
    status: Literal["pending", "running", "done"]
    summary: str
    detail: str
    duration_ms: int


class PFZZone(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    radius_km: float
    score: float
    depth_m: float


class HeatmapPoint(BaseModel):
    lat: float
    lng: float
    value: float


class CurrentVector(BaseModel):
    lat: float
    lng: float
    direction_deg: int
    speed_kmph: float


class Hazard(BaseModel):
    id: str
    region_name: str
    title: str
    level: Literal["green", "yellow", "red"]
    description: str
    wind_speed_kmph: float
    wave_height_m: float


class ChartPoint(BaseModel):
    day: str
    sst: float
    chlorophyll: float


class QueryResponse(BaseModel):
    query: str
    language: str
    language_label: str
    intent: str
    location_name: str
    location_state: str
    center: dict
    alert_level: Literal["green", "yellow", "red"]
    markdown: str
    audio_text: str
    agent_steps: list[AgentStep]
    pfz_zones: list[PFZZone]
    heatmap: list[HeatmapPoint]
    current_vectors: list[CurrentVector]
    hazards: list[Hazard]
    chart_data: list[ChartPoint]
