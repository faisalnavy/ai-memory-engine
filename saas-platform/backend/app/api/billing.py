"""Stripe billing routes — subscription management, webhooks."""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.auth import get_current_user_id
from app.core.db import get_db
from app.core.config import settings
from app.models.schema import Organization, PlanType

router = APIRouter(prefix="/billing", tags=["billing"])

PLAN_LIMITS = {
    PlanType.free:       {"max_projects": 3,   "max_members": 1,  "price": "Free"},
    PlanType.pro:        {"max_projects": 20,  "max_members": 1,  "price": "$12/mo"},
    PlanType.team:       {"max_projects": 100, "max_members": 10, "price": "$49/mo"},
    PlanType.enterprise: {"max_projects": 999, "max_members": 999,"price": "Custom"},
}


@router.get("/plans")
def get_plans():
    return {"plans": [
        {"id": "free",       "name": "Free",       "price": "$0/mo",   "projects": 3,   "members": 1,  "features": ["3 projects", "CLI + GUI", "Community support"]},
        {"id": "pro",        "name": "Pro",         "price": "$12/mo",  "projects": 20,  "members": 1,  "features": ["20 projects", "API access", "Priority support"]},
        {"id": "team",       "name": "Team",        "price": "$49/mo",  "projects": 100, "members": 10, "features": ["100 projects", "10 team members", "Webhooks + SDK"]},
        {"id": "enterprise", "name": "Enterprise",  "price": "Custom",  "projects": 999, "members": 999,"features": ["Unlimited", "SSO/SAML", "Dedicated support", "SLA"]},
    ]}


class CheckoutRequest(BaseModel):
    org_id: str
    plan: str
    success_url: str
    cancel_url: str


@router.post("/checkout")
async def create_checkout(req: CheckoutRequest,
                          user_id: str = Depends(get_current_user_id),
                          db: AsyncSession = Depends(get_db)):
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        price_id = settings.STRIPE_PRICE_PRO if req.plan == "pro" else settings.STRIPE_PRICE_TEAM

        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=req.success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=req.cancel_url,
            metadata={"org_id": req.org_id, "user_id": user_id},
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(500, f"Stripe error: {e}")


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payload   = await request.body()
        sig_header= request.headers.get("stripe-signature")
        event     = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(400, str(e))

    if event["type"] == "checkout.session.completed":
        data   = event["data"]["object"]
        org_id = data["metadata"]["org_id"]
        plan   = data["metadata"].get("plan", "pro")

        result = await db.execute(select(Organization).where(Organization.id == org_id))
        org = result.scalar_one_or_none()
        if org:
            org.plan = PlanType(plan)
            org.stripe_customer_id     = data.get("customer")
            org.stripe_subscription_id = data.get("subscription")
            limits = PLAN_LIMITS[org.plan]
            org.max_projects = limits["max_projects"]
            org.max_members  = limits["max_members"]
            await db.commit()

    elif event["type"] == "customer.subscription.deleted":
        customer_id = event["data"]["object"]["customer"]
        result = await db.execute(select(Organization).where(
            Organization.stripe_customer_id == customer_id))
        org = result.scalar_one_or_none()
        if org:
            org.plan = PlanType.free
            org.max_projects = 3
            org.max_members  = 1
            await db.commit()

    return {"status": "ok"}


@router.get("/usage/{org_id}")
async def get_usage(org_id: str, user_id: str = Depends(get_current_user_id),
                    db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func
    from app.models.schema import UsageRecord
    result = await db.execute(
        select(UsageRecord).where(UsageRecord.org_id == org_id)
        .order_by(UsageRecord.month.desc()).limit(12))
    records = result.scalars().all()
    return {"usage": [{"month": r.month, "queries": r.queries,
                       "tokens_saved": r.tokens_saved,
                       "files_indexed": r.files_indexed} for r in records]}
