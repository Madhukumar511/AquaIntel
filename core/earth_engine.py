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
    logger.warning("earthengine-api library not installed. Running in simulation mode.")

def sample_satellite_bands(lat: float, lon: float, radius: int) -> Optional[pd.DataFrame]:
    """
    Samples multispectral bands from the ASTER AST_L1T_003 collection for a given coordinate ROI.
    Returns DataFrame with [lon, lat, B01..B08] or None if unauthenticated / unavailable.
    """
    if not EE_CONNECTED or ee is None:
        return None

    try:
        roi = ee.Geometry.Point([lon, lat]).buffer(radius)
        aster = (
            ee.ImageCollection("ASTER/AST_L1T_003")
            .filterBounds(roi)
            .filterDate('2000-01-01', '2007-12-31')
            .median()
            .select(BANDS)
        )

        dynamic_scale = max(30, int(radius / 15))
        raw_data = aster.sample(region=roi, scale=dynamic_scale, numPixels=4900, geometries=True).getInfo()

        if not raw_data or 'features' not in raw_data or len(raw_data['features']) == 0:
            return None

        rows = []
        for f in raw_data['features']:
            props = f.get('properties', {})
            if all(b in props for b in BANDS):
                coords = f['geometry']['coordinates']
                rows.append([coords[0], coords[1]] + [props[b] for b in BANDS])

        if not rows:
            return None

        return pd.DataFrame(rows, columns=['lon', 'lat'] + BANDS)
    except Exception as e:
        logger.error(f"Error extracting satellite pixels from Earth Engine: {e}")
        return None
