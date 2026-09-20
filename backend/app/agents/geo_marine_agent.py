"""ISRO Satellite & Ocean Data Retrieval Agent.

Simulates querying ISRO Bhuvan / INCOIS style endpoints for SST,
Chlorophyll-a, ocean current vectors, and PFZ candidate zones.
"""
from __future__ import annotations
from app.data.mock_data import (
    COASTAL_LOCATIONS,
    get_pfz_zones,
    get_sst_heatmap,
    get_current_vectors,
    get_sst_chlorophyll_series,
)
from app.models import AgentStep


def run(location_key: str, live_data: bool, deep_reasoning: bool) -> tuple[dict, AgentStep]:
    loc = COASTAL_LOCATIONS[location_key]
    pfz_zones = get_pfz_zones(location_key)
    heatmap = get_sst_heatmap(location_key)
    vectors = get_current_vectors(location_key)
    chart_data = get_sst_chlorophyll_series(location_key)

    source = (
        "Live ISRO Earth Observation feed (Oceansat-3 OCM, SCATSAT-1)"
        if live_data
        else "Cached mock dataset (simulated Oceansat-3 / INCOIS PFZ advisory)"
    )

    detail_lines = [
        f"Data source: {source}",
        f"Retrieved **{len(pfz_zones)}** candidate PFZ polygons within 40 nm of "
        f"{loc['name']}.",
        f"Sampled **{len(heatmap)}** SST grid pixels and **{len(vectors)}** ocean "
        "current vectors.",
        f"Latest SST: {chart_data[-1]['sst']} °C · Chlorophyll-a: "
        f"{chart_data[-1]['chlorophyll']} mg/m³.",
    ]
    if deep_reasoning:
        detail_lines.append(
            "Cross-referencing chlorophyll fronts with thermal gradients to rank "
            "PFZ polygons by biological productivity likelihood score."
        )

    step = AgentStep(
        agent="ISRO Satellite & Ocean Data Retrieval Agent",
        icon="satellite",
        status="done",
        summary=f"Fetched SST, Chlorophyll-a & {len(pfz_zones)} PFZ candidates near {loc['name']}",
        detail="\n\n".join(detail_lines),
        duration_ms=420 if live_data else 260,
    )
    context = {
        "pfz_zones": pfz_zones,
        "heatmap": heatmap,
        "current_vectors": vectors,
        "chart_data": chart_data,
    }
    return context, step
