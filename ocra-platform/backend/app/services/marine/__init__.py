"""
Marine services package for ORCA Marine Engine backend.
"""
from app.services.marine.open_meteo_client import fetch_open_meteo_marine

__all__ = ["fetch_open_meteo_marine"]
