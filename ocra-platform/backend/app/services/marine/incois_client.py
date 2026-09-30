"""
Client for INCOIS ERDDAP OceanSat & Marine Satellite Data.

Queries live OceanSat-2/3 Chlorophyll-a and Argo/Satellite SST grids
from INCOIS ERDDAP (https://erddap.incois.gov.in/erddap/griddap).
"""

import math
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_ERDDAP_URL = "https://erddap.incois.gov.in/erddap/griddap"


def fetch_incois_chlorophyll(lat: float, lon: float, timeout: int = 10) -> dict:
    """
    Retrieves OceanSat chlorophyll-a concentration (mg/m3) from INCOIS ERDDAP.
    If the exact point is masked or null, checks a surrounding 0.25-degree bounding box.
    Returns a dict with value, unit, timestamp, and source, or an error dict on failure.
    """
    dataset_id = "incois_oceansat2_datasets"
    url = f"{BASE_ERDDAP_URL}/{dataset_id}.json?CHL[(last)][({lat})][({lon})]"

    try:
        resp = requests.get(url, timeout=timeout, verify=False)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("table", {}).get("rows", [])

        val = rows[0][3] if rows and len(rows[0]) >= 4 else None
        obs_time = rows[0][0] if rows and len(rows[0]) >= 1 else ""

        # If point pixel is null or NaN (cloud cover or nearshore mask), query bounding box neighborhood
        if val is None or (isinstance(val, float) and math.isnan(val)):
            box_url = (
                f"{BASE_ERDDAP_URL}/{dataset_id}.json?"
                f"CHL[(last)][({lat - 0.25}):({lat + 0.25})][({lon - 0.25}):({lon + 0.25})]"
            )
            box_resp = requests.get(box_url, timeout=timeout, verify=False)
            if box_resp.status_code == 200:
                box_rows = box_resp.json().get("table", {}).get("rows", [])
                for row in box_rows:
                    if len(row) >= 4 and row[3] is not None and not (isinstance(row[3], float) and math.isnan(row[3])):
                        val = row[3]
                        obs_time = row[0]
                        break

        if val is not None and not (isinstance(val, float) and math.isnan(val)):
            return {
                "value": round(float(val), 3),
                "unit": "mg/m3",
                "timestamp": obs_time,
                "source": "ISRO OceanSat Data (INCOIS ERDDAP)",
            }
        return {"error": f"No valid chlorophyll data found near ({lat}, {lon})"}

    except Exception as exc:
        return {"error": f"Failed to retrieve INCOIS chlorophyll data: {str(exc)}"}


def fetch_incois_sst(lat: float, lon: float, timeout: int = 10) -> dict:
    """
    Retrieves Sea Surface Temperature (°C) from INCOIS ERDDAP Argo/SST grids.
    Returns a dict with value, unit, and timestamp, or an error dict on failure.
    """
    dataset_id = "incois_argo_10d_VAM"
    url = f"{BASE_ERDDAP_URL}/{dataset_id}.json?TEMP[(last)][(0)][({lat})][({lon})]"

    try:
        resp = requests.get(url, timeout=timeout, verify=False)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("table", {}).get("rows", [])

        val = rows[0][4] if rows and len(rows[0]) >= 5 else None
        obs_time = rows[0][0] if rows and len(rows[0]) >= 1 else ""

        if val is not None and not (isinstance(val, float) and math.isnan(val)):
            return {
                "value": round(float(val), 1),
                "unit": "°C",
                "timestamp": obs_time,
                "source": "INCOIS Argo SST Data",
            }
        return {"error": f"No valid SST data found near ({lat}, {lon})"}

    except Exception as exc:
        return {"error": f"Failed to retrieve INCOIS SST data: {str(exc)}"}
