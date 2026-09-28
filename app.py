"""AquaIntel AI Global Core — FastAPI Application Entrypoint."""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from config import BASE_DIR, BANDS, FEATURE_COLS_10, GLOBAL_PRESET_ZONES
from routes.api import router as api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AquaIntel")

app = FastAPI(
    title="AquaIntel Global Core",
    description="Multispectral Satellite Marine Debris & Water Quality Detection AI",
    version="2.1.0",
)

# CORS middleware for cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Mount modular static assets (CSS, JS)
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Register modular API routes
app.include_router(api_router)

@app.get("/")
def serve_index():
    """Serves the primary tactical marine dashboard."""
    index_file = BASE_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({"status": "online", "service": "AquaIntel Global Core"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)