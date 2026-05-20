# AdX Engine · Integration Spec for pm_agency

**Version:** 0.1.2
**Target backend:** pm_agency (FastAPI · Python 3.12+ · Pydantic v2)
**Author:** Rey · Clapp B.V.
**Last updated:** 2026-05-19

---

## What this gives you

- **259-check engine** across Meta · Google · GA4 · Shopify · cross-platform · all firing in your existing `/audit/run` flow
- **36 sub-agents** powering deep-dives · differential thinking · scale moves · creative pulse · audience pulse · intel briefing · trust ratio
- **16-page Expert Playbook** rendered as standalone HTML · served via `/playbook/{run_id}` route mounted in your FastAPI app
- **Legacy-shape compatibility** · `AuditReport` Pydantic schema returned unchanged · your UI / DB / billing / analytics keep working
- **Auto-fallback** · if our engine throws, your existing `engine.run_audit()` takes over · zero customer impact

---

## Installation (1 line)

```toml
# pyproject.toml or requirements.txt
adx-engine @ git+https://github.com/vinayrajchouhan/adx-engine.git@v0.1.2
```

```bash
pip install -e .  # or uv sync
```

---

## Integration · 3 code changes total

### Change 1 · `api/main.py` · mount the viewer route (1 line)

```python
from adx_engine import register_playbook_routes

app = FastAPI(...)
# ... your existing route registrations
register_playbook_routes(app, mount_path="/playbook")
```

Exposes:
- `GET /playbook/{run_id}` → renders the 16-page Playbook HTML
- `GET /playbook/{run_id}/pdf` → downloads PDF (if available)
- `GET /playbook/{run_id}/raw` → raw HTML text (debug)

---

### Change 2 · `services/audit/engine.py` · swap engine call (8 lines)

```python
from adx_engine import ship_playbook, to_legacy_audit_report
from adx_engine.schemas import EngineInput, MetaAdsData, GoogleAdsData, GA4Data, ShopifyData

async def run_audit(brand_id, current_user, session, meta_account_id, google_account_id):
    try:
        eng = await _build_engine_input(brand_id, current_user, session,
                                        meta_account_id, google_account_id)
        ship = ship_playbook(eng)
        if ship.ok:
            return to_legacy_audit_report(
                ship,
                brand_id=current_user.brand_id,
                currency=current_user.brand_currency or "USD",
                currency_symbol=current_user.brand_currency_symbol or "$",
                market=current_user.brand_market or "us",
            )
    except Exception as e:
        logger.warning("adx engine failed · falling back to legacy", exc_info=e)
    return await _legacy_run_audit(brand_id, current_user, session,
                                    meta_account_id, google_account_id)
```

You write `_build_engine_input()` · maps your DB fields to our `EngineInput`. See schema appendix below.

---

### Change 3 · `schemas/audit.py` · allow adx_* fields (1 line · OPTIONAL but recommended)

Pydantic v2 default strips our extra `adx_playbook_url` field. To pass it through to your frontend, add ONE of these:

**Option A · allow all extras (1 line):**
```python
from pydantic import ConfigDict

class AuditReport(BaseModel):
    model_config = ConfigDict(extra="allow")   # ← add this
    id: UUID
    # ... rest unchanged
```

**Option B · explicit AdX fields (3 lines):**
```python
class AuditReport(BaseModel):
    # ... existing fields
    adx_playbook_url: str | None = None
    adx_playbook_html_path: str | None = None
    adx_short_id: str | None = None
```

Without this change, `/audit/run` still works · your frontend just won't see the Playbook URL · you'd need to construct `/playbook/{audit_id}` yourself in the frontend.

---

## EngineInput builder · how to map your DB to ours

```python
from adx_engine.schemas import EngineInput, MetaAdsData, GoogleAdsData, GA4Data, ShopifyData

async def _build_engine_input(brand_id, current_user, session, meta_account_id, google_account_id):
    brand = await get_brand(session, brand_id)

    meta_data = None
    if meta_account_id:
        scan = await get_meta_scan_data(session, brand_id, meta_account_id)
        meta_data = MetaAdsData(
            account_id=meta_account_id,
            monthly_spend=scan.monthly_spend,
            pixel_diagnostics={
                "purchase_events_count": scan.pixel_purchases,
                "backend_conversions": scan.backend_orders,
                "event_match_quality": scan.emq_score,
                "status": scan.pixel_status,
                "attribution_window_days": scan.attribution_window or 7,
            },
            capi_status={
                "event_match_quality": scan.emq_score,
                "purchase_events_count": scan.capi_purchases,
            },
            creative_performance=[
                {"name": c.name, "frequency": c.frequency, "hook_rate": c.hook_rate,
                 "spend": c.spend, "similarity_score": c.similarity_score}
                for c in scan.creatives
            ],
            ad_sets=[
                {"name": a.name, "spend": a.spend, "frequency": a.frequency,
                 "reach_pct": a.reach_pct}
                for a in scan.ad_sets
            ],
            campaigns=[{"name": c.name} for c in scan.campaigns],
        )

    # Same pattern for google_data, ga4_data, shopify_data

    return EngineInput(
        brand_id=str(brand_id),
        brand_name=brand.name,
        conversion_goal=brand.conversion_goal or "sales",
        primary_geo=brand.geo or "US",
        audit_window_days=90,
        meta=meta_data,
        google=google_data,
        ga4=ga4_data,
        shopify=shopify_data,
    )
```

---

## Response shape · what `to_legacy_audit_report()` returns

Exact match for your `pm_agency.schemas.audit.AuditReport` Pydantic model. Verified field-by-field against `src/schemas/audit.py:302`.

| Your field | Source from our engine |
|---|---|
| `id` | Auto-generated UUID (or pass `audit_id=`) |
| `brand_id` | Pass-through |
| `audit_score` | Engine `overall_score` (0-100) |
| `audit_label` | Derived: excellent / good / warning / poor / critical |
| `platforms_audited` | Connected platforms set |
| `monthly_spend` | Sum of Meta + Google spend |
| `currency` · `currency_symbol` · `market` | Pass-through (default USD/$/us) |
| `current_phase` | Inferred: foundation / efficiency / scale / optimize |
| `retrospective` | Stub (v1.1 wires real data from feedback_loop agent) |
| `quick_wins` | Findings where `effort_category="quick_win"` |
| `current_problems` | Non-quick-win findings |
| `layer_health` | Mapped from engine `score_breakdown` dict |
| `top_action` | Highest-priority finding |
| `next_steps` | Next 3 by priority |
| `total_problems_detected` | `len(detected_problems)` |
| `total_risk_exposure` | Sum of `impact_estimate` |
| `computed_at` | UTC now |
| **`adx_playbook_url`** | `"/playbook/{short_id}"` (requires Change 3) |
| **`adx_short_id`** | Engine run short_id |

---

## Failure handling · zero customer impact guarantee

The integration pattern wraps our call in try/except. If anything fails, your existing `_legacy_run_audit` runs · customer sees yesterday's behavior.

| Failure mode | Result |
|---|---|
| Our engine crashes on call | Legacy fires · customer never sees error |
| Pydantic validation rejects output | Caught · falls back to legacy |
| Our PDF emitter fails | HTML still served · `pdf_path` is None · no exception |
| Performance >5s | Set `ship_playbook(eng, max_seconds=5)` · falls through on timeout |
| Dependency conflict on install | `pip install` fails · revert one commit · we fix upstream |

---

## Logging · route our logs through yours

```python
import logging
from adx_engine import set_logger

set_logger(logging.getLogger("pm_agency"))  # or your Sentry-wrapped logger
```

All `adx_engine.*` log calls flow through your handler · Sentry/Datadog/etc capture them.

---

## Customer-storage location · ONE env var to set on Linux

Our engine writes per-run artifacts to `customers/{brand_id}/runs/{run_id}/playbook.html`. Default root is `/Users/vrc/Adx/customers/` (Mac). On your Linux server:

```bash
export ADX_CUSTOMERS_ROOT=/var/adx-customers/
```

Make sure the directory exists and your service has write permission. Same `run_id` lookup works for `/playbook/{run_id}` route regardless of path.

---

## Testing locally before merge

```python
# quick_smoke.py
from adx_engine import ship_playbook, to_legacy_audit_report
from adx_engine.schemas import EngineInput, MetaAdsData
from uuid import uuid4

eng = EngineInput(
    brand_id="test", brand_name="Test", conversion_goal="sales",
    primary_geo="US", audit_window_days=90,
    meta=MetaAdsData(account_id="act_test", monthly_spend=5000,
        pixel_diagnostics={"purchase_events_count": 80, "backend_conversions": 100,
                           "event_match_quality": 5.5},
        capi_status={"event_match_quality": 5.5},
        creative_performance=[{"name": "a", "frequency": 3.5, "hook_rate": 0.25}],
        ad_sets=[{"name": "as_a", "spend": 4000, "frequency": 3.5}],
        campaigns=[{"name": "c1"}]),
)
ship = ship_playbook(eng)
print(f"engine: ok={ship.ok} · findings={ship.findings_count}")
print(f"HTML: {ship.html_path}")

legacy = to_legacy_audit_report(ship, brand_id=uuid4())
print(f"adapter: audit_score={legacy['audit_score']} · phase={legacy['current_phase']}")
print(f"playbook URL: {legacy['adx_playbook_url']}")
```

```bash
python quick_smoke.py
```

Expected: `engine: ok=True · findings=7-14 · audit_score=70-85 · playbook URL: /playbook/...`

---

## Recommended deploy sequence

1. **Phase 1 · Install** (1 day) · `pip install` in staging · run smoke test · don't change any routes yet
2. **Phase 2 · Wire route handler** (1 day) · Change 2 in staging with try/except fallback · monitor 24h
3. **Phase 3 · Mount viewer** (1 hour) · Change 1 + 3 · soft-launch to internal user
4. **Phase 4 · Production rollout** · monitor `/playbook/*` route metrics · ramp customer traffic

If anything goes wrong at any phase, revert one commit · legacy path resumes immediately.

---

## Open items · known limitations in v0.1.0

| Item | Status | Target |
|---|---|---|
| Live AI Visibility (Page 15) scraper | Partial · scaffolded | v0.1.1 |
| `predicted_problems` (predictive layer) | Returns `[]` | v0.2.0 |
| `retrospective` field | Returns stub | v0.2.0 |
| `narrative_clusters` (LLM narratives) | Returns `[]` | v0.2.0 |
| PDF on Linux | Requires `apt install chromium` on server | v0.1.0 (your choice) |
| Customer storage default path | Hard-coded Mac path · override with `ADX_CUSTOMERS_ROOT` | v0.1.0 |

---

## Ownership

| Layer | Owner |
|---|---|
| `adx_engine.*` source · bugs · updates | Rey (Clapp · Mac-side) |
| `EngineInput` builder (DB → engine) | Prudhvi |
| `_legacy_run_audit` fallback path | Prudhvi (already exists) |
| Customer-facing UI for `/playbook/{id}` link | Prudhvi |
| Schema additions (`adx_playbook_url`) | Prudhvi (1-line change) |

Questions or concerns · reply on this PR · I'll draft the `_build_engine_input` mapper against your exact DB schema if useful.
