"""Answerspot API — FastAPI application entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db import init_db
from routers import audit, auth, billing, businesses, dashboard, reports
from scheduler import shutdown_scheduler, start_scheduler

logging.basicConfig(level=logging.INFO)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(title="Answerspot API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audit.router)
app.include_router(auth.router)
app.include_router(businesses.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(billing.router)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "gemini_configured": settings.gemini_configured,
        "stripe_configured": settings.stripe_configured,
        "google_oauth_configured": settings.google_oauth_configured,
    }
