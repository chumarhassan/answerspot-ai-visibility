"""Authentication: bcrypt password hashing, JWT sessions, Google OAuth exchange.

Both email/password and Google OAuth are supported (§10).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import get_settings
from db import get_db
from models import Plan, Subscription, User

settings = get_settings()
_bearer = HTTPBearer(auto_error=False)


# ── Password hashing ──────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


# ── JWT ───────────────────────────────────────────────────────────────────────
def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expires_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        ) from exc


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = _decode_token(creds.credentials)
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_plan(db: Session, user: User) -> Plan:
    sub = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    return sub.plan if sub else Plan.free


def ensure_subscription(db: Session, user: User) -> Subscription:
    """Every user has a subscription row; default free."""
    sub = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if sub is None:
        sub = Subscription(user_id=user.id, plan=Plan.free, status="active")
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub


# ── Google OAuth ──────────────────────────────────────────────────────────────
async def exchange_google_code(code: str) -> dict:
    """Exchange an OAuth authorization code for the user's Google profile.

    Returns {"email": ...}. Raises HTTPException on failure.
    """
    if not settings.google_oauth_configured:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured on the server")

    async with httpx.AsyncClient(timeout=15.0) as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "redirect_uri": settings.google_oauth_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Google token exchange failed")
        access_token = token_resp.json().get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token from Google")

        info_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if info_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch Google profile")
        profile = info_resp.json()

    email = profile.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")
    return {"email": email}
