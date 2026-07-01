from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
import audit as audit_service
from auth import get_current_user
from db import get_db
from models import (
    ACTIVE_PLATFORMS,
    Business,
    Competitor,
    FixRecommendation,
    FixStatus,
    Platform,
    SnapshotStatus,
    User,
)
from schemas import (
    BusinessOut,
    CompetitorOut,
    DashboardResponse,
    FixOut,
    PlatformStatus,
)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
@router.get("/{business_id}", response_model=DashboardResponse)
async def get_dashboard(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    biz = db.get(Business, business_id)
    if not biz or biz.user_id != user.id:
        raise HTTPException(status_code=404, detail="Business not found")
    snapshot = audit_service.latest_snapshot(db, business_id)
    has_snapshot = snapshot is not None
    mentioned = bool(snapshot and snapshot.position is not None)
    position = snapshot.position if snapshot else None
    competitors = db.scalars(
        select(Competitor)
        .where(Competitor.business_id == business_id)
        .order_by(Competitor.last_seen_at.desc())
    ).all()
    competitor_names = [c.competitor_name for c in competitors]
    fixes = db.scalars(
        select(FixRecommendation)
        .where(FixRecommendation.business_id == business_id, FixRecommendation.status == FixStatus.open)
        .order_by(FixRecommendation.priority.desc())
    ).all()
    summary = (
        "Run your first check to see how AI assistants represent your business."
        if not has_snapshot
        else "We couldn't complete the last check — it will retry automatically."
        if snapshot.status == SnapshotStatus.failed
        else snapshot.summary_text or audit_service._fallback_summary(biz, mentioned, position, competitor_names)
    )
    platforms = [
        PlatformStatus(platform=p, active=p in ACTIVE_PLATFORMS) for p in Platform
    ]
    return DashboardResponse(
        business=BusinessOut.model_validate(biz),
        has_snapshot=has_snapshot,
        latest_status=snapshot.status if snapshot else None,
        mentioned=mentioned,
        position=position,
        visibility_score=audit_service.visibility_score(mentioned, position, has_snapshot),
        summary=summary,
        competitors=[CompetitorOut.model_validate(c) for c in competitors],
        fixes=[FixOut.model_validate(f) for f in fixes],
        platforms=platforms,
        last_checked=snapshot.ran_at if snapshot else None,
    )