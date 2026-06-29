"""Audit orchestration: run one AI-platform check and turn it into stored, immutable
results plus concrete fix recommendations.

Honesty rule (§7): we do NOT have a paid reviews/citations data source in the MVP, so
fix recommendations are specific about the ACTION but honest about the fact that we
can't yet measure the user's exact review/citation counts — we never invent a precise
statistic to sound authoritative.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

import gemini
from models import (
    AuditSnapshot,
    Business,
    Competitor,
    FixRecommendation,
    FixStatus,
    FixType,
    Platform,
    SnapshotStatus,
    utcnow,
)

MAX_TEASER_COMPETITORS = 3


@dataclass
class CheckResult:
    status: SnapshotStatus
    raw: str | None
    businesses: list[str]
    mentioned: bool
    position: int | None
    error: str | None


async def execute_check(category: str, city: str, target_name: str) -> CheckResult:
    """Call Gemini once and parse the outcome. Never raises — failures become a
    `failed` CheckResult so the caller can store an honest failed snapshot (§8)."""
    prompt = gemini.audit_prompt(category, city)
    try:
        raw = await gemini.query_gemini(prompt, as_json=True)
    except gemini.GeminiError as exc:
        return CheckResult(SnapshotStatus.failed, None, [], False, None, str(exc))

    businesses = gemini.parse_business_list(raw)
    mentioned, position = gemini.match_target(businesses, target_name)
    return CheckResult(SnapshotStatus.ok, raw, businesses, mentioned, position, None)


def competitors_from(result: CheckResult, target_name: str, limit: int | None = None) -> list[str]:
    """Recommended businesses other than the target, in rank order."""
    target_norm = gemini._norm(target_name)
    others = [b for b in result.businesses if gemini._norm(b) != target_norm
              and target_norm not in gemini._norm(b)]
    return others[:limit] if limit else others


# ── Free audit (public, no login) ─────────────────────────────────────────────
async def run_free_audit(db: Session, name: str, category: str, city: str) -> AuditSnapshot:
    """Run a one-time audit and persist an immutable snapshot with no business_id."""
    result = await execute_check(category, city, name)
    snapshot = AuditSnapshot(
        business_id=None,
        platform=Platform.gemini,
        query_text=gemini.build_audit_query(category, city),
        raw_response=result.raw,
        businesses_mentioned=result.businesses,
        position=result.position,
        status=result.status,
        error=result.error,
        ran_at=utcnow(),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def teaser_issues(result: CheckResult, competitors: list[str]) -> list[dict]:
    """1–2 honest teaser issues for the free audit (§7)."""
    issues: list[dict] = []
    if result.status == SnapshotStatus.failed:
        return issues
    if not result.mentioned:
        issues.append({
            "title": "AI doesn't recommend you yet",
            "detail": (
                f"When asked, the AI named {len(competitors)} other business(es) before you "
                "and didn't mention you at all. The full audit shows why and how to fix it."
            ),
        })
    if competitors:
        issues.append({
            "title": "Competitors are filling the recommendation slots",
            "detail": (
                f"Businesses like {competitors[0]} currently hold the spots you want. "
                "Closing the gap usually comes down to reviews, citations, and site markup."
            ),
        })
    return issues[:2]


# ── Logged-in business audit ──────────────────────────────────────────────────
async def run_business_audit(db: Session, business: Business) -> AuditSnapshot:
    """Run a tracked check for a saved business: persist snapshot, update competitor
    table, and (re)generate fix recommendations."""
    result = await execute_check(business.category, business.city, business.name)

    snapshot = AuditSnapshot(
        business_id=business.id,
        platform=Platform.gemini,
        query_text=gemini.build_audit_query(business.category, business.city),
        raw_response=result.raw,
        businesses_mentioned=result.businesses,
        position=result.position,
        status=result.status,
        error=result.error,
        ran_at=utcnow(),
    )
    db.add(snapshot)

    if result.status == SnapshotStatus.ok:
        _upsert_competitors(db, business, competitors_from(result, business.name))
        _regenerate_fixes(db, business, result)

    db.commit()
    db.refresh(snapshot)
    return snapshot


def _upsert_competitors(db: Session, business: Business, names: list[str]) -> None:
    existing = {c.competitor_name.lower(): c for c in business.competitors}
    now = utcnow()
    for name in names:
        c = existing.get(name.lower())
        if c:
            c.last_seen_at = now
        else:
            db.add(Competitor(
                business_id=business.id,
                competitor_name=name,
                first_seen_at=now,
                last_seen_at=now,
            ))


def _regenerate_fixes(db: Session, business: Business, result: CheckResult) -> None:
    """Replace the open fix list with a fresh prioritized set.

    Kept honest: we flag where we lack measured data instead of inventing numbers (§7).
    """
    # Clear prior open fixes so the list reflects the latest check.
    for fix in list(business.fixes):
        if fix.status == FixStatus.open:
            db.delete(fix)

    fixes: list[tuple[FixType, int, str]] = []

    if not result.mentioned:
        fixes.append((
            FixType.review_volume, 100,
            "Build review volume. AI assistants lean on businesses with many recent, "
            "high-rating reviews. We can't yet read your exact Google review count "
            "(that needs a data source you haven't connected), so count your current "
            "reviews and set a target above the competitors who are getting recommended.",
        ))
        fixes.append((
            FixType.citation, 80,
            "Fix your citations. Make sure your business name, address, and phone number "
            "(your \"NAP\") are identical across Google Business Profile, Yelp, and major "
            "directories — inconsistent listings make AI less confident recommending you.",
        ))
        fixes.append((
            FixType.schema, 60,
            "Add LocalBusiness schema markup to your website. Schema is invisible code "
            "that tells search engines and AI exactly what your business is, where it is, "
            "and what it offers — making you easier to surface.",
        ))
    else:
        fixes.append((
            FixType.review_volume, 70,
            "You're being recommended — protect that position. Keep collecting fresh "
            "reviews so newer competitors don't overtake you.",
        ))

    if not (business.website or "").strip():
        fixes.append((
            FixType.website, 90,
            "Add a website. You don't have one on file. Without a crawlable site with "
            "clear service and location info, AI has little to cite when recommending you.",
        ))

    for fix_type, priority, description in fixes:
        db.add(FixRecommendation(
            business_id=business.id,
            type=fix_type,
            priority=priority,
            description=description,
            status=FixStatus.open,
        ))


# ── Dashboard summary copy (Gemini with honest deterministic fallback) ─────────
async def generate_summary(business: Business, result_mentioned: bool, position: int | None,
                           competitors: list[str]) -> str:
    """Plain-English 'why you're not showing up' copy (§7).

    Tries Gemini for natural phrasing (reusing the free key, §10) but falls back to a
    deterministic sentence if Gemini is unavailable — the dashboard must never block on it.
    """
    deterministic = _fallback_summary(business, result_mentioned, position, competitors)
    if not gemini.settings.gemini_configured:
        return deterministic
    try:
        comp = ", ".join(competitors[:3]) if competitors else "no specific competitors"
        prompt = (
            "Write 2 plain-English sentences for a non-technical local business owner "
            "explaining their AI visibility. Be direct and honest; do NOT invent specific "
            "numbers or statistics.\n"
            f"Business: {business.name} ({business.category} in {business.city}).\n"
            f"Currently recommended by AI: {'yes' if result_mentioned else 'no'}.\n"
            f"Competitors AI recommends: {comp}."
        )
        text = await gemini.query_gemini(prompt, temperature=0.4)
        return text.strip() or deterministic
    except gemini.GeminiError:
        return deterministic


def _fallback_summary(business: Business, mentioned: bool, position: int | None,
                      competitors: list[str]) -> str:
    if mentioned:
        rank = f" at position {position}" if position else ""
        return (f"Good news — AI assistants currently recommend {business.name}{rank} for "
                f"\"{business.category} in {business.city}\". Keep your reviews and listings "
                "fresh to hold that spot.")
    lead = competitors[0] if competitors else "other local businesses"
    return (f"When customers ask AI for the best {business.category} in {business.city}, "
            f"{business.name} isn't mentioned — {lead} and others are recommended instead. "
            "This usually comes down to review volume, citation consistency, and website markup.")


def latest_snapshot(db: Session, business_id: int) -> AuditSnapshot | None:
    return db.scalar(
        select(AuditSnapshot)
        .where(AuditSnapshot.business_id == business_id)
        .order_by(AuditSnapshot.ran_at.desc())
        .limit(1)
    )


def visibility_score(mentioned: bool, position: int | None, has_snapshot: bool) -> int:
    """0–100 score that is the dominant visual on the dashboard (§9)."""
    if not has_snapshot:
        return 0
    if not mentioned:
        return 15
    if position is None:
        return 60
    # Position 1 -> ~95, decreasing with rank.
    return max(55, 100 - (position - 1) * 8)
