from __future__ import annotations
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from db import SessionLocal
from models import AuditSnapshot, Business, User, SnapshotStatus
from diff import diff_snapshots
from routers.reports import _to_view
import emails
logger = logging.getLogger("answerspot.reports")
async def dispatch_weekly_reports() -> None:
    logger.info("Reports: starting weekly dispatch.")
    with SessionLocal() as db:
        users = db.scalars(select(User)).all()
        for user in users:
            businesses = db.scalars(select(Business).where(Business.user_id == user.id)).all()
            for biz in businesses:
                try:
                    await _process_business_report(db, user, biz)
                except Exception:
                    logger.exception("Failed to send report for business %s", biz.id)
    logger.info("Reports: weekly dispatch complete.")
async def _process_business_report(db: Session, user: User, biz: Business) -> None:
    snaps = db.scalars(
        select(AuditSnapshot)
        .where(
            AuditSnapshot.business_id == biz.id,
            AuditSnapshot.status == SnapshotStatus.ok,
        )
        .order_by(AuditSnapshot.ran_at.desc())
        .limit(2)
    ).all()
    if len(snaps) < 2:
        return
    current = _to_view(snaps[0], biz.name)
    previous = _to_view(snaps[1], biz.name)
    delta = diff_snapshots(current, previous)
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    html = emails.build_weekly_report_html(
        business_name=biz.name,
        summary=delta.summary,
        current_date=today
    )
    subject = f"Weekly Visibility Update: {biz.name}"
    await emails.send_email(user.email, subject, html)