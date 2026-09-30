from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str = Field(..., json_schema_extra={"example": "Where should I fish near Chennai today?"})
    language: Optional[str] = "en"
    session_id: Optional[str] = None
    voice: Optional[bool] = False  # answer will be spoken aloud by the voice assistant
    lat: Optional[float] = None
    lon: Optional[float] = None

class GeoCoordinates(BaseModel):
    lat: float
    lon: float

    @field_validator("lat", "lon")
    def validate_indian_eez(cls, v, info):
        if info.field_name == "lat" and not (6.0 <= v <= 37.0):
            raise ValueError("Latitude is outside the operational Indian EEZ.")
        if info.field_name == "lon" and not (68.0 <= v <= 98.0):
            raise ValueError("Longitude is outside the operational Indian EEZ.")
        return v

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    detected_language: str
    has_warning: bool = False
    warning_message: Optional[str] = None
    trigger_peer_call: bool = False
    invoked_agents: List[str]
    citations: List[str]

class PredictRequest(BaseModel):
    lat: float = Field(default=13.0827, description="Latitude degree (-90 to 90)")
    lon: float = Field(default=80.2707, description="Longitude degree (-180 to 180)")
    forecast_hours: int = Field(default=24, description="Forecast step projection in hours")
    variables: Optional[List[str]] = Field(
        default=["u10", "v10", "msl", "t2m", "swh"],
        description="Atmospheric and ocean surface variables to predict"
    )
    model_name: Optional[str] = Field(
        default="SFNO",
        description="Target SciDL model: SFNO, FourCastNet, GraphCast, Aurora, PINN_Swin"
    )
    data_source: Optional[str] = Field(
        default="GFS",
        description="Initial condition data feed: GFS, ERA5, SYNTHETIC"
    )
    time: Optional[str] = Field(default="latest", description="Initial condition timestamp or 'latest'")

class PredictResponse(BaseModel):
    status: str
    model_name: str
    data_source: str
    forecast_time: str
    coordinates: dict
    predictions: dict
    units: dict
    execution_engine: str
    execution_device: str
    inference_time_ms: float
    metadata: Optional[dict] = None

class ModelDetail(BaseModel):
    id: str
    name: str
    type: str
    framework: str
    description: str
    predicts: List[str]
    grid_resolution: str
    status: str
    access_method: str

class ModelListResponse(BaseModel):
    models: List[ModelDetail]
    default_model: str
    total: int

class FineTuneRequest(BaseModel):
    base_model_name: Optional[str] = Field(default="SFNO", description="Base model to fine-tune: SFNO, FOURCASTNET, PINN_SWIN")
    dataset_path: Optional[str] = Field(default="data/indian_ocean_training.nc", description="Regional NetCDF dataset path")
    epochs: int = Field(default=5, description="Number of fine-tuning epochs")
    learning_rate: float = Field(default=1e-4, description="Optimizer learning rate")
    batch_size: int = Field(default=4, description="Batch size")
    use_amp: bool = Field(default=True, description="Enable Automatic Mixed Precision (FP16)")

class FineTuneStatusResponse(BaseModel):
    status: str
    job_id: Optional[str] = None
    base_model: Optional[str] = None
    epochs_completed: Optional[int] = None
    initial_loss: Optional[float] = None
    final_loss: Optional[float] = None
    checkpoint_saved: Optional[str] = None
    elapsed_seconds: Optional[float] = None
    device: Optional[str] = None
    message: Optional[str] = None

class DatasetDownloadRequest(BaseModel):
    source: Optional[str] = Field(default="COPERNICUS", description="Data source: COPERNICUS, ARGO, SYNTHETIC")
    dataset_id: Optional[str] = Field(default="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m", description="Copernicus dataset ID")
    variables: Optional[List[str]] = Field(default=["thetao", "so", "uo", "vo"], description="Target variables")
    min_lon: float = Field(default=45.0, description="Minimum longitude degree")
    max_lon: float = Field(default=100.0, description="Maximum longitude degree")
    min_lat: float = Field(default=-10.0, description="Minimum latitude degree")
    max_lat: float = Field(default=30.0, description="Maximum latitude degree")

class LocationPoint(BaseModel):
    lat: float
    lon: float
    point_id: Optional[str] = None

class BatchPredictRequest(BaseModel):
    points: List[LocationPoint] = Field(..., description="List of lat/lon coordinate points")
    forecast_hours: int = Field(default=24, description="Forecast horizon in hours")
    model_name: Optional[str] = Field(default="SFNO", description="Target model")
    variables: Optional[List[str]] = Field(default=["u10", "v10", "msl", "t2m", "swh"])

class BatchPredictResponse(BaseModel):
    status: str
    model_name: str
    total_points: int
    results: List[PredictResponse]