# 🌊 ORCA Scientific Deep Learning (SciDL) Agent Integration Guide

Welcome to the **ORCA Scientific Deep Learning (SciDL) Engine**. This guide provides your AI agent team (Routing, Weather, Satellite, Safety, and Fishermen/Navigational agents) with the exact instructions, API endpoint specifications, model catalog details, and Python client code necessary to leverage state-of-the-art neural oceanography & weather models efficiently.

---

## 🚀 1. Fast Server Startup

To serve all models over high-performance FastAPI HTTP endpoints:

```bash
cd /home/franz/Downloads/MCP/sih26176-research-docs/ocra-platform/backend

PYTHONPATH=. /usr/bin/python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

FastAPI Interactive Documentation: `http://localhost:8000/docs`

---

## 🔬 2. Deep Learning Model Catalog

| Model ID | Framework / Base Engine | Output Tensors | Grid Resolution & Domain |
| :--- | :--- | :--- | :--- |
| **`SFNO`** | NVIDIA Earth2Studio / Modulus | `u10`, `v10`, `wind_speed_ms`, `msl`, `t2m`, `swh` | $0.25^\circ$ Global Grid (~25km) |
| **`FOURCASTNET`** | NVIDIA FourCastNet v3 | `u10`, `v10`, `msl`, `t2m`, `swh`, `sst` | $0.25^\circ$ Global Grid (~25km) |
| **`GRAPHCAST`** | Google DeepMind ST-GNN | `u10`, `v10`, `msl`, `t2m`, `geopotential`, `swh` | $0.25^\circ$ 3D Icosahedral Mesh |
| **`AURORA`** | Microsoft Foundation Model | `u10`, `v10`, `msl`, `t2m`, `swh`, `sst`, `precipitation` | $0.10^\circ$ Global Grid (~10km) |
| **`PINN_SWIN`** | PyTorch PINN + Swin-UNet | `swh`, `current_speed_ms`, `thermocline_depth_m`, `subsurface_temp_20m_c`, `wave_power_kw_m`, `ocean_vorticity` | Continuous Domain (PDE Solver) |
| **`SFNO_FINETUNED_INDIAN_OCEAN`** | Fine-Tuned SFNO (Copernicus) | `u10`, `v10`, `msl`, `t2m`, `swh`, `sst`, `salinity` | $0.083^\circ$ Indian Ocean (~9km) |
| **`PINN_CORRECTOR_INDIAN_OCEAN`** | Fine-Tuned PINN (ARGO Float) | `thermocline_depth_m`, `subsurface_temp_20m_c`, `swh`, `wave_power_kw_m` | Continuous ARGO Depth Profiles |

---

## 📡 3. FastAPI API Endpoints Reference

### Endpoint 1: Single Location Prediction (`POST /predict` or `POST /api/predict`)

**URL:** `http://localhost:8000/predict`  
**Method:** `POST`

#### Request Payload:
```json
{
  "lat": 13.0827,
  "lon": 80.2707,
  "forecast_hours": 24,
  "model_name": "SFNO_FINETUNED_INDIAN_OCEAN",
  "variables": ["u10", "v10", "msl", "t2m", "swh"]
}
```

#### Response Output:
```json
{
  "status": "success",
  "model_name": "NVIDIA SFNO Fine-Tuned (Indian Ocean Slice)",
  "data_source": "GFS",
  "forecast_time": "2026-09-22T00:00:00.000Z",
  "coordinates": { "lat": 13.0827, "lon": 80.2707 },
  "predictions": {
    "u10": 4.27,
    "v10": 0.48,
    "wind_speed_ms": 4.3,
    "msl": 1013.09,
    "t2m": 28.73,
    "swh": 0.9
  },
  "units": {
    "u10": "m/s", "v10": "m/s", "wind_speed_ms": "m/s",
    "msl": "hPa", "t2m": "°C", "swh": "m"
  },
  "execution_engine": "NVIDIA Earth2Studio SFNO Spherical FNO Engine",
  "execution_device": "cpu",
  "inference_time_ms": 0.11
}
```

---

### Endpoint 2: Trajectory Batch Prediction (`POST /api/predict/batch`)

Ideal for the **Routing Agent** querying wind/wave conditions across a multi-waypoint navigation route.

**URL:** `http://localhost:8000/api/predict/batch`  
**Method:** `POST`

#### Request Payload:
```json
{
  "points": [
    { "lat": 13.0827, "lon": 80.2707, "point_id": "Chennai_Port" },
    { "lat": 14.0000, "lon": 81.0000, "point_id": "Waypoint_1" },
    { "lat": 15.0000, "lon": 82.0000, "point_id": "Deep_Sea_Destination" }
  ],
  "forecast_hours": 24,
  "model_name": "SFNO"
}
```

---

### Endpoint 3: Model Listing (`GET /api/models`)

**URL:** `http://localhost:8000/api/models`  
**Method:** `GET`

Returns the active model registry catalog, including fine-tuned models, capabilities, and grid resolutions.

---

### Endpoint 4: Trigger Fine-Tuning Loop (`POST /api/finetune/start`)

**URL:** `http://localhost:8000/api/finetune/start`  
**Method:** `POST`

#### Request Payload:
```json
{
  "base_model_name": "SFNO",
  "dataset_path": "data/indian_ocean_training.nc",
  "epochs": 10,
  "learning_rate": 0.0001,
  "use_amp": true
}
```

---

## 🤖 4. Agent Team Best Practices & Python Client Code

### Python Client Helper Snippet for Agents:

```python
import requests

def query_scidl_model(lat: float, lon: float, model_name: str = "SFNO", forecast_hours: int = 24):
    url = "http://localhost:8000/predict"
    payload = {
        "lat": lat,
        "lon": lon,
        "forecast_hours": forecast_hours,
        "model_name": model_name
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error querying SciDL model: {e}")
        return None
```

### Agent Domain Matrix:

- **Routing Agent**: Call `POST /api/predict/batch` using model `SFNO_FINETUNED_INDIAN_OCEAN` to evaluate wave resistance ($swh$) and wind vector ($u_{10}, v_{10}$) along sea routes.
- **Weather & Storm Safety Agent**: Call `POST /predict` using model `FOURCASTNET` or `SFNO`. Trigger emergency alerts if $swh > 2.5\text{m}$ or wind speed $> 12\text{m/s}$.
- **Fishermen & Subsurface Agent**: Call `POST /predict` using model `PINN_CORRECTOR_INDIAN_OCEAN` or `PINN_SWIN` to query thermocline depth ($D_{20}$), subsurface temperature, and wave power density ($kW/m$).

---

## 🛠️ 5. Running Direct Fine-Tuning via CLI

To train models directly from Python using Copernicus Marine (`copernicusmarine`) or ARGO Float (`argopy`) datasets:

```bash
cd /home/franz/Downloads/MCP/sih26176-research-docs/ocra-platform/backend

PYTHONPATH=. /usr/bin/python3.11 train_indian_ocean.py --model SFNO --epochs 10 --source COPERNICUS
```
