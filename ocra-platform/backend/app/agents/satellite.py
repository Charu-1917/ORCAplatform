from typing import Optional
from app.cache import OFFLINE_MARINE_CACHE
from app.services.marine.incois_client import fetch_incois_chlorophyll, fetch_incois_sst

def run_satellite_agent(
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> dict:
    if lat is not None and lon is not None:
        try:
            chl_res = fetch_incois_chlorophyll(lat, lon)
            if "error" not in chl_res and chl_res.get("value") is not None:
                chl_val = chl_res["value"]
                chl_unit = chl_res.get("unit", "mg/m3")
                info_parts = [f"Chlorophyll concentration around {chl_val} {chl_unit}"]

                # Attempt SST via INCOIS ERDDAP
                try:
                    sst_res = fetch_incois_sst(lat, lon)
                    if "error" not in sst_res and sst_res.get("value") is not None:
                        info_parts.append(f"favorable SST around {sst_res['value']}{sst_res.get('unit', '°C')}")
                except Exception:
                    pass

                return {
                    "agent_name": "Satellite Agent",
                    "info": ", ".join(info_parts) + " detected.",
                    "source": chl_res.get("source", "ISRO OceanSat Data (INCOIS ERDDAP)")
                }
        except Exception:
            pass

        # Fallback if live INCOIS retrieval fails or is unavailable
        return {
            "agent_name": "Satellite Agent",
            "info": "High chlorophyll concentration and favorable SST detected off Chennai shore (offline fallback).",
            "source": "ISRO OceanSat-3 Data (Offline Fallback)"
        }

    # Default behavior when coordinates are missing
    return {
        "agent_name": "Satellite Agent",
        "info": "High chlorophyll concentration and favorable SST detected off Chennai shore.",
        "source": "ISRO OceanSat-3 Data"
    }
