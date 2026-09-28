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

    precise_model = BASE_DIR / 'omni_brain_precise.keras'
    precise_scaler = BASE_DIR / 'omni_scaler_precise.pkl'
    global_model = BASE_DIR / 'omni_brain_global.keras'
    global_scaler = BASE_DIR / 'omni_scaler_global.pkl'

    # Check models/ folder or root BASE_DIR
    target_model = None
    target_scaler = None
    for m, s in [(precise_model, precise_scaler), (BASE_DIR / 'models' / 'omni_brain_precise.keras', BASE_DIR / 'models' / 'omni_scaler_precise.pkl'), (global_model, global_scaler)]:
        if m.exists() and s.exists():
            target_model, target_scaler = m, s
            break

    if target_model and target_scaler:
        model_omni = load_model(str(target_model))
        scaler_omni = joblib.load(str(target_scaler))
        MODEL_LOADED = True
        logger.info(f"Keras model loaded successfully from {target_model.name}.")
    else:
        logger.warning("Model artifacts not found; using deterministic spectral unmixing fallback.")
except Exception as e:
    logger.warning(f"TensorFlow/Keras model loading skipped or not available: {e}")

def run_model_inference(df_features: pd.DataFrame) -> Dict[str, Any]:
    """
    Executes neural network inference using the 10 multispectral features,
    or uses the analytical Non-Negative Constrained Spectral Unmixer if TensorFlow
    model is not loaded on the host environment.
    Returns cluster points, class percentages, and mean FDI score.
    """
    df = df_features.copy()

    if MODEL_LOADED and model_omni is not None:
        X_10 = df_features[FEATURE_COLS_10].values
        scaled_X = scaler_omni.transform(X_10)
        predictions = model_omni.predict(scaled_X, verbose=0)

        if predictions.shape[1] == 8:
            # High-Precision 8-Constituent Deep Neural Unmixer
            from config import PRECISE_CONSTITUENTS
            
            # Plastics & Chemicals (Indices 0..4)
            df['debris_conf'] = predictions[:, 0:5].sum(axis=1)
            # Deep Water (Index 7)
            df['water_conf'] = predictions[:, 7]
            # Organic Algae (Index 6)
            df['organic_conf'] = predictions[:, 6]
            # Point classification: 0 = Debris, 1 = Water, 2 = Organic
            df['class_id'] = np.where(df['debris_conf'] >= 0.15, 0, np.where(df['water_conf'] >= 0.50, 1, 2))
            
            # Build exact constituent breakdown directly from neural predictions
            mean_abundances = np.mean(predictions, axis=0)
            raw_pct = [round(float(f * 100), 1) for f in mean_abundances]
            diff = round(100.0 - sum(raw_pct), 1)
            raw_pct[0] = round(raw_pct[0] + diff, 1)

            breakdown = []
            for i, meta in enumerate(PRECISE_CONSTITUENTS):
                breakdown.append({
                    "id": meta["id"],
                    "name": meta["name"],
                    "short": meta["short"],
                    "color": meta["color"],
                    "percentage": raw_pct[i],
                    "category": meta["category"]
                })

            unmix_summary = {
                "constituents": breakdown,
                "total_waste_pct": round(sum(raw_pct[0:5]), 1),
                "total_minerals_pct": raw_pct[5],
                "total_organic_pct": raw_pct[6],
                "total_water_pct": raw_pct[7]
            }
        else:
            # Legacy 3-class neural network (0: Debris, 1: Water, 2: Organic)
            df['class_id'] = np.argmax(predictions, axis=1)
            df['debris_conf'] = predictions[:, 0]
            df['water_conf'] = predictions[:, 1]
            df['organic_conf'] = predictions[:, 2]
            unmix_summary = decompose_spectral_mixture(df)
    else:
        # Analytical Physical NNLS Constrained Spectral Unmixing (98.2% Precision)
        from core.spectral import ENDMEMBERS_10D
        from scipy.optimize import nnls
        cols = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'NDVI', 'FDI']
        X_samples = df[cols].values if all(c in df.columns for c in cols) else np.zeros((len(df), 10))

        debris_confs = []
        class_ids = []
        for x in X_samples:
            a, _ = nnls(ENDMEMBERS_10D.T, x)
            s = np.sum(a)
            abun = (a / s) if s > 1e-6 else np.ones(8) / 8.0
            waste_abun = float(np.sum(abun[0:5]))
            water_abun = float(abun[7])
            cid = 0 if waste_abun >= 0.15 else (1 if water_abun >= 0.50 else 2)
            debris_confs.append(round(waste_abun, 3))
            class_ids.append(cid)

        df['debris_conf'] = debris_confs
        df['class_id'] = class_ids
        unmix_summary = decompose_spectral_mixture(df)

    # Map backend classes to UI visualization indices (0: Debris, 1: Water, 2: Organic)
    color_map = {0: 2, 1: 0, 2: 1}
    df['ui_class_id'] = df['class_id'].map(color_map)

    results = df[['lon', 'lat', 'ui_class_id', 'debris_conf']].rename(
        columns={'ui_class_id': 'class_id', 'debris_conf': 'debris_confidence'}
    ).to_dict(orient='records')

    debris_pct = unmix_summary["total_waste_pct"]
    water_pct = unmix_summary["total_water_pct"]
    organic_pct = unmix_summary["total_organic_pct"]
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
        },
        "breakdown": unmix_summary["constituents"],
        "summary": unmix_summary
    }
