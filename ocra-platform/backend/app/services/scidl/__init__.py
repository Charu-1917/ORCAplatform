"""
Scientific Deep Learning (SciDL) Ocean & Atmospheric AI Engine Package
"""
from app.services.scidl.earth2studio_engine import Earth2StudioEngine
from app.services.scidl.pinn_swin_engine import PINNSwinEngine
from app.services.scidl.model_registry import SciDLModelRegistry

__all__ = ["Earth2StudioEngine", "PINNSwinEngine", "SciDLModelRegistry"]
