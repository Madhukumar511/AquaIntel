"""API endpoints for AquaIntel multispectral ocean monitoring."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import (
    BANDS,
    FEATURE_COLS_10,
    GLOBAL_PRESET_ZONES,
    BAND_WAVELENGTHS,
    GEMINI_API_KEY
)
from core.earth_engine import EE_CONNECTED, sample_satellite_bands
from core.spectral import engineer_features
from core.model_runner import MODEL_LOADED, run_model_inference
from core.gemini_analyzer import analyze_marine_zone

router = APIRouter()

class ScanRequest(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    radius: int = Field(default=1500, gt=0, le=50000, description="Scanning radius in meters")

class GeminiRequest(BaseModel):
    zone_type: str = "Global Marine Environment"
    materials: str = "Microplastics, Synthetic Nets, Ocean Debris, Algae"
    rsi: float = 0.0
    fdi: float = 0.0
    waste_pct: float = Field(default=0.0, ge=0.0, le=100.0)

@router.get("/health")
@router.get("/api/health")
def get_health() -> Dict[str, Any]:
    """Returns real-time health and connection diagnostics."""
    return {
        "status": "ok",
        "service": "AquaIntel Global Core",
        "model_loaded": MODEL_LOADED,
        "earth_engine_connected": EE_CONNECTED,
        "gemini_api_configured": bool(GEMINI_API_KEY and not GEMINI_API_KEY.startswith("AIzaSyB")),
        "feature_bands": BANDS,
        "supported_classes": {
            0: "Debris / Plastic Waste",
            1: "Ocean Water",
            2: "Organic Algae Blooms"
        }
    }

@router.get("/api/presets")
def get_presets() -> Dict[str, Any]:
    """Returns curated high-impact marine monitoring zones."""
    return {"status": "success", "zones": GLOBAL_PRESET_ZONES}

@router.get("/api/spectral/bands")
def get_spectral_bands() -> Dict[str, Any]:
    """Returns satellite sensor wavelength information."""
    return {"sensor": "ASTER VNIR/SWIR", "bands": BAND_WAVELENGTHS}

@router.get("/api/model/info")
def get_model_info() -> Dict[str, Any]:
    """Returns neural network architecture specifications."""
    return {
        "architecture": "Sequential Deep Neural Network (512-256-128-64-3)",
        "features": FEATURE_COLS_10,
        "bands": BANDS,
        "scaler": "StandardScaler (10 features)",
        "classes": ["Marine Debris / Plastic", "Ocean Water", "Algae / Organic Blooms"],
        "color_map": {
            0: {"label": "Marine Debris", "color": "#ef4444"},
            1: {"label": "Ocean Water", "color": "#3b82f6"},
            2: {"label": "Organic Algae", "color": "#10b981"}
        }
    }

@router.post("/api/scan")
def scan_ocean_surface(request: ScanRequest) -> Dict[str, Any]:
    """
    Samples real multispectral satellite bands, computes spectral indices (FDI, NDVI),
    and executes neural network / NNLS inference to detect surface marine debris.
    Simulation fallback has been completely removed per scientific accuracy requirements.
    """
    context_profile = "Global Marine Environment"
    materials_expected = "PET Bottles, HDPE Crates, Ghost Nets, Microplastics, Oil Sheens, Minerals"
    base_value_per_ton = 250

    if not EE_CONNECTED:
        raise HTTPException(
            status_code=503,
            detail="Live satellite uplink inactive: Google Earth Engine credentials not initialized. Authenticate via 'earthengine authenticate' in terminal or set EE_PROJECT in .env. Simulation mode has been completely removed."
        )

    # 1. Extract real satellite pixels from Earth Engine
    raw_df = sample_satellite_bands(request.lat, request.lon, request.radius)
    if raw_df is None or raw_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No satellite imagery available for coordinates ({request.lat}, {request.lon}) within {request.radius}m radius in the orbital catalog. Adjust target coordinates or expand scanning radius."
        )

    # 2. Engineer spectral features and physics indices from real satellite bands
    features_df = engineer_features(raw_df)

    # 3. Neural network prediction / NNLS physical decomposition
    inference_result = run_model_inference(features_df)

    return {
        "status": "success",
        "total_clusters": inference_result["total_clusters"],
        "data": inference_result["data"],
        "metrics": inference_result["metrics"],
        "breakdown": inference_result.get("breakdown", []),
        "summary": inference_result.get("summary", {}),
        "intelligence": {
            "zone_type": context_profile,
            "expected_materials": materials_expected,
            "base_value_per_ton": base_value_per_ton
        }
    }

@router.post("/api/analyze")
def generate_analysis(request: GeminiRequest) -> Dict[str, Any]:
    """Generates ocean cleanup intelligence via Gemini model."""
    fdi = request.fdi if request.fdi != 0.0 else request.rsi
    return analyze_marine_zone(
        zone_type=request.zone_type,
        materials=request.materials,
        rsi=request.rsi,
        fdi=fdi,
        waste_pct=request.waste_pct
    )
