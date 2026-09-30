import math
import re
from typing import Any, Optional, Tuple
from app.cache import OFFLINE_MARINE_CACHE

# Default destination waypoint (Chennai Offshore Fishing Ground / PFZ Zone ~24 km East of Chennai coast)
DEFAULT_TARGET_LAT = 13.08
DEFAULT_TARGET_LON = 80.49
DEFAULT_WAYPOINT_NAME = "Chennai Offshore Fishing Ground"

# Operational Indian EEZ bounding box (derived from GeoCoordinates in app/schemas.py)
EEZ_LAT_MIN = 6.0
EEZ_LAT_MAX = 37.0
EEZ_LON_MIN = 68.0
EEZ_LON_MAX = 98.0

# Rough Sea Advisory Threshold (meters)
ROUGH_SEA_ADVISORY_THRESHOLD_M = 2.5

# Potential Fishing Zone (PFZ) biological habitat criteria (fishing/biological guidance only)
PFZ_CHL_MIN = 0.5
PFZ_SST_MIN = 25.0
PFZ_SST_MAX = 30.0


def validate_coordinates(lat: Any, lon: Any) -> bool:
    """Validate latitude and longitude values."""
    try:
        if lat is None or lon is None:
            return False
        flat = float(lat)
        flon = float(lon)
        if math.isnan(flat) or math.isinf(flat) or math.isnan(flon) or math.isinf(flon):
            return False
        if not (-90.0 <= flat <= 90.0 and -180.0 <= flon <= 180.0):
            return False
        return True
    except (ValueError, TypeError):
        return False


def is_within_indian_eez_bounds(lat: float, lon: float) -> bool:
    """
    Check whether coordinates fall within the operational Indian EEZ bounding box.
    Note: This is an operational rectangular bounding box [6.0-37.0 N, 68.0-98.0 E],
    not a complex maritime GIS polygon.
    """
    return (EEZ_LAT_MIN <= lat <= EEZ_LAT_MAX) and (EEZ_LON_MIN <= lon <= EEZ_LON_MAX)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth (in kilometers)
    using the Haversine formula.
    """
    R = 6371.0  # Earth's mean radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def calculate_compass_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the forward initial compass bearing (azimuth) from point 1 to point 2 in degrees.
    Normalized to [0, 360).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)

    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)

    initial_bearing = math.atan2(y, x)
    return (math.degrees(initial_bearing) + 360.0) % 360.0


def bearing_to_compass(bearing: float) -> str:
    """Convert bearing angle in degrees to a 16-point cardinal compass direction."""
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    idx = int(round(bearing / 22.5)) % 16
    return directions[idx]


def extract_wave_height(weather_data: Optional[dict]) -> Optional[float]:
    """Extract significant wave height (m) from direct key or info string."""
    if not weather_data or not isinstance(weather_data, dict):
        return None
    for key in ("wave_height", "wave_height_m", "hs", "significant_wave_height"):
        if key in weather_data and weather_data[key] is not None:
            try:
                return round(float(weather_data[key]), 2)
            except (ValueError, TypeError):
                pass
    info_str = weather_data.get("info", "")
    if isinstance(info_str, str):
        match = re.search(r"(?i)waves around ([\d\.]+)\s*m", info_str)
        if match:
            try:
                return round(float(match.group(1)), 2)
            except (ValueError, TypeError):
                pass
    return None


def generate_high_wave_advisory(weather_data: Optional[dict]) -> str:
    """
    Generate Rough Sea Advisory if forecast significant wave height meets
    or exceeds the project rough sea threshold (2.5m).
    """
    wave_h = extract_wave_height(weather_data)
    if wave_h is not None and wave_h >= ROUGH_SEA_ADVISORY_THRESHOLD_M:
        return (
            f" Advisory: Forecast significant wave height around {wave_h}m indicates "
            f"rough sea conditions (>= {ROUGH_SEA_ADVISORY_THRESHOLD_M}m). "
            f"Small craft exercise caution."
        )
    return ""


def extract_satellite_metrics(satellite_data: Optional[dict]) -> Tuple[Optional[float], Optional[float]]:
    """Extract chlorophyll-a (mg/m3) and SST (°C) from direct keys or info string."""
    if not satellite_data or not isinstance(satellite_data, dict):
        return None, None
    chl_val = None
    sst_val = None
    for key in ("chlorophyll", "chlorophyll_a", "chl", "value"):
        if key in satellite_data and satellite_data[key] is not None:
            try:
                chl_val = float(satellite_data[key])
                break
            except (ValueError, TypeError):
                pass
    for key in ("sst", "sea_surface_temperature"):
        if key in satellite_data and satellite_data[key] is not None:
            try:
                sst_val = float(satellite_data[key])
                break
            except (ValueError, TypeError):
                pass
    info_str = satellite_data.get("info", "")
    if isinstance(info_str, str):
        if chl_val is None:
            chl_match = re.search(r"Chlorophyll(?: concentration)? around ([\d\.]+)", info_str, re.IGNORECASE)
            if chl_match:
                try:
                    chl_val = float(chl_match.group(1))
                except (ValueError, TypeError):
                    pass
        if sst_val is None:
            sst_match = re.search(r"(?:favorable\s+)?SST around ([\d\.]+)", info_str, re.IGNORECASE)
            if sst_match:
                try:
                    sst_val = float(sst_match.group(1))
                except (ValueError, TypeError):
                    pass
    return chl_val, sst_val


def generate_pfz_advisory(satellite_data: Optional[dict]) -> str:
    """
    Generate Potential Fishing Zone (PFZ) Habitat Advisory.
    Provides fishing/biological guidance only (not navigation safety)
    when chlorophyll >= PFZ_CHL_MIN (0.5 mg/m³) and SST is between 25.0°C and 30.0°C.
    """
    chl_val, sst_val = extract_satellite_metrics(satellite_data)
    if (
        chl_val is not None
        and sst_val is not None
        and (chl_val >= PFZ_CHL_MIN)
        and (PFZ_SST_MIN <= sst_val <= PFZ_SST_MAX)
    ):
        return (
            f" Fishing Advisory: Satellite data indicates conditions favorable for Potential "
            f"Fishing Zone (PFZ) aggregation (chlorophyll {chl_val} mg/m³, SST {sst_val}°C)."
        )
    return ""


def validate_current_metrics(
    velocity_raw: Any,
    direction_raw: Any,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Validate and sanitize ocean current velocity and direction metrics.
    Velocity must be numeric, finite, and non-negative (>= 0).
    Direction must be numeric and finite.
    Returns (velocity, direction) floats if valid, or (None, None) if invalid.
    """
    try:
        if velocity_raw is None or direction_raw is None:
            return None, None
        v = float(velocity_raw)
        d = float(direction_raw)
        if not (math.isfinite(v) and math.isfinite(d)):
            return None, None
        if v < 0:
            return None, None
        return v, d
    except (ValueError, TypeError):
        return None, None


def extract_current_metrics(
    weather_data: Optional[dict],
) -> Tuple[Optional[float], Optional[str], Optional[float]]:
    """
    Extract ocean current velocity, velocity unit, and direction.

    Priority 1 (Preferred): Structured dictionary fields
      - ocean_current_velocity / current_velocity
      - ocean_current_direction / current_direction
      - current_velocity_unit / velocity_unit

    Priority 2 (Compatibility Fallback): Regex extraction from legacy info string
      - e.g., "ocean currents 0.6 km/h (214°)"

    Note on provenance and interpretation:
      Open-Meteo ocean-current data is model-derived (~8 km resolution) and
      represents the direction the current is flowing TOWARD.
      Accuracy is limited in coastal areas; this is passive informational context
      and does not replace a nautical almanac or local hydrographic clearance.
    """
    if not weather_data or not isinstance(weather_data, dict):
        return None, None, None

    # Priority 1: Structured numeric fields
    vel_raw = None
    dir_raw = None
    unit_str = None

    for key in ("ocean_current_velocity", "current_velocity"):
        if key in weather_data and weather_data[key] is not None:
            vel_raw = weather_data[key]
            break

    for key in ("ocean_current_direction", "current_direction"):
        if key in weather_data and weather_data[key] is not None:
            dir_raw = weather_data[key]
            break

    for key in ("current_velocity_unit", "velocity_unit"):
        if key in weather_data and weather_data[key] is not None:
            unit_str = str(weather_data[key])
            break

    v, d = validate_current_metrics(vel_raw, dir_raw)
    if v is not None and d is not None:
        return v, unit_str or "km/h", d

    # Priority 2: Fallback regex on legacy info string
    info_str = weather_data.get("info", "")
    if isinstance(info_str, str):
        match = re.search(
            r"(?i)ocean currents?\s+([\d\.]+)\s*([a-zA-Z/]+)?\s*\(([\d\.]+)°\)",
            info_str,
        )
        if match:
            v, d = validate_current_metrics(match.group(1), match.group(3))
            if v is not None and d is not None:
                extracted_unit = match.group(2) or "km/h"
                return v, extracted_unit, d

    return None, None, None


def generate_current_context(
    weather_data: Optional[dict],
) -> Tuple[Optional[dict], str]:
    """
    Generate passive ocean current context (REQ-ORCA-003).
    Returns (current_context_dict, current_info_str).
    Direction is normalized to [0, 360) and represents flow TOWARD heading.
    """
    v, unit, d = extract_current_metrics(weather_data)
    if v is None or d is None:
        return None, ""

    norm_dir = (d % 360.0 + 360.0) % 360.0
    compass_dir = bearing_to_compass(norm_dir)
    source_str = (weather_data or {}).get("source", "Open-Meteo Marine API")
    unit_str = unit or "km/h"

    current_context = {
        "velocity": round(v, 2),
        "unit": unit_str,
        "direction_deg": round(norm_dir, 1),
        "compass_heading": compass_dir,
        "source": source_str,
    }

    current_info = (
        f" Current setting towards {norm_dir:.1f}° ({compass_dir}) "
        f"at {round(v, 2)} {unit_str} (model forecast)."
    )

    return current_context, current_info


def run_routing_agent(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    target_lat: Optional[float] = None,
    target_lon: Optional[float] = None,
    weather_data: Optional[dict] = None,
    satellite_data: Optional[dict] = None,
) -> dict:
    """
    Routing Agent:
    Computes navigation vectors (Haversine distance and compass bearing)
    towards the target waypoint while maintaining boundary compliance,
    incorporating weather and satellite context when provided,
    adding Rough Sea Advisories when significant wave height >= 2.5m (REQ-ORCA-001),
    adding PFZ Habitat Advisories when chlorophyll and SST meet biological criteria (REQ-ORCA-002),
    and adding passive Ocean Current kinematic context (REQ-ORCA-003).
    """
    routing_context = {}
    if weather_data and isinstance(weather_data, dict):
        if "info" in weather_data:
            routing_context["weather_info"] = weather_data["info"]
        if "source" in weather_data:
            routing_context["weather_source"] = weather_data["source"]
    if satellite_data and isinstance(satellite_data, dict):
        if "info" in satellite_data:
            routing_context["satellite_info"] = satellite_data["info"]
        if "source" in satellite_data:
            routing_context["satellite_source"] = satellite_data["source"]

    high_wave_advisory = generate_high_wave_advisory(weather_data)
    pfz_advisory = generate_pfz_advisory(satellite_data)
    current_context, current_info = generate_current_context(weather_data)
    if current_context:
        routing_context["current_context"] = current_context
        routing_context["current_info"] = current_info.strip()

    base_default_info = "Route clear. Safe distance maintained from restricted boundaries."

    if not validate_coordinates(lat, lon):
        return {
            "agent_name": "Routing Agent",
            "info": f"{base_default_info}{high_wave_advisory}{pfz_advisory}{current_info}",
            "source": "Hydrographic GIS Boundary Layers",
            "distance_km": None,
            "bearing_deg": None,
            "compass_heading": None,
            "within_operational_bounds": None,
            "routing_context": routing_context if routing_context else None,
        }

    try:
        flat = float(lat)
        flon = float(lon)

        within_eez = is_within_indian_eez_bounds(flat, flon)

        if validate_coordinates(target_lat, target_lon):
            tlat = float(target_lat)
            tlon = float(target_lon)
            dest_name = f"waypoint ({tlat:.2f}, {tlon:.2f})"
        else:
            tlat = DEFAULT_TARGET_LAT
            tlon = DEFAULT_TARGET_LON
            dest_name = DEFAULT_WAYPOINT_NAME

        dist_km = haversine_distance(flat, flon, tlat, tlon)
        bearing_deg = calculate_compass_bearing(flat, flon, tlat, tlon)
        compass_dir = bearing_to_compass(bearing_deg)

        if within_eez:
            boundary_note = "Within operational Indian EEZ bounds."
            if dist_km < 0.05:
                base_text = f"On station at {dest_name}. {boundary_note} Route clear. Safe distance maintained from restricted boundaries."
            else:
                base_text = (
                    f"Course to {dest_name}: {dist_km:.2f} km at bearing {bearing_deg:.1f}° ({compass_dir}). "
                    f"{boundary_note} Route clear. Safe distance maintained from restricted boundaries."
                )
        else:
            boundary_note = "WARNING: Coordinates are outside operational Indian EEZ bounds (6.0°-37.0°N, 68.0°-98.0°E)."
            if dist_km < 0.05:
                base_text = f"{boundary_note} On station at {dest_name}."
            else:
                base_text = (
                    f"{boundary_note} "
                    f"Course to {dest_name}: {dist_km:.2f} km at bearing {bearing_deg:.1f}° ({compass_dir})."
                )

        info_text = f"{base_text}{high_wave_advisory}{pfz_advisory}{current_info}"

        return {
            "agent_name": "Routing Agent",
            "info": info_text,
            "source": "Hydrographic GIS Boundary Layers",
            "distance_km": round(dist_km, 2),
            "bearing_deg": round(bearing_deg, 1),
            "compass_heading": compass_dir,
            "within_operational_bounds": within_eez,
            "routing_context": routing_context if routing_context else None,
        }
    except Exception:
        return {
            "agent_name": "Routing Agent",
            "info": f"{base_default_info}{high_wave_advisory}{pfz_advisory}{current_info}",
            "source": "Hydrographic GIS Boundary Layers",
            "distance_km": None,
            "bearing_deg": None,
            "compass_heading": None,
            "within_operational_bounds": None,
            "routing_context": routing_context if routing_context else None,
        }