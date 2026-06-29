"""Stripe billing — TEST MODE by default (§5, §10).

Nothing here goes live until real keys are supplied and the user says so. If Stripe
isn't configured the checkout endpoint returns a clear 503 rather than pretending.
"""
from __future__ import annotations

import stripe
from fastapi import HTTPException
from sqlalchemy.orm import Session

from config import get_settings
from models import Plan, Subscription, User

settings = get_settings()
if settings.stripe_configured:
    stripe.api_key = settings.stripe_secret_key

# Plan metadata shown on the billing page and enforced for gating (§3.6).
PLAN_CATALOG = {
    Plan.free: {"name": "Free", "price": 0, "features": ["One-time AI visibility audit"]},
    Plan.starter: {"name": "Starter", "price": 49, "features": [
        "Single category + city", "Weekly automated checks", "Fix recommendations",
    ]},
    Plan.pro: {"name": "Pro", "price": 99, "features": [
        "Everything in Starter", "Deeper competitor tracking", "More frequent checks",
    ]},
}


def _price_id(plan: Plan) -> str:
    mapping = {
        Plan.starter: settings.stripe_starter_price_id,
        Plan.pro: settings.stripe_pro_price_id,
    }
    price_id = mapping.get(plan)
    if not price_id:
        raise HTTPException(status_code=503, detail=f"No Stripe price configured for {plan.value}")
    return price_id


def create_checkout_session(db: Session, user: User, plan: Plan) -> str:
    if not settings.stripe_configured:
        raise HTTPException(
            status_code=503,
            detail="Stripe is not configured on the server. Add test keys to .env to enable checkout.",
        )

    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    customer_id = sub.stripe_customer_id if sub else None
    if not customer_id:
        customer = stripe.Customer.create(email=user.email, metadata={"user_id": str(user.id)})
        customer_id = customer.id
        if sub:
            sub.stripe_customer_id = customer_id
            db.commit()

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": _price_id(plan), "quantity": 1}],
        success_url=f"{settings.frontend_url}/billing?status=success",
        cancel_url=f"{settings.frontend_url}/billing?status=cancelled",
        metadata={"user_id": str(user.id), "plan": plan.value},
    )
    return session.url


def handle_webhook(db: Session, payload: bytes, signature: str | None) -> None:
    """Verify and process a Stripe webhook, updating the subscription row."""
    if not settings.stripe_configured or not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook not configured")
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.stripe_webhook_secret
        )
    except (ValueError, stripe.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail="Invalid webhook signature") from exc

    etype = event["type"]
    obj = event["data"]["object"]

    if etype == "checkout.session.completed":
        user_id = int(obj["metadata"]["user_id"])
        plan = Plan(obj["metadata"]["plan"])
        _set_plan(db, user_id, plan, obj.get("subscription"), obj.get("customer"))
    elif etype in ("customer.subscription.deleted", "customer.subscription.paused"):
        _downgrade_by_customer(db, obj.get("customer"))


def _set_plan(db: Session, user_id: int, plan: Plan, sub_id, customer_id) -> None:
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not sub:
        sub = Subscription(user_id=user_id)
        db.add(sub)
    sub.plan = plan
    sub.status = "active"
    sub.stripe_subscription_id = sub_id
    if customer_id:
        sub.stripe_customer_id = customer_id
    db.commit()


def _downgrade_by_customer(db: Session, customer_id) -> None:
    if not customer_id:
        return
    sub = db.query(Subscription).filter(Subscription.stripe_customer_id == customer_id).first()
    if sub:
        sub.plan = Plan.free
        sub.status = "cancelled"
        db.commit()
