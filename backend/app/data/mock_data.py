"""Mock ISRO / INCOIS style datasets for the ORCA prototype.

All values are simulated for demonstration purposes and are not sourced
from live satellite feeds.
"""
from __future__ import annotations
import math
import random
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Coastal reference locations (major Indian fishing hubs)
# ---------------------------------------------------------------------------
COASTAL_LOCATIONS = {
    "kochi": {
        "name": "Kochi",
        "state": "Kerala",
        "lat": 9.9312,
        "lng": 76.2673,
        "aliases": ["kochi", "cochin", "kerala"],
    },
    "chennai": {
        "name": "Chennai",
        "state": "Tamil Nadu",
        "lat": 13.0827,
        "lng": 80.2707,
        "aliases": ["chennai", "madras", "tamil nadu", "tn"],
    },
    "vizag": {
        "name": "Visakhapatnam",
        "state": "Andhra Pradesh",
        "lat": 17.6868,
        "lng": 83.2185,
        "aliases": ["vizag", "visakhapatnam", "andhra", "andhra pradesh"],
    },
    "veraval": {
        "name": "Veraval",
        "state": "Gujarat",
        "lat": 20.9159,
        "lng": 70.3629,
        "aliases": ["veraval", "gujarat", "porbandar", "saurashtra"],
    },
    "kanyakumari": {
        "name": "Kanyakumari",
        "state": "Tamil Nadu",
        "lat": 8.0883,
        "lng": 77.5385,
        "aliases": ["kanyakumari", "cape comorin", "gulf of mannar", "mannar"],
    },
    "mumbai": {
        "name": "Mumbai",
        "state": "Maharashtra",
        "lat": 19.0760,
        "lng": 72.8777,
        "aliases": ["mumbai", "bombay", "maharashtra", "konkan"],
    },
    "paradip": {
        "name": "Paradip",
        "state": "Odisha",
        "lat": 20.3167,
        "lng": 86.6167,
        "aliases": ["paradip", "odisha", "orissa"],
    },
}

DEFAULT_LOCATION_KEY = "kochi"

# ---------------------------------------------------------------------------
# Potential Fishing Zone (PFZ) seed data per location
# Each zone is offset (km-ish in degrees) from the base location.
# ---------------------------------------------------------------------------
PFZ_SEED = {
    "kochi": [
        {"offset": (0.35, 0.55), "radius_km": 8, "score": 0.92, "depth_m": 45},
        {"offset": (-0.20, 0.75), "radius_km": 6, "score": 0.81, "depth_m": 60},
        {"offset": (0.60, 0.25), "radius_km": 5, "score": 0.74, "depth_m": 38},
    ],
    "chennai": [
        {"offset": (0.30, 0.65), "radius_km": 7, "score": 0.88, "depth_m": 50},
        {"offset": (-0.15, 0.85), "radius_km": 6, "score": 0.79, "depth_m": 65},
    ],
    "vizag": [
        {"offset": (0.25, 0.70), "radius_km": 9, "score": 0.90, "depth_m": 55},
        {"offset": (0.55, 0.40), "radius_km": 5, "score": 0.72, "depth_m": 42},
    ],
    "veraval": [
        {"offset": (0.20, -0.60), "radius_km": 10, "score": 0.86, "depth_m": 48},
        {"offset": (-0.40, -0.35), "radius_km": 6, "score": 0.77, "depth_m": 33},
    ],
    "kanyakumari": [
        {"offset": (0.15, 0.45), "radius_km": 6, "score": 0.83, "depth_m": 52},
        {"offset": (-0.30, 0.30), "radius_km": 5, "score": 0.69, "depth_m": 40},
    ],
    "mumbai": [
        {"offset": (0.10, -0.55), "radius_km": 8, "score": 0.80, "depth_m": 44},
    ],
    "paradip": [
        {"offset": (0.30, 0.50), "radius_km": 7, "score": 0.85, "depth_m": 47},
    ],
}

# ---------------------------------------------------------------------------
# Hazard / advisory database (simulated INCOIS style warnings)
# ---------------------------------------------------------------------------
HAZARD_DB = [
    {
        "id": "gom-hw-01",
        "region_key": "kanyakumari",
        "region_name": "Gulf of Mannar, Tamil Nadu",
        "title": "High Wave Warning",
        "level": "yellow",
        "description": "Sea state rough with wave heights of 2.5-3.2 m expected over the "
        "next 48 hours. Small craft advised to avoid deep-sea fishing.",
        "wind_speed_kmph": 42,
        "wave_height_m": 2.8,
    },
    {
        "id": "guj-cyc-01",
        "region_key": "veraval",
        "region_name": "Gujarat Coast (Veraval - Porbandar)",
        "title": "Cyclone Watch",
        "level": "red",
        "description": "A depression over the Arabian Sea is likely to intensify. "
        "Fishermen are strongly advised not to venture into the sea until further notice.",
        "wind_speed_kmph": 68,
        "wave_height_m": 4.1,
    },
    {
        "id": "ap-mod-01",
        "region_key": "vizag",
        "region_name": "Visakhapatnam Coast, Andhra Pradesh",
        "title": "Moderate Wind Advisory",
        "level": "yellow",
        "description": "Gusty winds of 35-45 km/h likely along the coast. Exercise caution "
        "near harbour entrances.",
        "wind_speed_kmph": 38,
        "wave_height_m": 1.9,
    },
    {
        "id": "ker-safe-01",
        "region_key": "kochi",
        "region_name": "Kochi Coast, Kerala",
        "title": "Conditions Normal",
        "level": "green",
        "description": "Sea conditions are moderate and safe for fishing operations "
        "within 50 nautical miles.",
        "wind_speed_kmph": 18,
        "wave_height_m": 1.1,
    },
    {
        "id": "tn-safe-01",
        "region_key": "chennai",
        "region_name": "Chennai Coast, Tamil Nadu",
        "title": "Conditions Normal",
        "level": "green",
        "description": "No significant hazards reported. Sea state slight to moderate.",
        "wind_speed_kmph": 20,
        "wave_height_m": 1.3,
    },
    {
        "id": "mh-safe-01",
        "region_key": "mumbai",
        "region_name": "Mumbai Coast, Maharashtra",
        "title": "Conditions Normal",
        "level": "green",
        "description": "Sea state slight. Safe for near-shore fishing activity.",
        "wind_speed_kmph": 22,
        "wave_height_m": 1.4,
    },
    {
        "id": "od-mod-01",
        "region_key": "paradip",
        "region_name": "Paradip Coast, Odisha",
        "title": "Moderate Wave Advisory",
        "level": "yellow",
        "description": "Wave heights of 2.0-2.4 m expected due to an offshore trough. "
        "Small mechanised boats should exercise caution.",
        "wind_speed_kmph": 33,
        "wave_height_m": 2.1,
    },
]


def get_hazards_for_location(location_key: str) -> list[dict]:
    matches = [h for h in HAZARD_DB if h["region_key"] == location_key]
    if not matches:
        matches = [h for h in HAZARD_DB if h["level"] == "green"]
    return matches


def compute_alert_level(hazards: list[dict]) -> str:
    levels = {"red": 3, "yellow": 2, "green": 1}
    if not hazards:
        return "green"
    worst = max(hazards, key=lambda h: levels.get(h["level"], 0))
    return worst["level"]


# ---------------------------------------------------------------------------
# Time-series generation: SST (Sea Surface Temp) vs Chlorophyll-a, 7 days
# ---------------------------------------------------------------------------
def get_sst_chlorophyll_series(location_key: str) -> list[dict]:
    seed = sum(ord(c) for c in location_key)
    rng = random.Random(seed)
    base_sst = 27.5 + (seed % 5) * 0.3
    base_chl = 0.35 + (seed % 7) * 0.05
    series = []
    today = datetime.utcnow()
    for i in range(7):
        day = today - timedelta(days=6 - i)
        sst = round(base_sst + math.sin(i / 2.0) * 0.6 + rng.uniform(-0.15, 0.15), 2)
        chl = round(base_chl + math.cos(i / 1.7) * 0.08 + rng.uniform(-0.02, 0.02), 3)
        series.append(
            {
                "day": day.strftime("%b %d"),
                "sst": sst,
                "chlorophyll": max(chl, 0.05),
            }
        )
    return series


# ---------------------------------------------------------------------------
# SST heatmap grid points around a location (simulated satellite pixels)
# ---------------------------------------------------------------------------
def get_sst_heatmap(location_key: str) -> list[dict]:
    loc = COASTAL_LOCATIONS[location_key]
    rng = random.Random(sum(ord(c) for c in location_key) + 7)
    base_sst = 27.5 + (sum(ord(c) for c in location_key) % 5) * 0.3
    points = []
    for dx in [-0.6, -0.3, 0, 0.3, 0.6, 0.9]:
        for dy in [-0.4, -0.2, 0, 0.2, 0.4, 0.6]:
            value = round(base_sst + rng.uniform(-1.2, 1.2), 2)
            points.append(
                {
                    "lat": round(loc["lat"] + dy, 4),
                    "lng": round(loc["lng"] + dx, 4),
                    "value": value,
                }
            )
    return points


def get_pfz_zones(location_key: str) -> list[dict]:
    loc = COASTAL_LOCATIONS[location_key]
    zones = []
    for i, seed in enumerate(PFZ_SEED.get(location_key, [])):
        dlat, dlng = seed["offset"]
        zones.append(
            {
                "id": f"{location_key}-pfz-{i+1}",
                "name": f"PFZ-{i+1} off {loc['name']}",
                "lat": round(loc["lat"] + dlat, 4),
                "lng": round(loc["lng"] + dlng, 4),
                "radius_km": seed["radius_km"],
                "score": seed["score"],
                "depth_m": seed["depth_m"],
            }
        )
    return zones


# ---------------------------------------------------------------------------
# Ocean current vectors (simulated), a few arrows around the location
# ---------------------------------------------------------------------------
def get_current_vectors(location_key: str) -> list[dict]:
    loc = COASTAL_LOCATIONS[location_key]
    rng = random.Random(sum(ord(c) for c in location_key) + 21)
    vectors = []
    for dx in [-0.4, 0, 0.4]:
        for dy in [-0.3, 0.3]:
            vectors.append(
                {
                    "lat": round(loc["lat"] + dy, 4),
                    "lng": round(loc["lng"] + dx, 4),
                    "direction_deg": rng.randint(0, 359),
                    "speed_kmph": round(rng.uniform(1.5, 6.0), 1),
                }
            )
    return vectors


# ---------------------------------------------------------------------------
# Multilingual response templates
# ---------------------------------------------------------------------------
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "bn": "Bengali",
    "gu": "Gujarati",
    "mr": "Marathi",
}

# {location} {alert_level} {zone_count} are substituted at runtime
ADVISORY_TEMPLATES = {
    "en": "ORCA Marine Advisory for {location}: {zone_count} Potential Fishing Zones "
    "identified nearby. Current safety status is {alert_level}. {hazard_note}",
    "hi": "{location} के लिए ORCA समुद्री सलाह: पास में {zone_count} संभावित मत्स्य क्षेत्र "
    "मिले हैं। वर्तमान सुरक्षा स्थिति {alert_level} है। {hazard_note}",
    "ta": "{location} க்கான ORCA கடல் ஆலோசனை: அருகில் {zone_count} சாத்தியமான மீன்பிடி "
    "மண்டலங்கள் கண்டறியப்பட்டுள்ளன. தற்போதைய பாதுகாப்பு நிலை {alert_level}. {hazard_note}",
    "te": "{location} కోసం ORCA సముద్ర సలహా: సమీపంలో {zone_count} సంభావ్య మత్స్య మండలాలు "
    "గుర్తించబడ్డాయి. ప్రస్తుత భద్రతా స్థితి {alert_level}. {hazard_note}",
    "ml": "{location} നായുള്ള ORCA സമുദ്ര ഉപദേശം: സമീപത്ത് {zone_count} സാധ്യതയുള്ള മത്സ്യബന്ധന "
    "മേഖലകൾ കണ്ടെത്തി. നിലവിലെ സുരക്ഷാ നില {alert_level} ആണ്. {hazard_note}",
    "bn": "{location} এর জন্য ORCA সামুদ্রিক পরামর্শ: কাছাকাছি {zone_count}টি সম্ভাব্য মৎস্য "
    "অঞ্চল চিহ্নিত করা হয়েছে। বর্তমান নিরাপত্তা অবস্থা {alert_level}। {hazard_note}",
    "gu": "{location} માટે ORCA દરિયાઈ સલાહ: નજીકમાં {zone_count} સંભવિત મત્સ્ય ઝોન મળી "
    "આવ્યા છે. હાલની સલામતી સ્થિતિ {alert_level} છે. {hazard_note}",
    "mr": "{location} साठी ORCA सागरी सल्ला: जवळपास {zone_count} संभाव्य मासेमारी क्षेत्रे "
    "आढळली आहेत. सध्याची सुरक्षा स्थिती {alert_level} आहे. {hazard_note}",
}

ALERT_LEVEL_LABELS = {
    "green": {
        "en": "Safe (Green)", "hi": "सुरक्षित (हरा)", "ta": "பாதுகாப்பானது (பச்சை)",
        "te": "సురక్షితం (ఆకుపచ్చ)", "ml": "സുരക്ഷിതം (പച്ച)", "bn": "নিরাপদ (সবুজ)",
        "gu": "સુરક્ષિત (લીલો)", "mr": "सुरक्षित (हिरवा)",
    },
    "yellow": {
        "en": "Caution (Yellow)", "hi": "सावधानी (पीला)", "ta": "எச்சரிக்கை (மஞ்சள்)",
        "te": "జాగ్రత్త (పసుపు)", "ml": "ജാഗ്രത (മഞ്ഞ)", "bn": "সতর্কতা (হলুদ)",
        "gu": "સાવચેતી (પીળો)", "mr": "सावधगिरी (पिवळा)",
    },
    "red": {
        "en": "Danger - Do Not Venture (Red)", "hi": "खतरा - समुद्र में न जाएं (लाल)",
        "ta": "ஆபத்து - கடலுக்குச் செல்ல வேண்டாம் (சிவப்பு)",
        "te": "ప్రమాదం - సముద్రంలోకి వెళ్లవద్దు (ఎరుపు)",
        "ml": "അപകടം - കടലിൽ പോകരുത് (ചുവപ്പ്)",
        "bn": "বিপদ - সমুদ্রে যাবেন না (লাল)",
        "gu": "ખતરો - દરિયામાં ન જાવ (લાલ)",
        "mr": "धोका - समुद्रात जाऊ नका (लाल)",
    },
}

HAZARD_NOTE_TEMPLATES = {
    "en": "Advisory: {title} - {description}",
    "hi": "सलाह: {title} - {description}",
    "ta": "ஆலோசனை: {title} - {description}",
    "te": "సలహా: {title} - {description}",
    "ml": "ഉപദേശം: {title} - {description}",
    "bn": "পরামর্শ: {title} - {description}",
    "gu": "સલાહ: {title} - {description}",
    "mr": "सल्ला: {title} - {description}",
}


def resolve_location_key(text: str) -> str:
    text_l = text.lower()
    for key, loc in COASTAL_LOCATIONS.items():
        for alias in loc["aliases"]:
            if alias in text_l:
                return key
    return DEFAULT_LOCATION_KEY


INTENT_KEYWORDS = {
    "pfz": ["fishing zone", "pfz", "fish", "catch", "fishermen zone"],
    "hazard": ["cyclone", "wave", "hazard", "warning", "advisory", "storm", "wind", "safety", "danger"],
    "analytics": ["sst", "chlorophyll", "correlation", "temperature", "trend", "analy"],
}


def resolve_intent(text: str) -> str:
    text_l = text.lower()
    scores = {k: 0 for k in INTENT_KEYWORDS}
    for intent, kws in INTENT_KEYWORDS.items():
        for kw in kws:
            if kw in text_l:
                scores[intent] += 1
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "pfz"
    return best


LANGUAGE_KEYWORDS = {
    "hi": ["hindi", "हिंदी"],
    "ta": ["tamil", "தமிழ்"],
    "te": ["telugu", "తెలుగు"],
    "ml": ["malayalam", "മലയാളം"],
    "bn": ["bengali", "bangla"],
    "gu": ["gujarati"],
    "mr": ["marathi"],
}


def resolve_language(text: str, explicit: str | None) -> str:
    if explicit and explicit in LANGUAGES:
        return explicit
    text_l = text.lower()
    script_ranges = {
        "hi": ("\u0900", "\u097f"),
        "bn": ("\u0980", "\u09ff"),
        "gu": ("\u0a80", "\u0aff"),
        "ta": ("\u0b80", "\u0bff"),
        "te": ("\u0c00", "\u0c7f"),
        "ml": ("\u0d00", "\u0d7f"),
        "mr": ("\u0900", "\u097f"),
    }
    for code, (start, end) in script_ranges.items():
        if any(start <= character <= end for character in text):
            return code
    for code, kws in LANGUAGE_KEYWORDS.items():
        for kw in kws:
            if kw in text_l:
                return code
    return "en"
