"""Auth endpoints: email/password signup + login, and Google OAuth callback (§10)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

import auth as auth_service
from db import get_db
from models import User
from schemas import LoginRequest, SignupRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _token_response(db: Session, user: User) -> TokenResponse:
    sub = auth_service.ensure_subscription(db, user)
    token = auth_service.create_access_token(user.id)
    return TokenResponse(access_token=token, email=user.email, plan=sub.plan)


@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(
        email=str(payload.email),
        password_hash=auth_service.hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_response(db, user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not user.password_hash or not auth_service.verify_password(
        payload.password, user.password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _token_response(db, user)


class GoogleCallbackRequest(BaseModel):
    code: str


@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(payload: GoogleCallbackRequest, db: Session = Depends(get_db)) -> TokenResponse:
    info = await auth_service.exchange_google_code(payload.code)
    email = info["email"]
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        user = User(email=email, oauth_provider="google")
        db.add(user)
        db.commit()
        db.refresh(user)
    return _token_response(db, user)
