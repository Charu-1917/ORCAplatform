"""Multi-Agent Orchestrator for ORCA.

Runs the four visible pipeline agents (Router -> Satellite Retrieval ->
Spatial-Temporal PFZ Reasoning -> Marine Safety) plus a final Synthesis
agent, and assembles the full QueryResponse payload.
"""
from __future__ import annotations
from app.agents import router_agent, geo_marine_agent, spatial_temporal_agent, safety_agent, synthesis_agent
from app.data.mock_data import COASTAL_LOCATIONS, LANGUAGES
from app.models import QueryRequest, QueryResponse


def run_pipeline(req: QueryRequest) -> QueryResponse:
    steps = []

    router_ctx, router_step = router_agent.run(req.query, req.language, req.deep_reasoning)
    steps.append(router_step)

    geo_ctx, geo_step = geo_marine_agent.run(
        router_ctx["location_key"], req.live_data, req.deep_reasoning
    )
    steps.append(geo_step)

    spatial_ctx, spatial_step = spatial_temporal_agent.run(
        geo_ctx["pfz_zones"], geo_ctx["chart_data"], req.deep_reasoning
    )
    steps.append(spatial_step)

    safety_ctx, safety_step = safety_agent.run(router_ctx["location_key"], req.deep_reasoning)
    steps.append(safety_step)

    loc = COASTAL_LOCATIONS[router_ctx["location_key"]]

    synth_ctx, synth_step = synthesis_agent.run(
        query=req.query,
        location_name=loc["name"],
        location_state=loc["state"],
        intent=router_ctx["intent"],
        language=router_ctx["language"],
        ranked_zones=spatial_ctx["ranked_zones"],
        hazards=safety_ctx["hazards"],
        alert_level=safety_ctx["alert_level"],
        correlation=spatial_ctx["correlation"],
        chart_data=geo_ctx["chart_data"],
        deep_reasoning=req.deep_reasoning,
    )
    steps.append(synth_step)

    return QueryResponse(
        query=req.query,
        language=router_ctx["language"],
        language_label=LANGUAGES[router_ctx["language"]],
        intent=router_ctx["intent"],
        location_name=loc["name"],
        location_state=loc["state"],
        center={"lat": loc["lat"], "lng": loc["lng"]},
        alert_level=safety_ctx["alert_level"],
        markdown=synth_ctx["markdown"],
        audio_text=synth_ctx["audio_text"],
        agent_steps=steps,
        pfz_zones=spatial_ctx["ranked_zones"],
        heatmap=geo_ctx["heatmap"],
        current_vectors=geo_ctx["current_vectors"],
        hazards=safety_ctx["hazards"],
        chart_data=geo_ctx["chart_data"],
    )
