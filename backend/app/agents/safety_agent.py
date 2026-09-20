"""Marine Safety & Hazard Advisory Agent.

Checks wind speed, wave height, and cyclone advisories, and computes an
overall alert level (Green / Yellow / Red).
"""
from __future__ import annotations
from app.data.mock_data import get_hazards_for_location, compute_alert_level, COASTAL_LOCATIONS
from app.models import AgentStep


def run(location_key: str, deep_reasoning: bool) -> tuple[dict, AgentStep]:
    loc = COASTAL_LOCATIONS[location_key]
    hazards = get_hazards_for_location(location_key)
    alert_level = compute_alert_level(hazards)

    detail_lines = [
        f"Checked {len(hazards)} active advisory record(s) for {loc['name']}, {loc['state']}.",
    ]
    for h in hazards:
        detail_lines.append(
            f"- **{h['title']}** [{h['level'].upper()}]: {h['description']} "
            f"(wind {h['wind_speed_kmph']} km/h, wave {h['wave_height_m']} m)"
        )
    detail_lines.append(f"Computed composite alert level: **{alert_level.upper()}**")

    if deep_reasoning:
        detail_lines.append(
            "Alert level derived using max-severity fusion across cyclone watch, "
            "high-wave warning and wind-advisory channels, consistent with INCOIS "
            "Ocean State Forecast severity fusion rules."
        )

    step = AgentStep(
        agent="Marine Safety & Hazard Advisory Agent",
        icon="shield-alert",
        status="done",
        summary=f"Alert level: {alert_level.upper()} · {len(hazards)} advisory record(s)",
        detail="\n\n".join(detail_lines),
        duration_ms=300 if deep_reasoning else 190,
    )
    context = {"hazards": hazards, "alert_level": alert_level}
    return context, step
