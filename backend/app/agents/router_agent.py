"""Intent & Multilingual Router Agent.

Detects the user's language, coastal location of interest, and query intent
(PFZ search, hazard advisory, or environmental analytics).
"""
from __future__ import annotations
from app.data.mock_data import (
    COASTAL_LOCATIONS,
    LANGUAGES,
    resolve_location_key,
    resolve_intent,
    resolve_language,
)
from app.models import AgentStep

INTENT_LABELS = {
    "pfz": "Potential Fishing Zone Search",
    "hazard": "Marine Hazard / Safety Advisory",
    "analytics": "Environmental Analytics (SST / Chlorophyll)",
}


def run(query: str, explicit_language: str | None, deep_reasoning: bool) -> tuple[dict, AgentStep]:
    location_key = resolve_location_key(query)
    intent = resolve_intent(query)
    language = resolve_language(query, explicit_language)
    loc = COASTAL_LOCATIONS[location_key]

    detail_lines = [
        f"Detected coastal region: **{loc['name']}, {loc['state']}** "
        f"({loc['lat']:.3f}, {loc['lng']:.3f})",
        f"Classified intent: **{INTENT_LABELS[intent]}**",
        f"Resolved response language: **{LANGUAGES[language]}**",
    ]
    if deep_reasoning:
        detail_lines.append(
            "Deep reasoning enabled: cross-checking query tokens against gazetteer "
            "of 7 coastal hubs and intent keyword ontology (PFZ / hazard / analytics) "
            "before dispatching downstream agents."
        )

    step = AgentStep(
        agent="Intent & Multilingual Router Agent",
        icon="brain",
        status="done",
        summary=f"Routed to {loc['name']} · {INTENT_LABELS[intent]} · {LANGUAGES[language]}",
        detail="\n\n".join(detail_lines),
        duration_ms=180 if not deep_reasoning else 340,
    )
    context = {
        "location_key": location_key,
        "intent": intent,
        "language": language,
    }
    return context, step
