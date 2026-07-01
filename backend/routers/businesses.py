from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
import audit as audit_service
from auth import get_current_user, get_plan
from db import get_db
from models import Business, Plan, User
from schemas import BusinessCreate, BusinessOut, BusinessUpdate
router = APIRouter(prefix="/api/businesses", tags=["businesses"])
def _owned_business(db: Session, user: User, business_id: int) -> Business:
    biz = db.get(Business, business_id)
    if not biz or biz.user_id != user.id:
        raise HTTPException(status_code=404, detail="Business not found")
    return biz
@router.get("", response_model=list[BusinessOut])
def list_businesses(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Business]:
    return db.scalars(select(Business).where(Business.user_id == user.id)).all()
@router.get("/{business_id}", response_model=BusinessOut)
def get_business(
    business_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Business:
    return _owned_business(db, user, business_id)
@router.post("", response_model=BusinessOut, status_code=201)
def create_business(
    payload: BusinessCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:
    plan = get_plan(db, user)
    if plan in (Plan.free, Plan.starter):
        count = db.scalar(select(Business).where(Business.user_id == user.id).limit(1))
        if count is not None:
            raise HTTPException(
                status_code=403,
                detail="Your plan allows a single business. Upgrade to Pro to track more.",
            )
    biz = Business(
        user_id=user.id,
        name=payload.name,
        category=payload.category,
        city=payload.city,
        website=payload.website,
    )
    db.add(biz)
    db.commit()
    db.refresh(biz)
    return biz
@router.patch("/{business_id}", response_model=BusinessOut)
def patch_business(
    business_id: int,
    payload: BusinessUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:
    biz = _owned_business(db, user, business_id)
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(biz, k, v)
    db.commit()
    db.refresh(biz)
    return biz
@router.delete("/{business_id}")
def delete_business(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    biz = _owned_business(db, user, business_id)
    db.delete(biz)
    db.commit()
    return {"deleted": True, "id": business_id}
@router.post("/{business_id}/check", response_model=BusinessOut)
async def run_check(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:
    biz = _owned_business(db, user, business_id)
    await audit_service.run_business_audit(db, biz)
    return biz