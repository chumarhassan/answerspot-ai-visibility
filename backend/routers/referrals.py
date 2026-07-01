from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from auth import get_current_user
from db import get_db
from models import User
from pydantic import BaseModel
router = APIRouter(prefix="/api/referrals", tags=["referrals"])
class ReferralStats(BaseModel):
    code: str
    count: int
    reward_eligible: bool
@router.get("/stats", response_model=ReferralStats)
def get_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ReferralStats:
    count = db.scalar(
        select(func.count(User.id)).where(User.referred_by_id == user.id)
    ) or 0
    return ReferralStats(
        code=user.referral_code or "N/A",
        count=count,
        reward_eligible=count >= 3
    )