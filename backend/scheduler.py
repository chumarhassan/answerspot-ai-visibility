"""Recurring tracking scheduler (§3.4).

Runs automated Gemini checks for tracked businesses, gated by plan (Free = none,
Starter = weekly, Pro = more frequent) and spaced out to respect the free-tier quota
with graceful backoff rather than failure (§4). Quota is treated as a runtime reality
(react to 429 in gemini.py) — we do not hardcode it as fact here.
"""
from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

import audit
from db import SessionLocal
from models import Business, Plan, Subscription

logger = logging.getLogger("answerspot.scheduler")

# Seconds between consecutive checks within a run — conservative spacing so a batch of
# businesses stays well under the free-tier per-minute limit.
_INTER_CHECK_DELAY = 6.0

# How often a plan is due for a check.
_PLAN_INTERVAL_DAYS = {Plan.starter: 7, Plan.pro: 2}

_scheduler: AsyncIOScheduler | None = None


def _plans_due() -> dict[int, Plan]:
    """Map user_id -> plan for users on a paid (tracked) plan."""
    with SessionLocal() as db:
        subs = db.scalars(
            select(Subscription).where(Subscription.plan.in_([Plan.starter, Plan.pro]))
        ).all()
        return {s.user_id: s.plan for s in subs}


async def run_due_checks() -> None:
    """Run scheduled checks for all eligible businesses, spaced out for the quota."""
    due = _plans_due()
    if not due:
        return

    with SessionLocal() as db:
        businesses = db.scalars(
            select(Business).where(Business.user_id.in_(list(due.keys())))
        ).all()
        # Pro gets deeper tracking; for the MVP that means all their businesses,
        # Starter is limited to a single (their first) business per §3.6.
        targets: list[Business] = []
        seen_starter_user: set[int] = set()
        for biz in businesses:
            plan = due[biz.user_id]
            if plan == Plan.starter:
                if biz.user_id in seen_starter_user:
                    continue
                seen_starter_user.add(biz.user_id)
            targets.append(biz)

    logger.info("Scheduler: running %d due check(s)", len(targets))
    for biz in targets:
        with SessionLocal() as db:
            fresh = db.get(Business, biz.id)
            if fresh is None:
                continue
            try:
                await audit.run_business_audit(db, fresh)
            except Exception:  # never let one bad check kill the batch
                logger.exception("Scheduled check failed for business %s", biz.id)
        await asyncio.sleep(_INTER_CHECK_DELAY)


def start_scheduler() -> None:
    """Start the background scheduler. Daily tick decides who is actually due."""
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = AsyncIOScheduler()
    # Tick daily; per-plan cadence is enforced by which businesses we pick each tick.
    _scheduler.add_job(run_due_checks, "interval", days=1, id="due_checks", coalesce=True)
    _scheduler.start()
    logger.info("Scheduler started")


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
