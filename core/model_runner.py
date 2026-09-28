"""Deep Neural Network inference and deterministic fallback simulator."""

import math
import logging
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from config import BASE_DIR, FEATURE_COLS_10

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
        }
    }

def generate_simulation_scan(lat: float, lon: float, radius: int) -> Dict[str, Any]:
    """
    Generates realistic, physically plausible multispectral scan results
    when Earth Engine is unauthenticated or in offline demonstration mode.
    """
    num_pts = 35
    points = []
    
    # Deterministic seed based on coordinates so the same spot gives consistent results
    coord_seed = int((abs(lat) * 1000 + abs(lon) * 1000)) % 10000
    np.random.seed(coord_seed)

    for i in range(num_pts):
        angle = (2 * math.pi / num_pts) * i
        dist = (radius * 0.65) * (0.3 + 0.7 * ((i % 5) / 5.0))
        d_lat = (dist / 111320.0) * math.cos(angle)
        d_lon = (dist / (111320.0 * math.cos(math.radians(lat)))) * math.sin(angle)

        # Distribute classes realistically for ocean scanning
        cid = 0 if i % 4 == 0 else (1 if i % 2 == 0 else 2)
        conf = 0.88 if cid == 0 else (0.94 if cid == 1 else 0.81)

        points.append({
            "lon": round(lon + d_lon, 6),
            "lat": round(lat + d_lat, 6),
            "class_id": cid,
            "debris_confidence": conf
        })

    debris_pct = 28.5
    water_pct = 54.0
    organic_pct = 17.5
    fdi_score = 0.218

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
        "intelligence": {
            "zone_type": "Global Marine Environment",
            "expected_materials": "Microplastics, Synthetic Nets, Ocean Debris, Algae",
            "base_value_per_ton": 250
        }
    }
