from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import audit as audit_service
from db import get_db
from gemini import build_audit_query
from models import SnapshotStatus
from schemas import AuditRequest, AuditResponse, TeaserIssue
from security import RateLimit
router = APIRouter(prefix="/api/audit", tags=["audit"])
_audit_limit = RateLimit("audit", limit=5, window=60)
@router.post("", response_model=AuditResponse, dependencies=[Depends(_audit_limit)])
async def run_free_audit(payload: AuditRequest, db: Session = Depends(get_db)) -> AuditResponse:
    snapshot = await audit_service.run_free_audit(db, payload.name, payload.category, payload.city)
    result = audit_service.CheckResult(
        status=snapshot.status,
        raw=snapshot.raw_response,
        businesses=snapshot.businesses_mentioned or [],
        mentioned=snapshot.position is not None,
        position=snapshot.position,
        error=snapshot.error,
    )
    competitors = audit_service.competitors_from(
        result, payload.name, limit=audit_service.MAX_TEASER_COMPETITORS
    )
    issues = audit_service.teaser_issues(result, competitors)
    return AuditResponse(
        snapshot_id=snapshot.id,
        status=snapshot.status,
        mentioned=snapshot.position is not None,
        position=snapshot.position,
        competitors=competitors,
        teaser_issues=[TeaserIssue(**i) for i in issues],
        query_text=snapshot.query_text or build_audit_query(payload.category, payload.city),
        error=snapshot.error if snapshot.status == SnapshotStatus.failed else None,
    )