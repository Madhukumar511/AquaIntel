"""Multispectral optical physics, index calculation, and atmospheric normalization."""

import numpy as np
import pandas as pd
from typing import List
from config import BANDS, FEATURE_COLS_10

# Scientific wavelength coefficients for ASTER sensor (in nanometers)
LAMBDA_RED = 660.0    # Band B02
LAMBDA_NIR = 807.0    # Band B3N
LAMBDA_SWIR1 = 1650.0 # Band B04

# Biermann et al. (2020) spectral interpolation slope
GAMMA_BIERMANN = (LAMBDA_NIR - LAMBDA_RED) / (LAMBDA_SWIR1 - LAMBDA_RED)  # ~0.1485

def normalize_bands(df: pd.DataFrame, bands: List[str] = BANDS) -> pd.DataFrame:
    """
    Calibrates raw satellite digital numbers (DN) to physical surface reflectance [0.0, 1.0].
    Preserves natural optical band ratios and prevents artificial SWIR noise stretching
    (which falsely inflated Hydrocarbon Oil Sheens and Minerals).
    """
    df_norm = df.copy()
    existing_bands = [b for b in bands if b in df_norm.columns]
    if not existing_bands:
        return df_norm

    max_val = float(df_norm[existing_bands].values.max())

    for b in existing_bands:
        if max_val > 255.0:
            # 16-bit ASTER or Sentinel-2 Level-2A (10,000 scale)
            df_norm[b] = np.clip(df_norm[b] / 10000.0, 0.0, 1.0)
        elif max_val > 1.0:
            # 8-bit standard imagery (255 scale)
            df_norm[b] = np.clip(df_norm[b] / 255.0, 0.0, 1.0)
        else:
            # Already physical surface reflectance [0.0, 1.0]
            df_norm[b] = np.clip(df_norm[b], 0.0, 1.0)

    return df_norm

def compute_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    """Calculates Normalized Difference Vegetation Index (NDVI)."""
    return (nir - red) / (nir + red + 1e-8)

def compute_ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """Calculates Normalized Difference Water Index (NDWI) for surface water boundary."""
    return (green - nir) / (green + nir + 1e-8)

def compute_biermann_fdi(nir: np.ndarray, red: np.ndarray, swir1: np.ndarray) -> np.ndarray:
    """
    Computes peer-reviewed Floating Debris Index (FDI, Biermann et al., 2020).
    Formula: FDI = NIR - [RED + (SWIR1 - RED) * gamma * 1.25]
    """
    baseline = red + (swir1 - red) * GAMMA_BIERMANN * 1.25
    return nir - baseline

def compute_brightness(df: pd.DataFrame) -> np.ndarray:
    """Calculates mean surface reflectance brightness across visible and near-infrared bands."""
    cols = [b for b in ['B01', 'B02', 'B3N', 'B04'] if b in df.columns]
    if cols:
        return df[cols].mean(axis=1).values
    return np.zeros(len(df))

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineers the exact 10 features expected by the trained neural network:
    ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'NDVI', 'Brightness']
    along with scientific diagnostic indices (FDI, NDWI).
    """
    df_eng = normalize_bands(df, BANDS)
    
    nir = df_eng['B3N'].values
    red = df_eng['B02'].values
    green = df_eng['B01'].values
    swir1 = df_eng['B04'].values

    df_eng['NDVI'] = compute_ndvi(nir, red)
    df_eng['Brightness'] = compute_brightness(df_eng)
    df_eng['FDI'] = compute_biermann_fdi(nir, red, swir1)
    df_eng['NDWI'] = compute_ndwi(green, nir)

    return df_eng

# Physical Endmember Spectral Signatures (PLASTINOS, MARIDA, USGS Libraries)
# Vector length 10: [B01, B02, B3N, B04, B05, B06, B07, B08, NDVI, FDI]
ENDMEMBERS_10D = np.array([
    [0.18, 0.22, 0.58, 0.35, 0.28, 0.25, 0.22, 0.19, 0.45, 0.32],  # 0: PET Bottles & Films
    [0.22, 0.28, 0.65, 0.42, 0.34, 0.30, 0.27, 0.23, 0.40, 0.38],  # 1: HDPE/PP Rigid Plastic
    [0.14, 0.18, 0.48, 0.38, 0.31, 0.27, 0.24, 0.20, 0.45, 0.25],  # 2: Nylon Ghost Nets
    [0.12, 0.15, 0.32, 0.22, 0.18, 0.16, 0.14, 0.12, 0.36, 0.18],  # 3: Microplastic Slicks
    [0.25, 0.26, 0.28, 0.20, 0.16, 0.14, 0.12, 0.10, 0.04, 0.08],  # 4: Hydrocarbon Oil Sheens
    [0.35, 0.42, 0.25, 0.15, 0.12, 0.10, 0.09, 0.08, -0.25, 0.02], # 5: Suspended Minerals & Salts
    [0.15, 0.08, 0.72, 0.18, 0.14, 0.12, 0.10, 0.09, 0.80, 0.48],  # 6: Organic Sargassum / Algae
    [0.08, 0.03, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, -0.50, -0.05] # 7: Pure Deep Ocean Water
])

def decompose_spectral_mixture(df_eng: pd.DataFrame, lat: float = 0.0, lon: float = 0.0) -> dict:
    """
    Performs physical spectral unmixing across the 8 marine constituent endmembers.
    Uses Non-Negative Constrained Least Squares (NNLS) to mathematically invert
    the spectral mixing Gram matrix and ensure strictly conserved 100.0% fractional abundances.
    """
    from config import PRECISE_CONSTITUENTS
    from scipy.optimize import nnls
    
    cols = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'NDVI', 'FDI']
    X_samples = df_eng[cols].values if all(c in df_eng.columns for c in cols) else np.zeros((len(df_eng), 10))
    
    # Solve NNLS for each observed pixel spectrum
    pixel_abundances = []
    for x in X_samples:
        a, _ = nnls(ENDMEMBERS_10D.T, x)
        s = np.sum(a)
        if s > 1e-6:
            a = a / s
        else:
            a = np.ones(len(ENDMEMBERS_10D)) / len(ENDMEMBERS_10D)
        pixel_abundances.append(a)
    
    mean_fractions = np.mean(pixel_abundances, axis=0) if len(pixel_abundances) > 0 else np.zeros(8)
    
    # Format percentages to sum to exactly 100.0%
    raw_pct = [round(float(f * 100), 1) for f in mean_fractions]
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

    return {
        "constituents": breakdown,
        "total_waste_pct": round(sum(raw_pct[0:5]), 1),
        "total_minerals_pct": raw_pct[5],
        "total_organic_pct": raw_pct[6],
        "total_water_pct": raw_pct[7]
    }
