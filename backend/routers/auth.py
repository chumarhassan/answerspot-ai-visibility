from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
import auth as auth_service
from db import get_db
from models import Business, User
from schemas import LoginRequest, SignupRequest, TokenResponse
from security import RateLimit
_auth_limit = RateLimit("auth", limit=10, window=60)
router = APIRouter(prefix="/api/auth", tags=["auth"], dependencies=[Depends(_auth_limit)])
def _token_response(db: Session, user: User) -> TokenResponse:
    sub = auth_service.ensure_subscription(db, user)
    token = auth_service.create_access_token(user.id)
    has_biz = db.scalar(select(Business).where(Business.user_id == user.id)) is not None
    return TokenResponse(
        access_token=token, email=user.email, plan=sub.plan, has_business=has_biz
    )
@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = auth_service.create_user(
        db,
        email=str(payload.email),
        password_hash=auth_service.hash_password(payload.password),
        referred_by_code=payload.referral_code
    )
    return _token_response(db, user)
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not user.password_hash or not auth_service.verify_password(
        payload.password, user.password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _token_response(db, user)