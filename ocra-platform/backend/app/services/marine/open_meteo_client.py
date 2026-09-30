"""
Client for Open-Meteo Marine Weather API.

Retrieves real-time ocean dynamics:
- Significant wave height (m)
- Wave direction (degrees)
- Wind wave height & swell wave height (m)
- Ocean current velocity (m/s) & direction (degrees)
- Sea surface temperature (°C)
- Observation timestamp
"""

import requests

OPEN_METEO_MARINE_BASE = "https://marine-api.open-meteo.com/v1/marine"


def fetch_open_meteo_marine(lat: float, lon: float) -> dict:
    """
    Fetches marine weather parameters from Open-Meteo API for given coordinates.
    Returns a dictionary containing marine dynamics metrics on success,
    or a structured error dictionary on failure.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "wave_height,wave_direction,sea_surface_temperature,ocean_current_velocity,ocean_current_direction",
        "hourly": "wave_height,wind_wave_height,swell_wave_height,ocean_current_direction",
    }

    try:
        resp = requests.get(OPEN_METEO_MARINE_BASE, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        current_units = data.get("current_units", {})
        hourly = data.get("hourly", {})

        wind_wave = hourly.get("wind_wave_height", [None])[0] if hourly.get("wind_wave_height") else None
        swell_wave = hourly.get("swell_wave_height", [None])[0] if hourly.get("swell_wave_height") else None

        return {
            "latitude": lat,
            "longitude": lon,
            "timestamp": current.get("time"),
            "wave_height": current.get("wave_height"),
            "wave_height_unit": current_units.get("wave_height", "m"),
            "wave_direction": current.get("wave_direction"),
            "wave_direction_unit": current_units.get("wave_direction", "°"),
            "sea_surface_temperature": current.get("sea_surface_temperature"),
            "sst_unit": current_units.get("sea_surface_temperature", "°C"),
            "ocean_current_velocity": current.get("ocean_current_velocity"),
            "current_velocity_unit": current_units.get("ocean_current_velocity", "m/s"),
            "ocean_current_direction": current.get("ocean_current_direction"),
            "current_direction_unit": current_units.get("ocean_current_direction", "°"),
            "wind_wave_height": wind_wave,
            "swell_wave_height": swell_wave,
            "source": "Open-Meteo Marine API",
        }
    except Exception as exc:
        return {
            "error": f"Failed to retrieve Open-Meteo marine data: {str(exc)}",
            "latitude": lat,
            "longitude": lon,
            "source": "Open-Meteo Marine API",
        }
