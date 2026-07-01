from __future__ import annotations
from datetime import datetime, timedelta, timezone
import bcrypt
import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from config import get_settings
from db import get_db
from models import Plan, Subscription, User
import uuid
settings = get_settings()
_bearer = HTTPBearer(auto_error=False)
def create_user(
    db: Session,
    email: str,
    password_hash: str | None = None,
    oauth_provider: str | None = None,
    referred_by_code: str | None = None
) -> User:
    ref_code = str(uuid.uuid4())[:8].upper()
    referred_by_id = None
    if referred_by_code:
        referrer = db.scalar(select(User).where(User.referral_code == referred_by_code.upper()))
        if referrer:
            referred_by_id = referrer.id
    user = User(
        email=email,
        password_hash=password_hash,
        oauth_provider=oauth_provider,
        referral_code=ref_code,
        referred_by_id=referred_by_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    ensure_subscription(db, user)
    if referred_by_id:
        _check_referral_reward(db, referred_by_id)
    return user
def _check_referral_reward(db: Session, referrer_id: int) -> None:
    count = db.scalar(
        select(func.count(User.id)).where(User.referred_by_id == referrer_id)
    ) or 0
    if count >= 3:
        sub = ensure_subscription(db, db.get(User, referrer_id))
        if sub.plan == Plan.free:
            sub.plan = Plan.starter
            db.commit()
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False
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
    sub = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if sub is None:
        sub = Subscription(user_id=user.id, plan=Plan.free, status="active")
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub
    return sub