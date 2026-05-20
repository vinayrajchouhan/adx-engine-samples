# AdX · Sample Expert Playbooks · live demo

> **📘 Engine docs · single source of truth:** [`ARCHITECTURE.md`](ARCHITECTURE.md) (strategic · 16-page map · 259 evaluators · 36 agents · 5 evaluation paths · FAQ) · [`PAGE_MAPPING.md`](PAGE_MAPPING.md) (field-level data flow per page · 20 quality gates · empty-state behavior) · [`EVALUATORS.md`](EVALUATORS.md) (all 259 checks ID-by-ID) · [`INTEGRATION.md`](INTEGRATION.md) (3-change spec) · [`PRUDHVI_BUILD_ENGINE_INPUT.py`](PRUDHVI_BUILD_ENGINE_INPUT.py) (drop-in adapter).

**3 ways to see what AdX builds · pick your time budget:**

| # | Path | Time | What you see |
|---|---|---|---|
| **1** | [Live GitHub Pages](https://vinayrajchouhan.github.io/adx-engine-samples/samples/anon-skincare-de.html) | **5 seconds** | Open URL · scroll through a real 16-page Playbook in your browser |
| **2** | Clone + run locally (instructions below) | **5 minutes** | Generate a fresh Playbook on your machine for any brand input you choose |
| **3** | Embed in pm_agency staging | **30-60 minutes** | Run a real audit through your existing `/audit/run` endpoint · see Playbook delivered via your infra |

---

## Path 1 · Live demo · zero setup

Click any of these · they're real HTML rendered in your browser via GitHub Pages:

- [anon-skincare-de.html](https://vinayrajchouhan.github.io/adx-engine-samples/samples/anon-skincare-de.html) · €25K/mo subscription brand · 4 platforms · €7,010/mo recoverable
- [anon-supplements-us.html](https://vinayrajchouhan.github.io/adx-engine-samples/samples/anon-supplements-us.html) · $40K/mo US supplements · 14 findings · $12,425/mo recoverable
- [anon-fintech-in.html](https://vinayrajchouhan.github.io/adx-engine-samples/samples/anon-fintech-in.html) · India lead-gen · ₹120K/mo · ₹48,360/mo recoverable
- [anon-food-au.html](https://vinayrajchouhan.github.io/adx-engine-samples/samples/anon-food-au.html) · Australian food brand · Google-only · A$4,290/mo recoverable
- [anon-fitness-ca.html](https://vinayrajchouhan.github.io/adx-engine-samples/samples/anon-fitness-ca.html) · Canadian boutique fitness · already healthy · 5 findings only

Each is the actual HTML the customer receives. Scroll · this is what comes out of the engine.

---

## Path 2 · Local 5-minute demo · see fresh generation

Accept the invite at https://github.com/poornagurram/adx-engine/invitations (Vinay sent this) · then:

```bash
git clone git@github.com:vinayrajchouhan/adx-engine.git
cd adx-engine
pip install -e .
```

Save this as `demo.py`:
```python
from adx_engine import ship_playbook
from adx_engine.schemas import EngineInput, MetaAdsData, GoogleAdsData, ShopifyData

# Pick any test brand · these are the inputs your _build_engine_input() would produce
eng = EngineInput(
    brand_id="demo-prudhvi-test",
    brand_name="Demo Brand",
    conversion_goal="sales",
    primary_geo="US",
    audit_window_days=90,
    meta=MetaAdsData(
        account_id="act_demo",
        monthly_spend=10000,
        pixel_diagnostics={
            "purchase_events_count": 120,
            "backend_conversions": 165,
            "event_match_quality": 5.4,
            "status": "active",
        },
        capi_status={"event_match_quality": 5.4, "purchase_events_count": 115},
        creative_performance=[
            {"name": "UGC-A", "frequency": 3.8, "hook_rate": 0.24, "spend": 3500},
            {"name": "Brand-Hero", "frequency": 2.9, "hook_rate": 0.31, "spend": 2800},
        ],
        ad_sets=[
            {"name": "LAL-1%", "spend": 5500, "frequency": 3.4, "reach_pct": 0.72},
            {"name": "Retargeting", "spend": 4500, "frequency": 5.1, "reach_pct": 0.91},
        ],
        campaigns=[{"name": "Acquisition"}, {"name": "Retargeting"}],
    ),
    shopify=ShopifyData(
        store_url="demo.myshopify.com",
        cart_funnel={"cart_to_checkout_rate": 0.24, "checkout_to_purchase_rate": 0.68},
    ),
)

result = ship_playbook(eng)
print(f"ok: {result.ok}")
print(f"findings: {result.findings_count}")
print(f"score: {result.report.overall_score}/100")
print(f"recoverable: ${result.report.total_recoverable_usd:,.0f}/mo")
print(f"\nHTML: {result.html_path}")
print(f"PDF:  {result.pdf_path}")
print(f"\nOpen the HTML in your browser to see the full 16-page Playbook.")
```

Run it:
```bash
python demo.py
open $(python -c "from adx_engine import ship_playbook; from adx_engine.schemas import EngineInput, MetaAdsData; r=ship_playbook(EngineInput(brand_id='t',brand_name='Test',conversion_goal='sales',primary_geo='US',audit_window_days=90,meta=MetaAdsData(account_id='a',monthly_spend=10000,pixel_diagnostics={'event_match_quality':5})));print(r.html_path)")
```

**Expected output:** `ok: True · findings: 12-14 · score: 50-65 · HTML at /customers/demo-prudhvi-test/runs/{id}/playbook.html` · opens in your browser showing the 16-page Playbook.

This is **the engine running on your machine** · same behavior it would have inside pm_agency.

---

## Path 3 · Embed in pm_agency staging · the real test

Full spec in [pm_agency#481](https://github.com/poornagurram/pm_agency/issues/481). Summary:

1. Add `adx-engine` to your `requirements.txt`
2. In `services/audit/engine.py` · wrap your existing `run_audit` body with a try-AdX-except-fallback-to-legacy pattern (~8 lines)
3. In `api/main.py` · mount the viewer route (1 line)

Try/except guarantees zero customer-impact if anything goes wrong · your existing legacy engine fires as fallback.

---

## What is AdX (the product, not the code)

**One sentence:** On-demand Expert Performance Marketing Playbook · $49 founder pricing · DTC founders connect ad accounts → receive a 16-page Expert Playbook in 3 minutes.

**Why it exists:** existing options are agency audits (slow, expensive, generic) or LLM-chat (fast, but can't rank by $ impact · no memory · no sequencing). AdX sits between · fast + specific + memory-compounding.

**Two products, one ladder:**

| Product | Price | Role | Who |
|---|---|---|---|
| **AdX** | $99 ($49 founder) | The wedge | DTC founders · $5-30K/mo spend · agency-disappointed |
| **ClappX** | $999-2,999/mo | The ladder | Same brands · continuous monitoring · graduates from AdX |

**Funnel target:** 100 AdX → 25 ClappX trials → 10 ClappX subscriptions.

---

## What's on each of the 16 pages

| # | Page | What it shows |
|---|---|---|
| 1 | Cover | Hero leak $ + top 3 critical findings |
| 2 | Dimensions | Radar chart · 5 health scores (tracking · creative · audience · budget · funnel) |
| 3-5 | Top 3 deep dives | Each: 5 evidence rows · 3 ranked differential causes · recommended action |
| 6 | Warnings | Next 8-11 findings ranked by $ impact |
| 7 | Trajectory | Revenue line chart + waterfall of $ impact per finding |
| 8 | Competitive | Curated competitor set + vertical-specific winning hook patterns |
| 9 | Scale moves | 5 ranked scale moves to ship once findings addressed |
| 10 | Intel briefing | Platform updates (Meta · Google · AI search) relevant to this brand |
| 11 | Action plan | 3 priority bands · sequenced fixes by $ recoverable |
| 12 | **Creative + Audience Pulse** | Per-creative verdict table (WINNING/FATIGUED/KILL/SCALE) + per-audience verdicts |
| 13 | Creative angles | 3 concept directions to ship next |
| 14 | Budget allocation | Current vs recommended channel mix |
| 15 | AI Visibility | SEO/AEO/GEO/AIV scores · buyer-query tests |
| 16 | What's next | Launch sequence + re-run cadence + ClappX upsell |

---

## Engine internals · 36 sub-agents in 6 layers

| Layer | What | Count |
|---|---|---|
| **L1 Data** | Ingest · enrich (vertical · benchmark · festival · history) | 7 |
| **L2 Engine** | 259 forensic signals across Meta · Google · GA4 · Shopify · cross-platform + scoring | 6 |
| **L3 Intelligence** | UX research · scale moves · stress test · competitive · intel · visibility · creative brief | 7 |
| **L4 Composer** | Context assembler · narrative · trust ratio · differential thinking · founder review · QA gate | 6 |
| **L5 Delivery** | Compose HTML · emit PDF · email · notification · scheduler | 5 |
| **L6 Feedback** | Customer memory · feedback loop · model evaluator · anonymizer · run history | 5 |

---

## Relationship to pm_agency

| | pm_agency engine | AdX engine |
|---|---|---|
| Designed for | ClappX continuous monitoring | $99 one-shot Playbook |
| Architecture | Backend-first · DB-heavy · multi-tenant SaaS | Output-first · Playbook-rendering · per-run |
| Output | AuditReport JSON (your existing schema) | 16-page HTML/PDF + AuditReport (matches your schema via adapter) |
| When to use | Continuous monitoring · long-term customer state | One-shot deep-dive · pre-ClappX wedge |

They're complementary. AdX produces the deliverable for the $99 wedge. pm_agency hosts the customer-facing flow + billing + auth + ClappX continuous-monitoring side. Both engines can coexist.

---

## Status · 2026-05-20

- Engine v0.1.5 · 259 evaluators wired · 36 agents · 16-page output
- 11-persona stress test passes (11 different #1 findings · currency-aware · vocab-locked)
- Uptik real Playbook validated (matches May-14 preliminary findings)
- Soft-launch target: this week (Uptik as first customer through new engine)
- Public launch: May 23-25

---

🤖 Maintained by Rey · acting on Vinay's direction. Reach Vinay direct for anything I missed.
