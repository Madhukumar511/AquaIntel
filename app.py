from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ee
import pandas as pd
import numpy as np
import joblib
import requests
import json
from tensorflow.keras.models import load_model

# ---------------------------------------------------------
GEMINI_API_KEY = "AIzaSyBc2xX0asabzIUoPHo8z0JCUQ684LsEA74" 
# ---------------------------------------------------------

app = FastAPI(title="WasteIntel Global Core")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

try:
    ee.Initialize(project='mythical-runner-479015-f2')
    print("✅ Earth Engine Connected")
except:
    ee.Authenticate()
    ee.Initialize(project='mythical-runner-479015-f2')

print("🧠 LOADING GLOBAL OMNI-MODEL...")

try:
    # 🌍 THE NEW SINGLE MASTER BRAIN
    model_omni = load_model('omni_brain_global.keras')
    scaler_omni = joblib.load('omni_scaler_global.pkl')
    print("🚀 OMNI-BRAIN ONLINE AND READY.")
except Exception as e:
    print(f"⚠️ LOAD ERROR: {e}")
    print("Make sure 'omni_brain_global.keras' and 'omni_scaler_global.pkl' are in this folder!")

BANDS = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08']
FEATURE_COLS_10 = ['B01','B02','B3N','B04','B05','B06','B07','B08', 'NDVI', 'Brightness']

class ScanRequest(BaseModel):
    lat: float
    lon: float
    radius: int = 1500

class GeminiRequest(BaseModel):
    zone_type: str
    materials: str
    rsi: float = 0.0 
    fdi: float = 0.0 
    waste_pct: float

@app.post("/api/scan")
def scan_marine_yard(request: ScanRequest):
    context_profile = "Global Marine Environment"
    materials_expected = "Microplastics, Synthetic Nets, General Ocean Debris, Organic Algae"
    base_value_per_ton = 250 
    
    roi = ee.Geometry.Point([request.lon, request.lat]).buffer(request.radius)
    aster = ee.ImageCollection("ASTER/AST_L1T_003").filterBounds(roi).filterDate('2000-01-01', '2007-12-31').median().select(BANDS)
    
    dynamic_scale = max(30, int(request.radius / 15))
    raw_data = aster.sample(region=roi, scale=dynamic_scale, numPixels=4900, geometries=True).getInfo()
    
    if not raw_data or 'features' not in raw_data or len(raw_data['features']) == 0: 
        raise HTTPException(status_code=404, detail="No satellite data found for this specific area.")
    
    rows = []
    for f in raw_data['features']:
        props = f['properties']
        if all(b in props for b in BANDS):
            rows.append([f['geometry']['coordinates'][0], f['geometry']['coordinates'][1]] + [props[b] for b in BANDS])
            
    df = pd.DataFrame(rows, columns=['lon', 'lat'] + BANDS)
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Corrupted satellite tile.")

    # 🛑 ATMOSPHERIC NORMALIZATION (Matches how we trained the Global Model)
    for b in BANDS:
        b_min = df[b].min()
        b_max = df[b].max()
        if b_max > b_min:
            df[b] = (df[b] - b_min) / (b_max - b_min)
        else:
            df[b] = 0.0

    # Core Math Calculation
    df['NDVI'] = (df['B3N'] - df['B02']) / (df['B3N'] + df['B02'] + 1e-8)
    df['Brightness'] = df[['B01','B02','B3N','B04']].mean(axis=1)
    df['FDI_Proxy'] = df['B04'] / (df['B02'] + 1e-8)
    
    # 🧠 SINGLE MODEL PREDICTION (Lightning Fast)
    X_10 = df[FEATURE_COLS_10].values
    predictions = model_omni.predict(scaler_omni.transform(X_10), verbose=0)
    
    df['class_id'] = np.argmax(predictions, axis=1)
    df['debris_conf'] = predictions[:, 0]
    df['water_conf'] = predictions[:, 1]
    df['organic_conf'] = predictions[:, 2]

    # 🎨 THE COLOR ROUTER SYNC (Matches UI hex map colors)
    # 0: BLUE (Water), 1: GREEN (Organic), 2: RED (Debris)
    color_map = {0: 2, 1: 0, 2: 1}
    df['ui_class_id'] = df['class_id'].map(color_map)
    
    results = df[['lon', 'lat', 'ui_class_id', 'debris_conf']].rename(columns={'ui_class_id': 'class_id', 'debris_conf': 'debris_confidence'}).to_dict(orient='records')
    
    # Metrics Sync for Sidebar Bars
    debris_pct = round(df['debris_conf'].mean() * 100, 1)
    water_pct = round(df['water_conf'].mean() * 100, 1)
    organic_pct = round(df['organic_conf'].mean() * 100, 1)
    fdi_score = round(df['FDI_Proxy'].mean() / 2, 3)

    return {
        "status": "success", 
        "total_clusters": len(df[df['class_id'] == 0]), 
        "data": results,
        "metrics": {
            "avg_metal": debris_pct,     # Maps to RED bar in UI
            "avg_city": water_pct,       # Maps to BLUE bar in UI
            "avg_minerals": organic_pct, # Maps to GREEN bar in UI
            "rsi_score": fdi_score,
            "Marine Debris (%)": debris_pct,
            "Ocean Water (%)": water_pct,
            "Organic Algae (%)": organic_pct
        },
        "intelligence": {"zone_type": context_profile, "expected_materials": materials_expected, "base_value_per_ton": base_value_per_ton}
    }

@app.post("/api/analyze")
def generate_gemini_report(req: GeminiRequest):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        prompt = f"""Role: Ocean Cleanup Expert. Data: Zone: {req.zone_type}, Debris: {req.waste_pct}%, FDI: {req.fdi}.
        Return ONLY a JSON object with: "insight", "minerals_breakdown", "recommendation"."""
        
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}}
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
        response_data = response.json()
        
        if not response.ok: return {"insight": "API Error", "minerals_breakdown": "None", "recommendation": "Check Key"}
            
        raw_text = response_data['candidates'][0]['content']['parts'][0]['text']
        clean_text = raw_text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
        
    except Exception as e:
        return {"insight": "Parsing Error", "minerals_breakdown": "• N/A", "recommendation": "Check logs"}