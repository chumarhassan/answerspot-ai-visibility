"""Relational data model (§6).

Design rules:
  * audit_snapshots rows are IMMUTABLE — never overwritten — so week-over-week
    diffing is a query, not a recomputation.
  * audit_snapshots.business_id is NULLABLE so the no-login free audit can persist a
    snapshot before an account exists.
  * Platform is an enum: gemini is ACTIVE; chatgpt/perplexity/claude are COMING_SOON
    placeholders (no paid calls — §4 Phase-2 prep).
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Platform(str, enum.Enum):
    gemini = "gemini"
    chatgpt = "chatgpt"      # Phase 2 — coming soon
    perplexity = "perplexity"  # Phase 2 — coming soon
    claude = "claude"        # Phase 2 — coming soon


# Platforms that are actually queried in the MVP. Everything else renders as
# "coming soon" in the dashboard and is never called.
ACTIVE_PLATFORMS = {Platform.gemini}


class SnapshotStatus(str, enum.Enum):
    pending = "pending"
    ok = "ok"
    failed = "failed"


class Plan(str, enum.Enum):
    free = "free"
    starter = "starter"
    pro = "pro"


class FixType(str, enum.Enum):
    review_volume = "review_volume"
    citation = "citation"
    schema = "schema"
    website = "website"
    other = "other"


class FixStatus(str, enum.Enum):
    open = "open"
    done = "done"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    oauth_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    businesses: Mapped[list[Business]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subscription: Mapped[Subscription | None] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="businesses")
    snapshots: Mapped[list[AuditSnapshot]] = relationship(back_populates="business", cascade="all, delete-orphan")
    competitors: Mapped[list[Competitor]] = relationship(back_populates="business", cascade="all, delete-orphan")
    fixes: Mapped[list[FixRecommendation]] = relationship(back_populates="business", cascade="all, delete-orphan")


class AuditSnapshot(Base):
    """Immutable, time-stamped result of one AI-platform check."""

    __tablename__ = "audit_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Nullable so a no-login free audit can be stored without an account.
    business_id: Mapped[int | None] = mapped_column(ForeignKey("businesses.id"), index=True, nullable=True)
    platform: Mapped[Platform] = mapped_column(Enum(Platform), default=Platform.gemini)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    businesses_mentioned: Mapped[list] = mapped_column(JSON, default=list)
    # 1-based rank of the target business in the recommendation list; null = not mentioned.
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[SnapshotStatus] = mapped_column(Enum(SnapshotStatus), default=SnapshotStatus.pending)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    ran_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    business: Mapped[Business | None] = relationship(back_populates="snapshots")


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True, nullable=False)
    competitor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    business: Mapped[Business] = relationship(back_populates="competitors")


class FixRecommendation(Base):
    __tablename__ = "fix_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True, nullable=False)
    type: Mapped[FixType] = mapped_column(Enum(FixType), default=FixType.other)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # Higher = more impactful; used to sort the fix list (§7).
    priority: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[FixStatus] = mapped_column(Enum(FixStatus), default=FixStatus.open)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    business: Mapped[Business] = relationship(back_populates="fixes")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True, nullable=False)
    plan: Mapped[Plan] = mapped_column(Enum(Plan), default=Plan.free)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    renewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="subscription")
