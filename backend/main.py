from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from db import init_db
from routers import audit, auth, billing, businesses, dashboard, reports, referrals
from scheduler import shutdown_scheduler, start_scheduler
from security import ContentLengthLimitMiddleware, SecurityHeadersMiddleware
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("answerspot")
settings = get_settings()
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.jwt_secret_is_insecure:
        msg = "JWT_SECRET is insecure — set a strong random secret."
        if settings.is_production:
            raise RuntimeError(msg)
        logger.warning("SECURITY: %s", msg)
    init_db()
    start_scheduler()
    yield
    shutdown_scheduler()
app = FastAPI(title="Answerspot API", version="1.0.0", lifespan=lifespan)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ContentLengthLimitMiddleware, max_bytes=1_048_576)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)
app.include_router(audit.router)
app.include_router(auth.router)
app.include_router(businesses.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(referrals.router)
app.include_router(billing.router)
@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "gemini_configured": settings.gemini_configured,
        "stripe_configured": settings.stripe_configured,
    }