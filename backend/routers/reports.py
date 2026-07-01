from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from auth import get_current_user
from db import get_db
from diff import SnapshotView, diff_snapshots
from gemini import _norm
from models import AuditSnapshot, Business, SnapshotStatus, User
from schemas import DiffResponse
router = APIRouter(prefix="/api/reports", tags=["reports"])
def _to_view(snapshot: AuditSnapshot, target_name: str) -> SnapshotView:
    target = _norm(target_name)
    competitors = [
        b for b in (snapshot.businesses_mentioned or [])
        if _norm(b) != target and target not in _norm(b)
    ]
    return SnapshotView(
        ran_at=snapshot.ran_at,
        mentioned=snapshot.position is not None,
        position=snapshot.position,
        competitors=competitors,
    )
@router.get("/{business_id}/diff", response_model=DiffResponse)
def get_diff(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DiffResponse:
    biz = db.get(Business, business_id)
    if not biz or biz.user_id != user.id:
        raise HTTPException(status_code=404, detail="Business not found")
    snaps = db.scalars(
        select(AuditSnapshot)
        .where(
            AuditSnapshot.business_id == business_id,
            AuditSnapshot.status == SnapshotStatus.ok,
        )
        .order_by(AuditSnapshot.ran_at.desc())
        .limit(2)
    ).all()
    if not snaps:
        return DiffResponse(has_previous=False, summary="No successful checks yet.")
    current = _to_view(snaps[0], biz.name)
    previous = _to_view(snaps[1], biz.name) if len(snaps) > 1 else None
    result = diff_snapshots(current, previous)
    return DiffResponse(**result.__dict__)