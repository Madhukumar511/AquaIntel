"""Deep Neural Network inference and deterministic fallback simulator."""

import math
import logging
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from config import BASE_DIR, FEATURE_COLS_10
from core.spectral import decompose_spectral_mixture

logger = logging.getLogger("AquaIntel.Model")

MODEL_LOADED = False
model_omni = None
scaler_omni = None

try:
    import joblib
    from tensorflow.keras.models import load_model

    model_path = BASE_DIR / 'omni_brain_global.keras'
    scaler_path = BASE_DIR / 'omni_scaler_global.pkl'

    if model_path.exists() and scaler_path.exists():
        model_omni = load_model(str(model_path))
        scaler_omni = joblib.load(str(scaler_path))
        MODEL_LOADED = True
        logger.info("Omni-Brain Keras model and Scaler loaded successfully.")
    else:
        logger.warning(f"Model artifacts not found at {model_path} or {scaler_path}")
except Exception as e:
    logger.warning(f"TensorFlow/Keras model loading skipped or not available: {e}")

def run_model_inference(df_features: pd.DataFrame) -> Dict[str, Any]:
    """
    Executes neural network inference using the 10 multispectral features.
    Returns cluster points, class percentages, and mean FDI score.
    """
    if not MODEL_LOADED:
        raise RuntimeError("Model is not loaded.")

    X_10 = df_features[FEATURE_COLS_10].values
    scaled_X = scaler_omni.transform(X_10)
    predictions = model_omni.predict(scaled_X, verbose=0)

    df = df_features.copy()
    df['class_id'] = np.argmax(predictions, axis=1)
    df['debris_conf'] = predictions[:, 0]
    df['water_conf'] = predictions[:, 1]
    df['organic_conf'] = predictions[:, 2]

    # Map backend classes to UI visualization indices (0: Debris, 1: Water, 2: Organic)
    color_map = {0: 2, 1: 0, 2: 1}
    df['ui_class_id'] = df['class_id'].map(color_map)

    results = df[['lon', 'lat', 'ui_class_id', 'debris_conf']].rename(
        columns={'ui_class_id': 'class_id', 'debris_conf': 'debris_confidence'}
    ).to_dict(orient='records')

    debris_pct = round(float(df['debris_conf'].mean() * 100), 1)
    water_pct = round(float(df['water_conf'].mean() * 100), 1)
    organic_pct = round(float(df['organic_conf'].mean() * 100), 1)
    fdi_score = round(float(df['FDI'].mean()), 3) if 'FDI' in df.columns else round(float(df['debris_conf'].mean() * 0.4), 3)

    unmix_summary = decompose_spectral_mixture(df)

    return {
        "total_clusters": int(len(df[df['class_id'] == 0])),
        "data": results,
        "metrics": {
            "avg_metal": debris_pct,
            "avg_city": water_pct,
            "avg_minerals": organic_pct,
            "rsi_score": fdi_score,
            "fdi_score": fdi_score,
            "Marine Debris (%)": debris_pct,
            "Ocean Water (%)": water_pct,
            "Organic Algae (%)": organic_pct
        },
        "breakdown": unmix_summary["constituents"],
        "summary": unmix_summary
    }

def generate_simulation_scan(lat: float, lon: float, radius: int) -> Dict[str, Any]:
    """
    Generates realistic, physically plausible multispectral scan results
    when Earth Engine is unauthenticated or in offline demonstration mode.
    """
    num_pts = 35
    points = []
    synthetic_rows = []
    
    # Deterministic seed based on coordinates so the same spot gives consistent results
    coord_seed = int((abs(lat) * 1000 + abs(lon) * 1000)) % 10000
    np.random.seed(coord_seed)

    # Coordinate-aware regional bias (e.g. Pacific gyre vs coast vs deep sea)
    is_gyre = (30 <= lat <= 40 and -145 <= lon <= -125)  # Pacific Garbage Patch area
    is_coastal = (abs(lat) < 35 and (100 <= lon <= 130 or -125 <= lon <= -70))

    for i in range(num_pts):
        angle = (2 * math.pi / num_pts) * i
        dist = (radius * 0.65) * (0.3 + 0.7 * ((i % 5) / 5.0))
        d_lat = (dist / 111320.0) * math.cos(angle)
        d_lon = (dist / (111320.0 * math.cos(math.radians(lat)))) * math.sin(angle)

        cid = 0 if (is_gyre and i % 2 == 0) else (0 if i % 4 == 0 else (1 if i % 2 == 0 else 2))
        conf = 0.88 if cid == 0 else (0.94 if cid == 1 else 0.81)

        pt_lon = round(lon + d_lon, 6)
        pt_lat = round(lat + d_lat, 6)
        points.append({
            "lon": pt_lon,
            "lat": pt_lat,
            "class_id": cid,
            "debris_confidence": conf
        })

        # Synthesize 10 spectral features corresponding to this point
        if cid == 0:  # Plastic cluster
            row = [0.20, 0.24, 0.60, 0.38, 0.30, 0.26, 0.23, 0.20, 0.42, 0.35]
        elif cid == 1:  # Water
            row = [0.09, 0.04, 0.02, 0.01, 0.01, 0.01, 0.00, 0.00, -0.45, -0.04]
        else:  # Organic / Algae / Minerals
            row = [0.18, 0.12, 0.55, 0.20, 0.15, 0.12, 0.10, 0.09, 0.65, 0.28]
        synthetic_rows.append(row)

    cols = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'NDVI', 'FDI']
    synth_df = pd.DataFrame(synthetic_rows, columns=cols)
    unmix_res = decompose_spectral_mixture(synth_df, lat, lon)

    debris_pct = unmix_res["total_waste_pct"]
    water_pct = unmix_res["total_water_pct"]
    organic_pct = unmix_res["total_organic_pct"]
    fdi_score = round(float(synth_df['FDI'].mean()), 3)

    return {
        "status": "success",
        "total_clusters": len([p for p in points if p["class_id"] == 0]),
        "data": points,
        "metrics": {
            "avg_metal": debris_pct,
            "avg_city": water_pct,
            "avg_minerals": organic_pct,
            "rsi_score": fdi_score,
            "fdi_score": fdi_score,
            "Marine Debris (%)": debris_pct,
            "Ocean Water (%)": water_pct,
            "Organic Algae (%)": organic_pct
        },
        "breakdown": unmix_res["constituents"],
        "summary": unmix_res,
        "intelligence": {
            "zone_type": "Global Marine Environment",
            "expected_materials": "PET Bottles, HDPE Crates, Ghost Nets, Microplastics, Oil Sheens, Minerals",
            "base_value_per_ton": 250
        }
    }
