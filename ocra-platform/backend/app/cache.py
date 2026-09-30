from datetime import datetime, timezone

OFFLINE_MARINE_CACHE = {
    "chennai": {
        "location_name": "Chennai Offshore PFZ Zone",
        "lat": 13.08,
        "lon": 80.27,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sst_celsius": 28.4,
        "chlorophyll_mg_m3": 1.2,
        "wave_height_m": 1.5,
        "wind_speed_kt": 14.0,
        "is_restricted_zone": False
    }
}