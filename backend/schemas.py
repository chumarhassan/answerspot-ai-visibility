from __future__ import annotations
import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from models import FixStatus, FixType, Plan, Platform, SnapshotStatus
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
def _clean(value: str, field: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field} cannot be empty")
    if _CONTROL_CHARS.search(value):
        raise ValueError(f"{field} contains invalid characters")
    return value
class AuditRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=120)
    @field_validator("name", "category", "city")
    @classmethod
    def _validate(cls, v: str, info) -> str:
        return _clean(v, info.field_name)
class TeaserIssue(BaseModel):
    title: str
    detail: str
class AuditResponse(BaseModel):
    snapshot_id: int
    status: SnapshotStatus
    mentioned: bool
    position: int | None = None
    competitors: list[str] = []
    teaser_issues: list[TeaserIssue] = []
    query_text: str
    error: str | None = None
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)
    referral_code: str | None = Field(default=None, max_length=20)
    @field_validator("password")
    @classmethod
    def _complexity(cls, v: str) -> str:
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    plan: Plan
    has_business: bool
class BusinessCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=120)
    website: str | None = Field(default=None, max_length=500)
    @field_validator("name", "category", "city")
    @classmethod
    def _validate(cls, v: str, info) -> str:
        return _clean(v, info.field_name)
class BusinessUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=120)
    city: str | None = Field(default=None, min_length=1, max_length=120)
    website: str | None = Field(default=None, max_length=500)
    @field_validator("name", "category", "city")
    @classmethod
    def _validate(cls, v: str | None, info) -> str | None:
        if v is None:
            return v
        return _clean(v, info.field_name)
class BusinessOut(BaseModel):
    id: int
    name: str
    category: str
    city: str
    website: str | None
    created_at: datetime
    model_config = {"from_attributes": True}
class CompetitorOut(BaseModel):
    competitor_name: str
    first_seen_at: datetime
    last_seen_at: datetime
    model_config = {"from_attributes": True}
class FixOut(BaseModel):
    id: int
    type: FixType
    description: str
    priority: int
    status: FixStatus
    model_config = {"from_attributes": True}
class PlatformStatus(BaseModel):
    platform: Platform
    active: bool
class DashboardResponse(BaseModel):
    business: BusinessOut
    has_snapshot: bool
    latest_status: SnapshotStatus | None = None
    mentioned: bool = False
    position: int | None = None
    visibility_score: int
    summary: str
    competitors: list[CompetitorOut] = []
    fixes: list[FixOut] = []
    platforms: list[PlatformStatus] = []
    last_checked: datetime | None = None
class DiffResponse(BaseModel):
    has_previous: bool
    current_ran_at: datetime | None = None
    previous_ran_at: datetime | None = None
    position_change: int | None = None
    new_competitors: list[str] = []
    dropped_competitors: list[str] = []
    became_mentioned: bool = False
    lost_mention: bool = False
    summary: str = ""
class CheckoutRequest(BaseModel):
    plan: Plan
    @field_validator("plan")
    @classmethod
    def _not_free(cls, v: Plan) -> Plan:
        if v == Plan.free:
            raise ValueError("Free plan does not require checkout")
        return v
class CheckoutResponse(BaseModel):
    checkout_url: str
class SubscriptionOut(BaseModel):
    plan: Plan
    status: str
    model_config = {"from_attributes": True}