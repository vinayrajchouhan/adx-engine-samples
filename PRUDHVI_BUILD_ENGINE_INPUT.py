"""Pre-written `_build_engine_input()` for Prudhvi · drop into services/audit/engine.py.

Built against the actual pm_agency models we inspected:
  - Brand (name · settings · website_url · slug · owner_email)
  - ConnectedPlatform (platform · external_account_id · metadata_ · status="connected")
  - Campaign (platform · external_id · name · status · daily_budget · platform_data)
  - AdSet (platform · name · status · daily_budget · learning_phase_* · platform_data)
  - scan_data flat dict from existing engine.py (meta_spend · meta_cpa · meta_roas · meta_ctr · meta_fatigue_* · meta_avg_frequency · google_*)

Usage in services/audit/engine.py:
    from src.services.audit.adx_input_builder import build_engine_input

    async def run_audit(brand_id, current_user, session, meta_account_id, google_account_id):
        try:
            eng = await build_engine_input(brand_id, current_user, session,
                                            meta_account_id, google_account_id)
            ship = await ship_playbook_async(eng, max_seconds=8)
            if ship.ok:
                return to_legacy_audit_report(ship,
                    brand_id=current_user.brand_id,
                    currency=brand.settings.get("currency", "USD"),
                    currency_symbol={"USD":"$","GBP":"£","EUR":"€","AUD":"A$","INR":"₹","CAD":"C$"}.get(currency, "$"),
                    market=brand.settings.get("market", "us"))
        except Exception as e:
            logger.warning("adx engine failed · using legacy", exc_info=e)
        return await _legacy_run_audit(...)
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

# These imports assume pm_agency project layout
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from src.models import Brand, ConnectedPlatform, Campaign, AdSet
# from src.services.audit.scanner_meta import scan_meta_account  # whatever produces scan_data
# from src.services.audit.scanner_google import scan_google_account

from adx_engine.schemas import (
    EngineInput, MetaAdsData, GoogleAdsData, GA4Data, ShopifyData,
)


async def build_engine_input(
    brand_id: UUID,
    current_user,
    session,
    meta_account_id: Optional[str] = None,
    google_account_id: Optional[str] = None,
) -> EngineInput:
    """Build EngineInput from pm_agency DB · drop-in for run_audit body.

    NOTE for Prudhvi: I'm using your existing scan_data dict shape (flat keys like
    meta_spend, meta_cpa, meta_fatigue_replace_now). If you already build a
    different shape, point me at it and I'll re-map this function in 5 min.
    """
    from sqlalchemy import select
    from src.models import Brand, ConnectedPlatform, Campaign, AdSet

    # 1. Brand
    brand_q = await session.execute(select(Brand).where(Brand.id == brand_id))
    brand = brand_q.scalar_one()
    settings = brand.settings or {}

    # 2. Resolve meta / google account ids from ConnectedPlatform if not passed
    if not meta_account_id or not google_account_id:
        platforms_q = await session.execute(
            select(ConnectedPlatform).where(
                ConnectedPlatform.brand_id == brand_id,
                ConnectedPlatform.status == "connected",
            )
        )
        for p in platforms_q.scalars().all():
            if p.platform == "meta" and not meta_account_id:
                meta_account_id = p.external_account_id
            elif p.platform == "google" and not google_account_id:
                google_account_id = p.external_account_id

    # 3. Run your existing scanner to get scan_data flat dict
    scan_data: dict = {}
    if meta_account_id:
        # YOUR EXISTING META SCANNER · whatever you call it
        # from src.services.audit.engine import _scan_and_diagnose_meta
        # scan_data = await _scan_and_diagnose_meta(session, brand_id, meta_account_id, scan_data)
        pass
    if google_account_id:
        # from src.services.audit.engine import _scan_and_diagnose_google
        # scan_data = await _scan_and_diagnose_google(session, brand_id, google_account_id, scan_data)
        pass

    # 4. Pull campaigns + ad_sets from DB for structure analysis
    meta_campaigns_q = await session.execute(
        select(Campaign).where(
            Campaign.brand_id == brand_id,
            Campaign.platform == "meta",
            Campaign.status.in_(("active", "ACTIVE")),
        )
    )
    meta_campaigns = list(meta_campaigns_q.scalars().all())

    meta_adsets_q = await session.execute(
        select(AdSet).where(
            AdSet.brand_id == brand_id,
            AdSet.platform == "meta",
            AdSet.status.in_(("active", "ACTIVE")),
        )
    )
    meta_adsets = list(meta_adsets_q.scalars().all())

    # 5. Build MetaAdsData
    meta_data = None
    if meta_account_id:
        meta_data = MetaAdsData(
            account_id=meta_account_id,
            monthly_spend=float(scan_data.get("meta_spend", 0)),
            pixel_diagnostics={
                "purchase_events_count": scan_data.get("meta_purchases_pixel", 0),
                "backend_conversions": scan_data.get("meta_backend_conversions", 0),
                "event_match_quality": scan_data.get("meta_emq_score", scan_data.get("meta_event_match_quality", 0)),
                "status": scan_data.get("meta_pixel_status", "active"),
                "domain_verified_status": scan_data.get("meta_domain_verified", "verified"),
                "attribution_window_days": scan_data.get("meta_attribution_window_days", 7),
            },
            capi_status={
                "event_match_quality": scan_data.get("meta_capi_emq", scan_data.get("meta_emq_score", 0)),
                "purchase_events_count": scan_data.get("meta_capi_purchases", 0),
                "active": scan_data.get("meta_capi_active", False),
            },
            creative_performance=[
                {
                    "name": c.get("name", "unknown"),
                    "frequency": c.get("frequency", 0),
                    "hook_rate": c.get("hook_rate", c.get("video_hook_rate", 0)),
                    "spend": c.get("spend", 0),
                    "similarity_score": c.get("similarity_score", 0),
                }
                for c in scan_data.get("meta_top_creatives", [])
            ],
            ad_sets=[
                {
                    "name": a.name,
                    "spend": float(a.platform_data.get("spend_30d", 0)) if a.platform_data else 0,
                    "frequency": (a.platform_data or {}).get("frequency", 0),
                    "reach_pct": (a.platform_data or {}).get("reach_pct", 0),
                }
                for a in meta_adsets
            ],
            campaigns=[{"name": c.name, "objective": c.objective} for c in meta_campaigns],
        )

    # 6. Build GoogleAdsData
    google_data = None
    if google_account_id:
        google_campaigns_q = await session.execute(
            select(Campaign).where(
                Campaign.brand_id == brand_id,
                Campaign.platform == "google",
                Campaign.status.in_(("active", "ACTIVE")),
            )
        )
        google_campaigns = list(google_campaigns_q.scalars().all())
        google_data = GoogleAdsData(
            account_id=google_account_id,
            monthly_spend=float(scan_data.get("google_spend", 0)),
            conversion_actions=scan_data.get("google_conversion_actions", []),
            campaigns=[{"name": c.name, "type": c.campaign_type} for c in google_campaigns],
        )

    # 7. Brand profile
    return EngineInput(
        brand_id=str(brand_id),
        brand_name=brand.name,
        conversion_goal=settings.get("conversion_goal", _infer_conversion_goal(brand, settings)),
        primary_geo=settings.get("market", "US").upper(),
        audit_window_days=settings.get("audit_window_days", 90),
        meta=meta_data,
        google=google_data,
        ga4=None,      # add if you have GA4 connector
        shopify=None,  # add if you have Shopify connector
        industry=settings.get("industry", ""),
        business_model=settings.get("business_model", ""),
        aov=settings.get("aov", 0),
        lifecycle_stage=settings.get("lifecycle_stage", "growth"),
    )


def _infer_conversion_goal(brand, settings) -> str:
    """Cheap inference if settings doesn't specify · brand-name keyword + plan_tier."""
    name = (brand.name or "").lower()
    if any(k in name for k in ("saas", "platform", "software", "data", "flow")):
        return "leads"
    if any(k in name for k in ("studio", "fitness", "spa", "salon", "clinic")):
        return "bookings"
    if any(k in name for k in ("subscription", "monthly", "box")):
        return "subscriptions"
    return "sales"
