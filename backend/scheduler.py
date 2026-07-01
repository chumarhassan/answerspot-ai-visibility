from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import delete, select
import audit
import reports_engine
from db import SessionLocal
from models import AuditSnapshot, Business, Plan, SnapshotStatus, Subscription
logger = logging.getLogger("answerspot.scheduler")
_INTER_CHECK_DELAY = 6.0
_PLAN_INTERVAL_DAYS = {Plan.starter: 7, Plan.pro: 2}
_scheduler: AsyncIOScheduler | None = None
def _plans_due() -> dict[int, Plan]:
    with SessionLocal() as db:
        subs = db.scalars(
            select(Subscription).where(Subscription.plan.in_([Plan.starter, Plan.pro]))
        ).all()
        return {s.user_id: s.plan for s in subs}
def _last_ok_snapshot(db, business_id: int) -> datetime | None:
    snap = db.scalar(
        select(AuditSnapshot.ran_at)
        .where(
            AuditSnapshot.business_id == business_id,
            AuditSnapshot.status == SnapshotStatus.ok,
        )
        .order_by(AuditSnapshot.ran_at.desc())
        .limit(1)
    )
    return snap
def _is_due(last_ran: datetime | None, plan: Plan) -> bool:
    if last_ran is None:
        return True
    interval = _PLAN_INTERVAL_DAYS.get(plan)
    if interval is None:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(days=interval)
    if last_ran.tzinfo is None:
        last_ran = last_ran.replace(tzinfo=timezone.utc)
    return last_ran <= cutoff
async def run_due_checks() -> None:
    due = _plans_due()
    if not due:
        return
    with SessionLocal() as db:
        businesses = db.scalars(
            select(Business).where(Business.user_id.in_(list(due.keys())))
        ).all()
        targets: list[Business] = []
        seen_starter_user: set[int] = set()
        for biz in businesses:
            plan = due[biz.user_id]
            if plan == Plan.starter:
                if biz.user_id in seen_starter_user:
                    continue
                seen_starter_user.add(biz.user_id)
            last_ran = _last_ok_snapshot(db, biz.id)
            if not _is_due(last_ran, plan):
                continue
            targets.append(biz)
    logger.info("Scheduler: running %d due check(s)", len(targets))
    for biz in targets:
        with SessionLocal() as db:
            fresh = db.get(Business, biz.id)
            if fresh is None:
                continue
            try:
                await audit.run_business_audit(db, fresh)
            except Exception:
                logger.exception("Scheduled check failed for business %s", biz.id)
        await asyncio.sleep(_INTER_CHECK_DELAY)
def prune_anonymous_snapshots() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    with SessionLocal() as db:
        q = delete(AuditSnapshot).where(
            AuditSnapshot.business_id == None, AuditSnapshot.ran_at <= cutoff
        )
        res = db.execute(q)
        db.commit()
        if res.rowcount > 0:
            logger.info("Scheduler: pruned %d anonymous snapshots", res.rowcount)
def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(run_due_checks, "interval", days=1, id="due_checks", coalesce=True)
    _scheduler.add_job(
        prune_anonymous_snapshots, "cron", hour=3, minute=0, id="prune_anon"
    )
    _scheduler.add_job(
        reports_engine.dispatch_weekly_reports, "cron", day_of_week="mon", hour=8, minute=0, id="weekly_reports"
    )
    _scheduler.start()
    logger.info("Scheduler started")
def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None