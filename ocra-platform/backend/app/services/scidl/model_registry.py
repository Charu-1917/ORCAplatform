import logging
from typing import Dict, Any, List, Optional

from app.services.scidl.earth2studio_engine import Earth2StudioEngine
from app.services.scidl.pinn_swin_engine import PINNSwinEngine
from app.schemas import ModelDetail, ModelListResponse

logger = logging.getLogger("scidl.registry")


class SciDLModelRegistry:
    """
    Central Scientific Deep Learning Model Registry.
    Routes inference calls to appropriate framework engines (Earth2Studio, PINN/Swin-UNet).
    """

    def __init__(self, device: str = "auto"):
        self.earth2studio_engine = Earth2StudioEngine(device=device)
        self.pinn_swin_engine = PINNSwinEngine()
        
        self.registered_models: Dict[str, Dict[str, Any]] = {
            "SFNO": {
                "id": "SFNO",
                "name": "NVIDIA Spherical Fourier Neural Operator (SFNO)",
                "type": "Prognostic Global Dynamics Engine",
                "framework": "NVIDIA Earth2Studio / Modulus",
                "description": "Spherical FNO predicting 73 surface and atmospheric variables on a 0.25° grid.",
                "predicts": ["10m Wind (u10, v10)", "Mean Sea Level Pressure (msl)", "2m Temperature (t2m)", "Significant Wave Height (swh)"],
                "grid_resolution": "0.25° (~25km)",
                "status": "active",
                "access_method": "earth2studio.models.px.SFNO",
                "engine_type": "earth2studio"
            },
            "FOURCASTNET": {
                "id": "FOURCASTNET",
                "name": "NVIDIA FourCastNet v3",
                "type": "Fourier Neural Operator (FNO)",
                "framework": "NVIDIA Earth2Studio",
                "description": "High-resolution atmospheric prognostic engine for extreme weather and wave state forecasting.",
                "predicts": ["u10", "v10", "msl", "t2m", "swh", "sst"],
                "grid_resolution": "0.25° (~25km)",
                "status": "active",
                "access_method": "earth2studio.models.px.FourCastNet",
                "engine_type": "earth2studio"
            },
            "GRAPHCAST": {
                "id": "GRAPHCAST",
                "name": "Google DeepMind GraphCast",
                "type": "Spatio-Temporal Graph Neural Network (ST-GNN)",
                "framework": "NVIDIA Earth2Studio / Google Cloud",
                "description": "Global atmospheric and sea-surface states forecasted on icosahedral 3D meshes.",
                "predicts": ["u10", "v10", "msl", "t2m", "geopotential", "swh"],
                "grid_resolution": "0.25° (~25km)",
                "status": "active",
                "access_method": "earth2studio.models.px.GraphCastOperational / gs://dm_graphcast",
                "engine_type": "earth2studio"
            },
            "AURORA": {
                "id": "AURORA",
                "name": "Microsoft Aurora Foundation Model",
                "type": "Large Multiscale Atmospheric & Surface Foundation Model",
                "framework": "NVIDIA Earth2Studio / HuggingFace",
                "description": "Integrated global forecasts combining multi-scale satellite observations and ocean surface dynamics.",
                "predicts": ["u10", "v10", "msl", "t2m", "swh", "sst", "total_precipitation"],
                "grid_resolution": "0.1° (~10km)",
                "status": "active",
                "access_method": "earth2studio.models.px.Aurora / microsoft/aurora",
                "engine_type": "earth2studio"
            },
            "PINN_SWIN": {
                "id": "PINN_SWIN",
                "name": "Custom Swin-UNet & PhysicsNeMo PINN",
                "type": "Physics-Informed Neural Network (PINN) + Swin-UNet",
                "framework": "PyTorch / NVIDIA PhysicsNeMo / DeepXDE",
                "description": "Subsurface thermocline dynamics, wave power density, ocean vorticity, and PDE shallow water solver.",
                "predicts": ["swh", "u10", "v10", "current_speed_ms", "thermocline_depth_m", "subsurface_temp_20m_c", "wave_power_kw_m", "ocean_vorticity"],
                "grid_resolution": "Continuous Domain (PINN)",
                "status": "active",
                "access_method": "PyTorch WaveNavierStokesPINN + Swin-UNet Vision Transformer",
                "engine_type": "pinn_swin"
            },
            "SFNO_FINETUNED_INDIAN_OCEAN": {
                "id": "SFNO_FINETUNED_INDIAN_OCEAN",
                "name": "NVIDIA SFNO Fine-Tuned (Indian Ocean Slice)",
                "type": "Regional Fine-Tuned Prognostic Surrogate",
                "framework": "NVIDIA Earth2Studio / PyTorch FP16 AMP",
                "description": "Fine-tuned SFNO head on Copernicus Marine NetCDF slice (Lat -10° to 30°, Lon 45° to 100°).",
                "predicts": ["u10", "v10", "msl", "t2m", "swh", "sst", "salinity"],
                "grid_resolution": "0.083° (~9km Regional)",
                "status": "active",
                "access_method": "checkpoints/orca_sfno_indian_ocean.pt",
                "engine_type": "earth2studio"
            },
            "PINN_CORRECTOR_INDIAN_OCEAN": {
                "id": "PINN_CORRECTOR_INDIAN_OCEAN",
                "name": "PhysicsNeMo PINN Predictor-Corrector (Indian Ocean)",
                "type": "Subsurface & Thermocline Corrector Model",
                "framework": "PyTorch / ARGO Float Network Data",
                "description": "Fine-tuned corrector head trained on ARGO Float 0m-2000m depth profiles.",
                "predicts": ["thermocline_depth_m", "subsurface_temp_20m_c", "swh", "wave_power_kw_m", "ocean_vorticity"],
                "grid_resolution": "Continuous ARGO Profile Domain",
                "status": "active",
                "access_method": "checkpoints/orca_pinn_swin_indian_ocean.pt",
                "engine_type": "pinn_swin"
            }
        }
        logger.info(f"Loaded {len(self.registered_models)} scientific models into SciDLModelRegistry")

    def list_models(self) -> ModelListResponse:
        model_details = [
            ModelDetail(
                id=m["id"],
                name=m["name"],
                type=m["type"],
                framework=m["framework"],
                description=m["description"],
                predicts=m["predicts"],
                grid_resolution=m["grid_resolution"],
                status=m["status"],
                access_method=m["access_method"]
            )
            for m in self.registered_models.values()
        ]
        return ModelListResponse(
            models=model_details,
            default_model="SFNO",
            total=len(model_details)
        )

    def predict(
        self,
        lat: float,
        lon: float,
        forecast_hours: int = 24,
        variables: Optional[List[str]] = None,
        model_name: str = "SFNO",
        data_source: str = "GFS",
        timestamp: str = "latest"
    ) -> Dict[str, Any]:
        """
        Unified prediction entrypoint routing to appropriate engine.
        """
        model_key = model_name.upper().strip()
        model_meta = self.registered_models.get(model_key)
        
        if not model_meta:
            # Default to SFNO if unrecognised model requested
            model_key = "SFNO"
            model_meta = self.registered_models["SFNO"]

        engine_type = model_meta["engine_type"]

        if engine_type == "pinn_swin":
            return self.pinn_swin_engine.run_inference(
                lat=lat,
                lon=lon,
                forecast_hours=forecast_hours,
                variables=variables,
                data_source=data_source
            )
        else:
            return self.earth2studio_engine.run_inference(
                lat=lat,
                lon=lon,
                forecast_hours=forecast_hours,
                variables=variables,
                model_name=model_key,
                data_source=data_source,
                timestamp=timestamp
            )


# Global singleton instance
scidl_registry = SciDLModelRegistry()
