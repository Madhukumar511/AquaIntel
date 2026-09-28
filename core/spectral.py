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
    """Applies atmospheric min-max normalization across all multispectral bands."""
    df_norm = df.copy()
    for b in bands:
        if b in df_norm.columns:
            b_min = df_norm[b].min()
            b_max = df_norm[b].max()
            if b_max > b_min:
                df_norm[b] = (df_norm[b] - b_min) / (b_max - b_min + 1e-8)
            else:
                df_norm[b] = 0.0
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
