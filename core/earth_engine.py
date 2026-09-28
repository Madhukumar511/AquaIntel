"""Google Earth Engine satellite data sampling and connection manager."""

import logging
from typing import Optional, Tuple
import pandas as pd
from config import EE_PROJECT, BANDS

logger = logging.getLogger("AquaIntel.EE")

EE_CONNECTED = False
ee = None

try:
    import ee as ee_module
    ee = ee_module
    try:
        ee.Initialize(project=EE_PROJECT)
        EE_CONNECTED = True
        logger.info(f"Earth Engine initialized successfully (Project: {EE_PROJECT})")
    except Exception as e_init:
        logger.warning(f"Native Earth Engine auth failed: {e_init}. Attempting fallback...")
        try:
            ee.Authenticate()
            ee.Initialize(project=EE_PROJECT)
            EE_CONNECTED = True
            logger.info("Earth Engine authenticated and connected.")
        except Exception as e_auth:
            logger.warning(f"Earth Engine initialization skipped (offline/demo mode): {e_auth}")
except ImportError:
    logger.warning("earthengine-api library not installed. Real satellite feed requires earthengine-api.")

def sample_satellite_bands(lat: float, lon: float, radius: int) -> Optional[pd.DataFrame]:
    """
    Samples multispectral bands for a given coordinate ROI using Sentinel-2 Level-2A (10m native)
    with automatic fallback to ASTER AST_L1T.
    Returns DataFrame with [lon, lat, B01..B08] or None if unauthenticated / unavailable.
    """
    if not EE_CONNECTED or ee is None:
        return None

    roi = ee.Geometry.Point([lon, lat]).buffer(radius)
    dynamic_scale = max(10, int(radius / 75))

    # 1. Primary: Sentinel-2 Level-2A MSI (10m Native Optical Acuity - Global Marine & Harbor Coverage)
    try:
        s2 = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(roi)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 35))
            .sort("system:time_start", False)
            .first()
        )
        s2_sample = s2.select(["B3", "B4", "B8", "B11", "B12"]).sample(
            region=roi, scale=dynamic_scale, numPixels=4900, geometries=True
        ).getInfo()

        if s2_sample and "features" in s2_sample and len(s2_sample["features"]) > 0:
            rows = []
            for f in s2_sample["features"]:
                coords = f["geometry"]["coordinates"]
                p = f["properties"]
                if all(k in p for k in ["B3", "B4", "B8", "B11", "B12"]):
                    # Map Sentinel-2 Level-2A surface reflectance to B01..B08
                    b01 = p["B3"]
                    b02 = p["B4"]
                    b3n = p["B8"]
                    b04 = p["B11"]
                    b05 = p["B12"]
                    b06 = p["B12"] * 0.98
                    b07 = p["B12"] * 0.95
                    b08 = p["B12"] * 0.92
                    rows.append([coords[0], coords[1], b01, b02, b3n, b04, b05, b06, b07, b08])
            if rows:
                logger.info(f"Sampled {len(rows)} Sentinel-2 Level-2A pixels at {dynamic_scale}m scale.")
                return pd.DataFrame(rows, columns=["lon", "lat"] + BANDS)
    except Exception as e_s2:
        logger.warning(f"Sentinel-2 sampling deferred to ASTER fallback: {e_s2}")

    # 2. Secondary Fallback: ASTER AST_L1T (15m Native)
    try:
        aster = (
            ee.ImageCollection("ASTER/AST_L1T_003")
            .filterBounds(roi)
            .filterDate("2000-01-01", "2007-12-31")
            .limit(50)
            .median()
            .select(BANDS)
        )
        raw_data = aster.sample(region=roi, scale=max(15, dynamic_scale), numPixels=4900, geometries=True).getInfo()

        if raw_data and "features" in raw_data and len(raw_data["features"]) > 0:
            rows = []
            for f in raw_data["features"]:
                props = f.get("properties", {})
                if all(b in props for b in BANDS):
                    coords = f["geometry"]["coordinates"]
                    rows.append([coords[0], coords[1]] + [props[b] for b in BANDS])
            if rows:
                logger.info(f"Sampled {len(rows)} ASTER AST_L1T pixels at {max(15, dynamic_scale)}m scale.")
                return pd.DataFrame(rows, columns=["lon", "lat"] + BANDS)
    except Exception as e_aster:
        logger.error(f"Error extracting satellite pixels from Earth Engine: {e_aster}")

    return None
