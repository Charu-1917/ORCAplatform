"""
Live coastal sea-state alerts for the Indian coastline.

Uses the Open-Meteo Marine (waves) and Forecast (10 m wind) APIs for a fixed
set of offshore points and flags where the next 24 h forecast crosses the
project's safety thresholds. These are computed from forecast data; they are
NOT official INCOIS / IMD bulletins, and every alert says so.
"""

import re
import math
import time
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List

import requests

logger = logging.getLogger("orca.alerts")

MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Offshore points (a few km off the coast so the marine grid has sea data)
COASTAL_POINTS = [
    {"id": "chennai", "name": "Chennai", "state": "Tamil Nadu", "lat": 13.08, "lon": 80.40},
    {"id": "puducherry", "name": "Puducherry", "state": "Puducherry", "lat": 11.90, "lon": 79.95},
    {"id": "nagapattinam", "name": "Nagapattinam", "state": "Tamil Nadu", "lat": 10.77, "lon": 80.00},
    {"id": "rameswaram", "name": "Rameswaram", "state": "Tamil Nadu", "lat": 9.28, "lon": 79.40},
    {"id": "thoothukudi", "name": "Thoothukudi", "state": "Tamil Nadu", "lat": 8.75, "lon": 78.30},
    {"id": "kanyakumari", "name": "Kanyakumari", "state": "Tamil Nadu", "lat": 7.95, "lon": 77.55},
    {"id": "kochi", "name": "Kochi", "state": "Kerala", "lat": 9.95, "lon": 76.10},
    {"id": "kozhikode", "name": "Kozhikode", "state": "Kerala", "lat": 11.25, "lon": 75.65},
    {"id": "mangaluru", "name": "Mangaluru", "state": "Karnataka", "lat": 12.85, "lon": 74.70},
    {"id": "goa", "name": "Goa", "state": "Goa", "lat": 15.45, "lon": 73.65},
    {"id": "mumbai", "name": "Mumbai", "state": "Maharashtra", "lat": 18.90, "lon": 72.70},
    {"id": "veraval", "name": "Veraval", "state": "Gujarat", "lat": 20.85, "lon": 70.30},
    {"id": "visakhapatnam", "name": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.65, "lon": 83.40},
    {"id": "kakinada", "name": "Kakinada", "state": "Andhra Pradesh", "lat": 16.90, "lon": 82.40},
    {"id": "paradip", "name": "Paradip", "state": "Odisha", "lat": 20.25, "lon": 86.80},
    {"id": "digha", "name": "Digha", "state": "West Bengal", "lat": 21.55, "lon": 87.60},
    {"id": "portblair", "name": "Port Blair", "state": "Andaman & Nicobar", "lat": 11.65, "lon": 92.80},
]

# Extra spellings (Tamil script, common short forms) used to recognise a place named in a chat message
PLACE_ALIASES = {
    "chennai": ["chennai", "madras", "kasimedu", "சென்னை", "காசிமேடு", "चेन्नई", "చెన్నై", "ಚೆನ್ನೈ", "ചെന്നൈ", "চেন্নাই"],
    "puducherry": ["puducherry", "pondicherry", "pondy", "karaikal", "புதுச்சேரி", "காரைக்கால்", "पुडुचेरी", "పుదుచ్చేరి"],
    "nagapattinam": ["nagapattinam", "nagai", "நாகப்பட்டினம்", "நாகை"],
    "rameswaram": ["rameswaram", "rameshwaram", "pamban", "ராமேஸ்வரம்", "இராமேஸ்வரம்", "பாம்பன்", "रामेश्वरम"],
    "thoothukudi": ["thoothukudi", "tuticorin", "தூத்துக்குடி", "तूतुकुडी"],
    "kanyakumari": ["kanyakumari", "kanniyakumari", "cape comorin", "கன்னியாகுமரி", "குமரி", "कन्याकुमारी", "കന്യാകുമാരി", "ಕನ್ಯಾಕುಮಾರಿ"],
    "kochi": ["kochi", "cochin", "கொச்சி", "कोच्चि", "കൊച്ചി", "ಕೊಚ್ಚಿ"],
    "kozhikode": ["kozhikode", "calicut", "कोझिकोड", "കോഴിക്കോട്"],
    "mangaluru": ["mangaluru", "mangalore", "मंगलुरु", "मंगलौर", "ಮಂಗಳೂರು", "മംഗലാപുരം"],
    "goa": ["goa", "गोवा", "ಗೋವಾ", "ഗോവ"],
    "mumbai": ["mumbai", "bombay", "मुंबई", "मुम्बई", "ಮುಂಬೈ", "ముంబై", "മുംബൈ", "মুম্বাই", "મુંબઈ"],
    "veraval": ["veraval", "वेरावल", "વેરાવળ"],
    "visakhapatnam": ["visakhapatnam", "vizag", "vishakhapatnam", "विशाखापत्तनम", "విశాఖపట్నం", "విశాఖ", "বিশাখাপত্তনম"],
    "kakinada": ["kakinada", "काकीनाडा", "కాకినాడ"],
    "paradip": ["paradip", "paradeep", "पारादीप"],
    "digha": ["digha", "दीघा", "দীঘা"],
    "portblair": ["port blair", "andaman", "पोर्ट ब्लेयर", "अंडमान"],
}


def find_place_in_text(text: str):
    """Returns the coastal point named in a message (earliest mention wins), or None."""
    lowered = text.lower()
    best = None
    for point in COASTAL_POINTS:
        for alias in PLACE_ALIASES.get(point["id"], [point["name"].lower()]):
            if alias.isascii():
                # Whole words only, so "goa" does not match "goal"
                match = re.search(r"\b" + re.escape(alias) + r"\b", lowered)
                idx = match.start() if match else -1
            else:
                idx = lowered.find(alias)
            if idx != -1 and (best is None or idx < best[0]):
                best = (idx, point)
    return best[1] if best else None


# Thresholds: 2.5 m / 12 m/s match the existing Routing (rough sea) and SciDL agents.
LEVELS = [
    # (level, min wave m, min wind m/s)
    ("danger", 3.5, 17.0),   # very rough sea / gale force (Beaufort 8+)
    ("warning", 2.5, 12.0),  # rough sea / strong wind - small craft should not venture
    ("caution", 1.5, 8.0),   # moderate sea - exercise caution
]
LEVEL_RANK = {"danger": 3, "warning": 2, "caution": 1, "normal": 0}

CACHE_SECONDS = 600
_cache: Dict[str, Any] = {"at": 0.0, "data": None}
_lock = threading.Lock()


def _max_next_24h(hourly: dict, key: str, now_iso: str):
    times = hourly.get("time", [])
    values = hourly.get(key, [])
    window = [v for t, v in zip(times, values) if t >= now_iso[:13] and v is not None][:24]
    return max(window) if window else None


def _classify(wave_m, wind_ms) -> str:
    for level, wave_min, wind_min in LEVELS:
        if (wave_m is not None and wave_m >= wave_min) or (wind_ms is not None and wind_ms >= wind_min):
            return level
    return "normal"


def _fetch() -> Dict[str, Any]:
    lats = ",".join(str(p["lat"]) for p in COASTAL_POINTS)
    lons = ",".join(str(p["lon"]) for p in COASTAL_POINTS)
    common = {"latitude": lats, "longitude": lons, "forecast_days": 2, "timezone": "Asia/Kolkata"}

    marine = requests.get(MARINE_URL, params={**common, "current": "wave_height", "hourly": "wave_height"}, timeout=20)
    marine.raise_for_status()
    wind = requests.get(FORECAST_URL, params={**common, "current": "wind_speed_10m,wind_gusts_10m",
                                              "hourly": "wind_speed_10m", "wind_speed_unit": "ms"}, timeout=20)
    wind.raise_for_status()
    marine_list, wind_list = marine.json(), wind.json()
    if isinstance(marine_list, dict):
        marine_list = [marine_list]
    if isinstance(wind_list, dict):
        wind_list = [wind_list]

    points = []
    for p, m, w in zip(COASTAL_POINTS, marine_list, wind_list):
        m_cur, w_cur = m.get("current", {}), w.get("current", {})
        now_iso = m_cur.get("time") or w_cur.get("time") or ""
        wave_now = m_cur.get("wave_height")
        wave_max = _max_next_24h(m.get("hourly", {}), "wave_height", now_iso)
        wind_now = w_cur.get("wind_speed_10m")
        wind_max = _max_next_24h(w.get("hourly", {}), "wind_speed_10m", now_iso)
        gust_now = w_cur.get("wind_gusts_10m")

        worst_wave = max([v for v in (wave_now, wave_max) if v is not None], default=None)
        worst_wind = max([v for v in (wind_now, wind_max) if v is not None], default=None)
        level = _classify(worst_wave, worst_wind)

        parts = []
        if worst_wave is not None and worst_wave >= 1.5:
            parts.append(f"waves up to {worst_wave} m")
        if worst_wind is not None and worst_wind >= 8.0:
            parts.append(f"wind up to {worst_wind} m/s ({round(worst_wind * 3.6)} km/h)")
        if level == "danger":
            headline = f"Very rough sea off {p['name']}: " + ", ".join(parts) + " in the next 24 h. Fishermen should not venture out."
        elif level == "warning":
            headline = f"Rough sea off {p['name']}: " + ", ".join(parts) + " in the next 24 h. Small boats should stay near shore."
        elif level == "caution":
            headline = f"Moderate sea off {p['name']}: " + ", ".join(parts) + " in the next 24 h. Exercise caution."
        else:
            headline = f"Calm to slight sea off {p['name']} (waves {wave_now} m, wind {wind_now} m/s)."

        points.append({
            **p,
            "level": level,
            "headline": headline,
            "wave_height_m": wave_now,
            "wave_height_max_24h_m": wave_max,
            "wind_speed_ms": wind_now,
            "wind_speed_max_24h_ms": wind_max,
            "wind_gust_ms": gust_now,
            "observed_at": now_iso,
            # Stable id per location+level+day so the frontend can show each new alert only once
            "alert_id": f"{p['id']}:{level}:{now_iso[:10]}",
        })

    points.sort(key=lambda x: (-LEVEL_RANK[x["level"]], -(x["wave_height_max_24h_m"] or 0)))
    return {
        "status": "success",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Open-Meteo Marine & Forecast API (computed forecast alerts, not an official INCOIS/IMD bulletin)",
        "thresholds": {"caution": "waves >= 1.5 m or wind >= 8 m/s",
                       "warning": "waves >= 2.5 m or wind >= 12 m/s",
                       "danger": "waves >= 3.5 m or wind >= 17 m/s"},
        "alert_count": sum(1 for x in points if x["level"] != "normal"),
        "points": points,
    }


def nearest_alert_point(lat, lon, max_km: float = 120.0):
    """Returns the cached live alert entry for the coastal point nearest to (lat, lon), within max_km."""
    if lat is None or lon is None:
        return None
    data = get_sea_alerts()
    best = None
    for p in data.get("points", []):
        # Equirectangular approximation is plenty for "which port is closest"
        dx = (p["lon"] - lon) * 111.32 * math.cos(math.radians((p["lat"] + lat) / 2))
        dy = (p["lat"] - lat) * 110.57
        dist = math.hypot(dx, dy)
        if dist <= max_km and (best is None or dist < best[0]):
            best = (dist, p)
    return best[1] if best else None


def get_sea_alerts() -> Dict[str, Any]:
    with _lock:
        if _cache["data"] and time.time() - _cache["at"] < CACHE_SECONDS:
            return _cache["data"]
        try:
            data = _fetch()
            _cache.update(at=time.time(), data=data)
            return data
        except Exception as exc:
            logger.warning(f"Sea alert fetch failed: {exc}")
            if _cache["data"]:
                stale = dict(_cache["data"])
                stale["stale"] = True
                return stale
            return {"status": "error", "error": f"Live sea data unavailable: {exc}", "alert_count": 0, "points": []}
