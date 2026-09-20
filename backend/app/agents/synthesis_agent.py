"""Synthesis Agent.

Aggregates all upstream agent outputs into a single markdown response,
prepares map/chart payloads, and generates the regional-language advisory
text used for the text-to-speech widget.
"""
from __future__ import annotations
from app.data.mock_data import (
    LANGUAGES,
    ADVISORY_TEMPLATES,
    ALERT_LEVEL_LABELS,
    HAZARD_NOTE_TEMPLATES,
)
from app.models import AgentStep

ALERT_EMOJI = {"green": "🟢", "yellow": "🟡", "red": "🔴"}


def build_markdown(
    location_name: str,
    location_state: str,
    intent: str,
    ranked_zones: list[dict],
    hazards: list[dict],
    alert_level: str,
    correlation: float,
    chart_data: list[dict],
) -> str:
    lines = [f"## Marine Advisory — {location_name}, {location_state}"]
    lines.append(
        f"**Overall Sea Safety Status:** {ALERT_EMOJI[alert_level]} "
        f"{alert_level.upper()}"
    )
    lines.append("")
    lines.append("### 🎣 Potential Fishing Zones (PFZ)")
    if ranked_zones:
        for z in ranked_zones:
            lines.append(
                f"- **{z['name']}** — {z['lat']:.3f}, {z['lng']:.3f} "
                f"(radius {z['radius_km']} km, depth {z['depth_m']} m, "
                f"productivity score **{z['score']:.2f}**)"
            )
    else:
        lines.append("- No high-confidence PFZ candidates found for this window.")

    lines.append("")
    lines.append("### ⚠️ Safety Advisories")
    if hazards:
        for h in hazards:
            lines.append(
                f"- {ALERT_EMOJI[h['level']]} **{h['title']}** ({h['region_name']}): "
                f"{h['description']}"
            )
    else:
        lines.append("- No active hazards reported.")

    lines.append("")
    lines.append("### 🌡️ SST & Chlorophyll-a Trend (7 days)")
    latest = chart_data[-1]
    lines.append(
        f"- Latest SST: **{latest['sst']} °C**, Chlorophyll-a: "
        f"**{latest['chlorophyll']} mg/m³**"
    )
    lines.append(f"- 7-day SST↔Chlorophyll correlation coefficient: **{correlation}**")

    lines.append("")
    lines.append(
        "> ORCA combines simulated ISRO Oceansat-3 / SCATSAT-1 imagery with "
        "INCOIS-style advisory logic. This is a hackathon prototype using mock data."
    )
    return "\n".join(lines)


def build_audio_text(
    language: str,
    location_name: str,
    zone_count: int,
    alert_level: str,
    hazards: list[dict],
) -> str:
    template = ADVISORY_TEMPLATES.get(language, ADVISORY_TEMPLATES["en"])
    alert_label = ALERT_LEVEL_LABELS[alert_level].get(
        language, ALERT_LEVEL_LABELS[alert_level]["en"]
    )
    if hazards:
        note_template = HAZARD_NOTE_TEMPLATES.get(language, HAZARD_NOTE_TEMPLATES["en"])
        top_hazard = hazards[0]
        hazard_note = note_template.format(
            title=top_hazard["title"], description=top_hazard["description"]
        )
    else:
        hazard_note = ""
    return template.format(
        location=location_name,
        zone_count=zone_count,
        alert_level=alert_label,
        hazard_note=hazard_note,
    ).strip()


def run(
    location_name: str,
    location_state: str,
    intent: str,
    language: str,
    ranked_zones: list[dict],
    hazards: list[dict],
    alert_level: str,
    correlation: float,
    chart_data: list[dict],
    deep_reasoning: bool,
) -> tuple[dict, AgentStep]:
    markdown = build_markdown(
        location_name, location_state, intent, ranked_zones, hazards,
        alert_level, correlation, chart_data,
    )
    audio_text = build_audio_text(language, location_name, len(ranked_zones), alert_level, hazards)

    detail_lines = [
        f"Composed markdown advisory ({len(markdown)} chars) covering PFZ, safety "
        "and environmental sections.",
        f"Translated spoken advisory into **{LANGUAGES[language]}** for the TTS widget.",
    ]
    if deep_reasoning:
        detail_lines.append(
            "Applied template-based neural-machine-translation simulation with "
            "domain-specific marine vocabulary substitution for regional dialects."
        )

    step = AgentStep(
        agent="Synthesis & Translation Agent",
        icon="sparkles",
        status="done",
        summary=f"Generated final advisory in {LANGUAGES[language]}",
        detail="\n\n".join(detail_lines),
        duration_ms=210 if deep_reasoning else 140,
    )
    context = {"markdown": markdown, "audio_text": audio_text}
    return context, step
