from typing import Optional
from app.cache import OFFLINE_MARINE_CACHE
from app.services.marine.open_meteo_client import fetch_open_meteo_marine

def run_weather_agent(
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> dict:
    # When coordinates are available, query live Open-Meteo marine telemetry
    if lat is not None and lon is not None:
        try:
            live_data = fetch_open_meteo_marine(lat, lon)
            if "error" not in live_data and live_data.get("wave_height") is not None:
                wave_h = live_data.get("wave_height")
                wave_dir = live_data.get("wave_direction")
                swell_h = live_data.get("swell_wave_height")
                wind_wave_h = live_data.get("wind_wave_height")
                sst = live_data.get("sea_surface_temperature")
                current_vel = live_data.get("ocean_current_velocity")
                current_dir = live_data.get("ocean_current_direction")
                current_unit = live_data.get("current_velocity_unit", "km/h")

                info_parts = [f"Waves around {wave_h}m ({wave_dir}°)"]
                if swell_h is not None:
                    info_parts.append(f"swell {swell_h}m")
                if wind_wave_h is not None:
                    info_parts.append(f"wind wave {wind_wave_h}m")
                if sst is not None:
                    info_parts.append(f"SST {sst}°C")
                if current_vel is not None and current_dir is not None:
                    info_parts.append(f"ocean currents {current_vel} {current_unit} ({current_dir}°)")

                return {
                    "agent_name": "Weather Agent",
                    "info": ", ".join(info_parts) + ".",
                    "source": live_data.get("source", "Open-Meteo Marine API")
                }
        except Exception:
            pass

        # Fallback when coordinates were provided but live call failed
        fallback_data = OFFLINE_MARINE_CACHE.get("chennai", {
            "wave_height_m": 1.5,
            "wind_speed_kt": 14.0,
        })
        return {
            "agent_name": "Weather Agent",
            "info": f"Waves around {fallback_data['wave_height_m']}m with {fallback_data['wind_speed_kt']} kt SW winds (offline fallback).",
            "source": "INCOIS Ocean Weather Forecast (Offline Cache)"
        }

    # Default behavior when coordinates are missing
    data = OFFLINE_MARINE_CACHE["chennai"]
    return {
        "agent_name": "Weather Agent",
        "info": f"Waves around {data['wave_height_m']}m with {data['wind_speed_kt']} kt SW winds.",
        "source": "INCOIS Ocean Weather Forecast"
    }
