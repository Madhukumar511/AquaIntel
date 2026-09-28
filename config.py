import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
EE_PROJECT = os.getenv("EE_PROJECT_ID", "mythical-runner-479015-f2")

# ASTER Sensor Satellite Bands (VNIR & SWIR)
BANDS = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08']
FEATURE_COLS_10 = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'NDVI', 'Brightness']

# Physical band center wavelengths in nanometers (for scientific spectral index computation)
BAND_WAVELENGTHS = {
    'B01': {'name': 'Green', 'center_nm': 560, 'region': 'VNIR'},
    'B02': {'name': 'Red', 'center_nm': 660, 'region': 'VNIR'},
    'B3N': {'name': 'Near-Infrared (NIR)', 'center_nm': 807, 'region': 'VNIR'},
    'B04': {'name': 'Shortwave-IR 1 (SWIR1)', 'center_nm': 1650, 'region': 'SWIR'},
    'B05': {'name': 'Shortwave-IR 2 (SWIR2)', 'center_nm': 2165, 'region': 'SWIR'},
    'B06': {'name': 'Shortwave-IR 3 (SWIR3)', 'center_nm': 2205, 'region': 'SWIR'},
    'B07': {'name': 'Shortwave-IR 4 (SWIR4)', 'center_nm': 2260, 'region': 'SWIR'},
    'B08': {'name': 'Shortwave-IR 5 (SWIR5)', 'center_nm': 2330, 'region': 'SWIR'},
}

# Spectral Classes recognized by neural network
CLASS_MAP = {
    0: "Marine Debris / Plastic",
    1: "Ocean Water",
    2: "Organic / Algae Blooms"
}

# 8 Granular High-Precision Constituent Categories
PRECISE_CONSTITUENTS = [
    {"id": "pet_bottles", "name": "PET Bottles & Packaging Films", "short": "PET", "color": "#ff3333", "category": "plastic"},
    {"id": "hdpe_rigid", "name": "HDPE/PP Rigid Marine Crates", "short": "HDPE", "color": "#ff7700", "category": "plastic"},
    {"id": "nylon_nets", "name": "Nylon-6 Ghost Fishing Gear", "short": "NYLON", "color": "#ffaa00", "category": "plastic"},
    {"id": "microplastics", "name": "Microplastic Slick Residue (<5mm)", "short": "MICRO", "color": "#ffdd00", "category": "plastic"},
    {"id": "oil_sheen", "name": "Hydrocarbon Oil Sheens", "short": "OIL", "color": "#cc66ff", "category": "chemical"},
    {"id": "minerals", "name": "Suspended Marine Minerals & Salts", "short": "MINERALS", "color": "#00d4ff", "category": "mineral"},
    {"id": "sargassum", "name": "Organic Sargassum & Algae", "short": "ALGAE", "color": "#00ff88", "category": "organic"},
    {"id": "water", "name": "Pure Deep Ocean Water", "short": "WATER", "color": "#0055ff", "category": "water"}
]

# Global Preset High-Impact Marine Zones
GLOBAL_PRESET_ZONES = [
    {
        "id": "pacific_garbage_patch",
        "name": "Great Pacific Garbage Patch",
        "lat": 35.00,
        "lon": -135.00,
        "radius": 5000,
        "class_type": "Debris / Microplastics",
        "description": "Dense accumulation zone of ocean plastics in the North Pacific Gyre."
    },
    {
        "id": "port_of_la",
        "name": "Port of Los Angeles",
        "lat": 33.73,
        "lon": -118.25,
        "radius": 4000,
        "class_type": "Urban / Industrial Runoff",
        "description": "High-traffic commercial maritime shipping and port facilities."
    },
    {
        "id": "manila_bay",
        "name": "Manila Bay Coast",
        "lat": 14.50,
        "lon": 120.98,
        "radius": 4500,
        "class_type": "Coastal Plastic Waste",
        "description": "Densely populated coastal basin with high synthetic plastic concentrations."
    },
    {
        "id": "great_barrier_reef",
        "name": "Great Barrier Reef",
        "lat": -15.00,
        "lon": 145.00,
        "radius": 5000,
        "class_type": "Coral & Algal Blooms",
        "description": "Marine ecosystem with seasonal organic phytoplankton and algae activity."
    },
    {
        "id": "deep_pacific",
        "name": "Deep Pacific Open Ocean",
        "lat": 20.00,
        "lon": -155.00,
        "radius": 5000,
        "class_type": "Clear Ocean Water",
        "description": "Pristine oligotrophic oceanic reference waters with minimal surface debris."
    }
]
