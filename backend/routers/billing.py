"""Billing endpoints: plan catalog, Stripe test checkout, and webhook (§3.6)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

import billing as billing_service
from auth import ensure_subscription, get_current_user
from db import get_db
from models import User
from schemas import CheckoutRequest, CheckoutResponse, SubscriptionOut

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("/plans")
def list_plans() -> dict:
    return {
        plan.value: {**meta, "id": plan.value}
        for plan, meta in billing_service.PLAN_CATALOG.items()
    }


@router.get("/subscription", response_model=SubscriptionOut)
def my_subscription(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> SubscriptionOut:
    sub = ensure_subscription(db, user)
    return SubscriptionOut.model_validate(sub)


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout(
    payload: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CheckoutResponse:
    ensure_subscription(db, user)
    url = billing_service.create_checkout_session(db, user, payload.plan)
    return CheckoutResponse(checkout_url=url)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    billing_service.handle_webhook(db, payload, signature)
    return {"received": True}
