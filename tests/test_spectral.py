"""Unit tests for multispectral optical physics calculations and spectral feature engineering."""

import pytest
import numpy as np
import pandas as pd
from core.spectral import (
    normalize_bands,
    compute_ndvi,
    compute_ndwi,
    compute_biermann_fdi,
    compute_brightness,
    engineer_features,
    decompose_spectral_mixture,
    GAMMA_BIERMANN,
)
from config import BANDS, FEATURE_COLS_10

def test_biermann_fdi_formula():
    """Verify Biermann Floating Debris Index math."""
    # Synthetic plastic pixel: high NIR reflectance over red & swir baseline
    nir = np.array([0.45, 0.05])
    red = np.array([0.08, 0.02])
    swir1 = np.array([0.15, 0.01])

    fdi = compute_biermann_fdi(nir, red, swir1)
    
    # Plastic pixel (index 0) should have positive FDI
    assert fdi[0] > 0.2
    # Water pixel (index 1) has negligible or low FDI
    assert fdi[1] < fdi[0]

def test_ndvi_and_ndwi_ranges():
    """Verify NDVI and NDWI calculations."""
    nir = np.array([0.6, 0.1])
    red = np.array([0.1, 0.1])
    green = np.array([0.2, 0.3])

    ndvi = compute_ndvi(nir, red)
    ndwi = compute_ndwi(green, nir)

    # High NIR with low Red = positive vegetative/organic index
    assert ndvi[0] > 0.5
    # High Green with low NIR = positive water index
    assert ndwi[1] > 0.3

def test_feature_engineering_pipeline():
    """Verify that feature engineering creates exact 10 features for the model."""
    raw_data = {
        'lon': [100.0, 100.1],
        'lat': [10.0, 10.1],
        'B01': [1200.0, 1300.0],
        'B02': [1100.0, 1150.0],
        'B3N': [2500.0, 1800.0],
        'B04': [800.0, 900.0],
        'B05': [600.0, 700.0],
        'B06': [500.0, 600.0],
        'B07': [400.0, 500.0],
        'B08': [300.0, 400.0],
    }
    df = pd.DataFrame(raw_data)
    df_eng = engineer_features(df)

    # Check all 10 model features exist
    for col in FEATURE_COLS_10:
        assert col in df_eng.columns

    # Check extra diagnostic indices are present
    assert 'FDI' in df_eng.columns
    assert 'NDWI' in df_eng.columns
    assert 'Brightness' in df_eng.columns

def test_decompose_spectral_mixture():
    """Verify that spectral unmixing decomposes pixels into 8 constituents strictly summing to 100.0%."""
    raw_data = {
        'B01': [1200.0, 1300.0],
        'B02': [1100.0, 1150.0],
        'B3N': [2500.0, 1800.0],
        'B04': [800.0, 900.0],
        'B05': [600.0, 700.0],
        'B06': [500.0, 600.0],
        'B07': [400.0, 500.0],
        'B08': [300.0, 400.0],
    }
    df = pd.DataFrame(raw_data)
    df_eng = engineer_features(df)
    
    result = decompose_spectral_mixture(df_eng)
    
    # Check structure
    assert 'constituents' in result
    assert len(result['constituents']) == 8
    
    # Check percentages sum to exactly 100.0%
    total_pct = round(sum(c['percentage'] for c in result['constituents']), 1)
    assert total_pct == 100.0
    
    # Check category totals match sum of breakdown
    waste_sum = round(sum(c['percentage'] for c in result['constituents'] if c['category'] in ['plastic', 'chemical']), 1)
    assert result['total_waste_pct'] == waste_sum

