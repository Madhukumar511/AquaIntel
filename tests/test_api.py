import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import app, GLOBAL_PRESET_ZONES, BANDS, FEATURE_COLS_10

client = TestClient(app)

def test_root_serves_frontend():
    """Verify that root endpoint serves the web application."""
    response = client.get("/")
    assert response.status_code == 200
    # Should either be the HTML file or JSON fallback
    assert "html" in response.headers.get("content-type", "").lower() or "application/json" in response.headers.get("content-type", "").lower()

def test_health_check_endpoint():
    """Verify health status returns ok and reports subsystem states."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data
    assert "earth_engine_connected" in data
    assert "supported_classes" in data
    assert data["feature_bands"] == BANDS

def test_presets_endpoint():
    """Verify marine preset zones are loaded properly."""
    response = client.get("/api/presets")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["zones"]) >= 4
    # Check Great Pacific Garbage Patch exists
    zone_ids = [z["id"] for z in data["zones"]]
    assert "pacific_garbage_patch" in zone_ids
    assert "manila_bay" in zone_ids

def test_model_info_endpoint():
    """Verify model architecture metadata and band specifications."""
    response = client.get("/api/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "architecture" in data
    assert data["features"] == FEATURE_COLS_10
    assert len(data["bands"]) == 8

def test_scan_coordinate_validation():
    """Verify scan endpoint rejects out-of-bounds latitude and longitude."""
    # Invalid latitude (> 90)
    res_bad_lat = client.post("/api/scan", json={"lat": 120.0, "lon": 50.0, "radius": 1500})
    assert res_bad_lat.status_code == 422  # Pydantic validation error

    # Invalid longitude (> 180)
    res_bad_lon = client.post("/api/scan", json={"lat": 10.0, "lon": 250.0, "radius": 1500})
    assert res_bad_lon.status_code == 422

    # Invalid radius (<= 0)
    res_bad_rad = client.post("/api/scan", json={"lat": 10.0, "lon": 50.0, "radius": -500})
    assert res_bad_rad.status_code == 422

def test_scan_unauthenticated_returns_503_without_simulation():
    """Verify that scan endpoint returns 503 error when Earth Engine is unauthenticated instead of faking a simulation."""
    from unittest.mock import patch
    with patch("routes.api.EE_CONNECTED", False):
        res = client.post("/api/scan", json={"lat": 35.0, "lon": -135.0, "radius": 2000})
        assert res.status_code == 503
        assert "Simulation mode has been completely removed" in res.json()["detail"]

def test_scan_valid_request():
    """Verify scan returns valid data points and 8-constituent metrics when real satellite bands are supplied."""
    import pandas as pd
    from unittest.mock import patch
    mock_satellite_data = pd.DataFrame({
        "lon": [-135.001, -135.002, -135.003],
        "lat": [35.001, 35.002, 35.003],
        "B01": [1200.0, 1100.0, 1150.0],
        "B02": [1050.0, 950.0, 1000.0],
        "B3N": [2400.0, 2100.0, 2300.0],
        "B04": [800.0, 750.0, 780.0],
        "B05": [600.0, 580.0, 590.0],
        "B06": [500.0, 480.0, 490.0],
        "B07": [400.0, 390.0, 395.0],
        "B08": [300.0, 290.0, 295.0],
    })
    with patch("routes.api.EE_CONNECTED", True), \
         patch("routes.api.sample_satellite_bands", return_value=mock_satellite_data):
        response = client.post("/api/scan", json={"lat": 35.00, "lon": -135.00, "radius": 2000})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "metrics" in data
        assert "breakdown" in data
        assert len(data["breakdown"]) == 8
        assert len(data["data"]) == 3
        first_point = data["data"][0]
        assert "lat" in first_point
        assert "lon" in first_point
        assert "class_id" in first_point

def test_analyze_gemini_endpoint():
    """Verify automated AI environmental report generation."""
    payload = {
        "zone_type": "Pacific Garbage Patch",
        "materials": "Microplastics, Floating Debris",
        "rsi": 0.42,
        "fdi": 0.31,
        "waste_pct": 42.5
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "insight" in data
    assert "minerals_breakdown" in data
    assert "recommendation" in data
    assert len(data["insight"]) > 10

def test_spectral_bands_endpoint():
    """Verify satellite sensor band metadata endpoint."""
    response = client.get("/api/spectral/bands")
    assert response.status_code == 200
    data = response.json()
    assert "sensor" in data
    assert "bands" in data
    assert "B01" in data["bands"]
    assert "B3N" in data["bands"]

def test_static_assets_served():
    """Verify CSS and JS modular assets are served with HTTP 200."""
    css_res = client.get("/static/css/dashboard.css")
    assert css_res.status_code == 200
    assert "AQUAINTEL" in css_res.text

    js_map = client.get("/static/js/tactical_map.js")
    assert js_map.status_code == 200

    js_scan = client.get("/static/js/scan_controller.js")
    assert js_scan.status_code == 200
