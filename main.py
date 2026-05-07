"""
main.py — FastAPI entry point
Khởi tạo app, mount static files, include API routers.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.services.data_loader import DataLoader
from src.api import phases, data_summary


# ── Lifespan: load data once at startup ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load tất cả CSV vào memory lúc startup để response nhanh."""
    DataLoader.load_all()
    yield
    DataLoader.clear()


# ── App factory ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="POS Audit — Data Mining Report",
    description="HCMUE Data Mining Final Project — CRISP-DM Pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── Static & Templates ───────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ── API routers ──────────────────────────────────────────────────────────────
app.include_router(phases.router,      prefix="/api", tags=["phases"])
app.include_router(data_summary.router, prefix="/api", tags=["data"])


# ── Root route: render SPA ───────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# -> uvicorn main:app --reload