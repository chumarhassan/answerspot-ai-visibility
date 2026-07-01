from __future__ import annotations
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import Session
import gemini
import llm
from models import (
    AuditSnapshot, Business, Competitor, FixRecommendation,
    FixStatus, FixType, Platform, SnapshotStatus, utcnow
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
    prompt = gemini.audit_prompt(category, city)
    try:
        raw = await llm.query_llm(prompt, as_json=True)
    except llm.LLMError as exc:
        return CheckResult(SnapshotStatus.failed, None, [], False, None, str(exc))
    businesses = gemini.parse_business_list(raw)
    mentioned, position = gemini.match_target(businesses, target_name)
    return CheckResult(SnapshotStatus.ok, raw, businesses, mentioned, position, None)
def competitors_from(result: CheckResult, target_name: str, limit: int | None = None) -> list[str]:
    target_norm = gemini._norm(target_name)
    others = [b for b in result.businesses if gemini._norm(b) != target_norm
              and target_norm not in gemini._norm(b)]
    return others[:limit] if limit else others
async def run_free_audit(db: Session, name: str, category: str, city: str) -> AuditSnapshot:
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
    issues: list[dict] = []
    if result.status == SnapshotStatus.failed:
        return issues
    if not result.mentioned:
        issues.append({
            "title": "AI doesn't recommend you yet",
            "detail": f"AI named {len(competitors)} other business(es) without mentioning you."
        })
    if competitors:
        issues.append({
            "title": "Competitors are filling the slots",
            "detail": f"Businesses like {competitors[0]} currently hold the spots you want."
        })
    return issues[:2]
async def run_business_audit(db: Session, business: Business) -> AuditSnapshot:
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
        snapshot.summary_text = await generate_summary(
            business, result.mentioned, result.position, competitors_from(result, business.name)
        )
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
    for fix in list(business.fixes):
        if fix.status == FixStatus.open:
            db.delete(fix)
    fixes: list[tuple[FixType, int, str]] = []
    if not result.mentioned:
        fixes.append((FixType.review_volume, 100, "Increase review volume and ratings."))
        fixes.append((FixType.citation, 80, "Standardize NAP profiles across major directories."))
        fixes.append((FixType.schema, 60, "Add LocalBusiness schema markup to your site."))
    else:
        fixes.append((FixType.review_volume, 70, "Keep collecting fresh reviews to hold your rank."))
    if not (business.website or "").strip():
        fixes.append((FixType.website, 90, "Add a crawlable website with clear location info."))
    for fix_type, priority, description in fixes:
        db.add(FixRecommendation(
            business_id=business.id,
            type=fix_type,
            priority=priority,
            description=description,
            status=FixStatus.open,
        ))
async def generate_summary(business: Business, result_mentioned: bool, position: int | None,
                           competitors: list[str]) -> str:
    deterministic = _fallback_summary(business, result_mentioned, position, competitors)
    try:
        comp = ", ".join(competitors[:3]) if competitors else "other businesses"
        prompt = (
            "Write 2 plain-English sentences explaining AI visibility.\n"
            "Rules: No invented stats. No global chains if local data is thin.\n"
            f"Business: {business.name} ({business.category} in {business.city}).\n"
            f"Mentioned: {'yes' if result_mentioned else 'no'}.\n"
            f"Competitors: {comp}."
        )
        text = await llm.query_llm(prompt, temperature=0.4)
        return text.strip() or deterministic
    except llm.LLMError:
        return deterministic
def _fallback_summary(business: Business, mentioned: bool, position: int | None,
                       competitors: list[str]) -> str:
    if mentioned:
        rank = f" at position {position}" if position else ""
        return f"AI assistants recommend {business.name}{rank} for this category."
    lead = competitors[0] if competitors else "local competitors"
    return f"AI is currently recommending {lead} instead of {business.name}."
def latest_snapshot(db: Session, business_id: int) -> AuditSnapshot | None:
    return db.scalar(
        select(AuditSnapshot)
        .where(AuditSnapshot.business_id == business_id)
        .order_by(AuditSnapshot.ran_at.desc())
        .limit(1)
    )
def visibility_score(mentioned: bool, position: int | None, has_snapshot: bool) -> int:
    return max(55, 100 - (position - 1) * 8)