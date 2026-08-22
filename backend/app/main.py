import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.db.session import init_db
from app.api.routes import router as api_router

# Initialize database tables
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Canonical Medical Record Structuring Pipeline - HL7 FHIR R4, Terminology Normalization & Review Queue"
)

# CORS middleware
raw_origins = settings.ALLOWED_ORIGINS
if isinstance(raw_origins, (list, tuple)):
    origins = [str(o).strip() for o in raw_origins if str(o).strip()]
else:
    origins = [orig.strip() for orig in str(raw_origins).split(",") if orig.strip()]

# Ensure Vercel production domain is always present
if "https://canonical-clinical-intelligence.vercel.app" not in origins and "*" not in origins:
    origins.append("https://canonical-clinical-intelligence.vercel.app")

if not origins or "*" in origins:
    allow_origins = ["*"]
    allow_credentials = False
else:
    allow_origins = origins
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"https://canonical-clinical-intelligence.*\.vercel\.app|https://.*\.vercel\.app",
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_PREFIX)

# Static Frontend Mounts
frontend_dir = settings.BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    css_dir = frontend_dir / "css"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    js_dir = frontend_dir / "js"
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

@app.get("/")
def read_root():
    index_file = settings.BASE_DIR / "frontend" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "message": "Canonical Medical Record Structuring Pipeline API",
        "docs_url": "/docs",
        "version": settings.VERSION
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION}
