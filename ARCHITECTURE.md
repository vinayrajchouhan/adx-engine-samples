# AdX Engine · Architecture Reference

**Single source of truth · everything we built · how the 16-page Playbook maps to the engine + agents · how to integrate · v0.1.5 · 2026-05-20**

This doc supersedes the old `ARCHITECTURE.md` · `AGENT_MAP.md` · and any prior architecture notes in this repo. Anything that conflicts with this file is stale.

---

## TL;DR · in 3 lines

1. **Engine input:** a populated `EngineInput` dataclass (Meta + Google + GA4 + Shopify scan data)
2. **Engine output:** a 16-page Expert Playbook · HTML string (in-memory) or file on disk · plus an `AuditReport` Pydantic object matching pm_agency schema
3. **Integration:** in-memory · call `run_engine()` + `composer.render_playbook()` inside your existing `run_audit()` · zero raw-data persisted by our code

---

## 1 · Product context (intentionally brief)

**AdX engine** ships the deliverable for the $99 wedge product. **pm_agency engine** ships continuous monitoring (ClappX). Both engines coexist in the funnel. They serve different products.

---

## 2 · The 16-page output · Page-to-Agent + Page-to-Function map

Each page is rendered by a function in `composer.py` reading agent-filled slots from `PageContext`.

| Pg | Title | Renderer | PageContext slots | Agents that fill |
|---|---|---|---|---|
| 1 | Cover | `_page1_cover()` | `hero_leak`, `top_three[]`, `cover_stats_*`, `recoverable_summary`, `run_delta` | `context_assembler` ← `scoring` ← engine |
| 2 | Where problems live | `_page2_dimensions()` + `_radar_chart()` | `dimensions[]`, `category_breakdowns[]`, `dimensions_deck`, `checks_run_label` | `scoring.compute_score()` + `context_assembler` |
| 3-5 | Top 3 deep dives | `_critical_deep_dive(d, page_num)` (looped) | `critical_findings[]` (`FindingDeepDive`) | `context_assembler` + `differential_thinking.enforce_all()` |
| 6 | Warnings | `_page6_warnings()` | `warnings[]` (`WarningRow`), `holding_up_items[]` | `context_assembler` ← `ux_researcher` + engine |
| 7 | Trajectory | `_page7_trajectory()` + `_trajectory_line_chart()` + `_waterfall_chart()` | `trajectory_points[]`, `waterfall_steps[]` | `scoring.cumulative_recovery_trajectory()` + `context_assembler` |
| 8 | Competitive | `_page8_competitive()` | `competitive_headline`, `competitive_deck`, `where_you_win`, `competitive_set[]`, `hook_patterns[]` | `competitive_set.find_competitors()` + `find_hook_patterns()` + `detect_moat()` |
| 9 | Scale moves | `_page9_scale()` | `scale_moves[]` (`ScaleMove`) | `scale_moves.generate_scale_moves()` |
| 10 | Intel briefing | `_page10_intel()` | `platform_updates[]`, `watch_signals[]` | `intel_briefing.relevant_for_brand()` + `scale_moves.generate_watch_signals()` |
| 11 | Action plan | `_page11_action()` | `action_items[]` (`ActionItem`) | `context_assembler` (inline · 3 priority bands · sequenced by $ recoverable) |
| 12 | Creative + Audience Pulse | `_page12_copilot_intro()` | `creative_pulse_rows[]`, `audience_pulse_rows[]`, format/structure/next-concepts recs | `context_assembler` (per-creative + per-audience verdict logic) |
| 13 | Creative angles | `_page13_creative()` | `creative_angles[]` (`CreativeAngle`) | `creative_brief.generate_creative_angles()` |
| 14 | Budget allocation | `_page14_budget()` + `_budget_pie()` | `budget_allocations[]`, `budget_headline`, `budget_context_line` | `creative_brief.generate_budget_allocations()` |
| 15 | AI Visibility | `_page15_visibility()` + `_donut_chart()` × 4 | `visibility_scores[]`, `organic_fixes[]`, `buyer_queries[]` | `visibility_audit.assess_visibility_scores()` + `generate_organic_fixes()` + `generate_buyer_queries()` + `live_ai_visibility.build_visibility_profile()` |
| 16 | What's next | `_page16_strategic()` | `festive_phases[]`, `run_history_unlocks[]`, baseline message (from `run_delta`) | `festival_calendar.primary_festival_for()` + `context_assembler` |

**Final safety pass:** `_final_currency_sweep(html, currency_symbol)` runs on the entire HTML output · catches any bare `$NNN` that slipped past per-call scrubbing · only fires for non-USD brands.

---

## 3 · The engine · 259 forensic evaluators

| Platform | Count | Hand-coded (deep) | Bulk (scaffold) | Files |
|---|---|---|---|---|
| Meta | 84 | 42 | 42 | `taxonomy/meta.py` + `_meta_factory.py` + `_meta_bulk.py` |
| Google Ads | 100 | 2 | 98 | `taxonomy/google_ads.py` + `_google_bulk.py` |
| GA4 | 35 | 1 | 34 | `taxonomy/ga4.py` + `_ga4_bulk.py` |
| Shopify | 30 | 1 | 29 | `taxonomy/shopify.py` + `_shopify_bulk.py` |
| Cross-platform | 10 | 1 | 9 | `taxonomy/cross_platform.py` + `_xp_bulk.py` |
| **Total** | **259** | **47** | **212** | **259 wired · 0 unwired** |

**Full list of all 259 checks** with ID + name + category + tier + wired status → [`EVALUATORS.md`](EVALUATORS.md) (companion doc · 325 lines · auto-generated from registries).

**Category breakdowns (verified against `taxonomy/*.py` registries):**

| Platform | A | B | C | D | E | F | G | X |
|---|---|---|---|---|---|---|---|---|
| Meta · 84 | 16 (Tech Health) | 14 (Creative) | 13 (Audience) | 14 (Budget) | 7 (Structure) | 6 (Attribution) | 14 (Andromeda) | — |
| Google · 100 | 17 (Tech Health) | 15 (Creative/Copy) | 14 (Keyword/Targeting) | 19 (Budget/Bidding) | 12 (Structure) | 9 (Attribution) | 14 (AI-era) | — |
| GA4 · 35 | 30 (Tracking config) | — | 1 | 1 | 3 (Audience triggers) | — | — | — |
| Shopify · 30 | 7 (Tracking) | 5 (Creative/PDP) | 16 (LTV/Audience) | 2 (Inventory/Budget) | — | — | — | — |
| XP · 10 | — | — | — | — | — | — | — | 10 (Cross-platform) |

**Tier definitions:**
- T1 · simple detection · deterministic fix · automate fully
- T2 · simple detection · ambiguous fix · alert + recommend
- T3 · complex (multi-signal) · deterministic fix · automate detection + prescribe fix
- T4 · complex · ambiguous · alert + analyze · human decides

**Hand-coded vs bulk distinction:**
- **Hand-coded (47 evaluators)** · full data-signal trigger logic + custom evidence narrative + deep alternative-cause ranking · used where we have rich data shape
- **Bulk-generated (212 evaluators)** · canonical-depth scaffold from research files (Prudhvi's `pm_agency/research/ad_problem_taxonomy/`) · hash-distributed firing across category triggers to prevent mass-fire · each check has its own ID + name + category + tier from research
- Hand-coded get a 2x priority boost in `prioritize_findings()` so they outrank bulk when both fire (see § 8.4)

**Tier definitions:**
- T1 · simple detection · deterministic fix · automate fully
- T2 · simple detection · ambiguous fix · alert + recommend
- T3 · complex (multi-signal) · deterministic fix · automate detection + prescribe fix
- T4 · complex · ambiguous · alert + analyze · human decides

Each evaluator returns a `DetectedProblem` (Pydantic · `schemas.py:43`) with: `problem_id`, `category`, `tier`, `severity`, `impact_estimate`, `effort`, `priority_score`, `evidence`, `evidence_narrative`, `urgency_reason`, `recommended_action`, `expected_improvement`, `alternative_causes[]`, `source_tag`, `detection_confidence`, plus dimension/domain tags.

**Priority math:** `priority_score = severity × impact_estimate / max(effort, 1)`. Hand-coded evaluators get a 2x multiplier (so they outrank bulk-research findings when both fire).

---

## 4 · The 36 sub-agents · 6 layers

```
EngineInput (dict from pm_agency scanner)
   │
   ▼
L1 · Data ingest + enrich          (7 agents)
   ▼
L2 · Engine scan                   (6 modules · 5 taxonomy + scoring)
   ▼
L3 · Intelligence                  (9 agents · including 2 v0.1.5 additions)
   ▼
L4 · Composition                   (6 agents)
   ▼
L5 · Delivery                      (5 agents · composer + 4 in /agents/)
   ▼
L6 · Feedback / memory             (4 agents · run_history folded into context_loader)
```

### L1 · Data ingest + enrich (7 agents)

| Agent | File | Entry function(s) | Role |
|---|---|---|---|
| `data_ingest` | `agents/data_ingest.py` | `ingest_live(req)`, `ingest_from_fixture()`, `validate_engine_input()` | Contract for live API pulls · v1 stub · your scanner already does this |
| `data_fallback` | `agents/data_fallback.py` | `apply_fallbacks(eng)`, `is_signal_sufficient(eng)` | Fills missing fields with safe defaults · ensures engine never crashes on partial data |
| `operational_context_intake` | `agents/operational_context_intake.py` | `infer_from_signals(eng_dict)` | Brand-side org context (team size · ad-ops owner · decision authority) · informs realism of scale moves |
| `vertical_classifier` | `agents/vertical_classifier.py` | `classify(eng)`, `audience_groups(eng, vertical)`, `infer_conversion_goal(eng)`, `language(goal)` | Brand-name/industry keywords → vertical bucket (`dtc_food`, `dtc_apparel`, `saas_b2b`, etc.) |
| `benchmark_library` | `agents/benchmark_library.py` | `get(vertical, metric_key)`, `vertical_specific(vertical)` | Vertical-specific industry benchmarks (CTR · CVR · CPM by vertical+region) |
| `festival_calendar` | `agents/festival_calendar.py` | `primary_festival_for(audience, geo)`, `upcoming_festivals(audience, geo, window_days)` | Geo+vertical festive event timing (Diwali · Black Friday · Eid · etc.) · 62 events · 13+ countries |
| `context_loader` | `agents/context_loader.py` | `save_run(eng, report)`, `load_prior_run(brand_id)`, `list_run_history(brand_id)`, `compute_delta(eng, current_report)` | Loads prior-run history · computes delta (closed/new/drifting findings) · enables compounding intelligence |

### L2 · Engine scan (6 modules)

| Module | File | Entry function | Role |
|---|---|---|---|
| `meta_check_engine` | `taxonomy/meta.py` | `evaluate_meta(data)` | Runs all 84 Meta evaluators · returns `DetectedProblem[]` |
| `google_check_engine` | `taxonomy/google_ads.py` | `evaluate_google(data)` | Runs all 100 Google evaluators |
| `ga4_check_engine` | `taxonomy/ga4.py` | `evaluate_ga4(data)` | Runs all 35 GA4 evaluators |
| `shopify_check_engine` | `taxonomy/shopify.py` | `evaluate_shopify(data)` | Runs all 30 Shopify evaluators |
| `cross_platform_check_engine` | `taxonomy/cross_platform.py` | `evaluate_cross_platform(eng)` | Runs all 10 XP attribution checks |
| `scoring` | `scoring.py` | `compute_score()`, `prioritize_findings()`, `cap_recoverable_at_spend()`, `categorize_findings()`, `compute_recoverable()`, `cumulative_recovery_trajectory()` | Score · prioritize top-N (cluster-deduped) · cap recoverable at 80% of spend |

### L3 · Intelligence (9 agents)

| Agent | File | Entry function(s) | Role |
|---|---|---|---|
| `ux_researcher` | `agents/ux_researcher.py` | `generate_ux_findings(eng, vertical)`, `assess_catalog_complexity()`, `infer_brand_voice()`, `summary_for_intel()` | UX-side findings (cart friction · PDP completeness · founder-story · mobile speed) |
| `scale_moves` | `agents/scale_moves.py` | `generate_scale_moves(eng, report, vertical)`, `generate_watch_signals(eng, report)` | 5 ranked scale moves once core findings closed · 3 watch signals · vertical + spend-tier aware |
| `stress_test` | `agents/stress_test.py` | `generate_stress_scenarios(eng, report)` | CPM ±50%/+100%/-25% scenarios · stress-test recoverable math · B2B variant uses CPL stress against LTV/CAC ratio |
| `competitive_set` | `agents/competitive_set.py` | `find_competitors(eng, vertical)`, `find_hook_patterns(vertical)`, `detect_moat(eng, report, vertical)` | Curated competitor library + hook patterns by vertical/geo + structural moat detection · 4-tier fallback chain |
| `intel_briefing` | `agents/intel_briefing.py` | `relevant_for_brand(brand_context, max_count)` | Platform updates relevant to brand (Andromeda · iOS ATT · Perplexity Shopping · etc.) · 20+ items in `RECENT_UPDATES` |
| `visibility_audit` | `agents/visibility_audit.py` | `assess_visibility_scores(eng, vertical)`, `generate_organic_fixes(eng, vertical, scores)`, `generate_buyer_queries(eng, vertical, audience)` | SEO/AEO/GEO/AIV scoring (synthetic v1 baseline · live wiring via `live_ai_visibility`) |
| `creative_brief` | `agents/creative_brief.py` | `generate_creative_angles(eng, report, vertical, hook_patterns, themes)`, `generate_budget_allocations(eng, report)`, `generate_path_scenarios(eng, report)` | 3 creative angles + budget allocation recommendations + path scenarios |
| **`live_ai_visibility`** *(v0.1.5)* | `agents/live_ai_visibility.py` | `build_visibility_profile(queries, brand_domain, brand_name, engines)`, `query_google_serp()`, `query_bing_serp()`, `query_perplexity()`, `generate_buyer_queries(vertical, geo, goal)` | Live SERP scraper · Google AI Overview detection · Bing Copilot · Perplexity citation scrape · rate-limited 1.5s between calls |
| **`organic_search_ingest`** *(v0.1.5)* | `agents/organic_search_ingest.py` | `ingest_organic(req)`, `derive_aeo_geo_scores(data)`, `quick_diagnostic(data)` | Search Console + Bing Webmaster + AI-mention contract · stub default · live wiring in v0.2 |

### L4 · Composition (6 agents)

| Agent | File | Entry function(s) | Role |
|---|---|---|---|
| `context_assembler` | `agents/context_assembler.py` | `assemble(eng, report) -> PageContext` | The L3→L4 spine · turns engine output + L3 agent outputs into populated `PageContext` for all 16 pages |
| `narrative_writer` | `agents/narrative_writer.py` | `narrative_for_finding(p)`, `page_intro(section, findings)`, `deep_dive_lead(finding)` | Evidence narrative + page intros from finding structure (v1 deterministic · v2 LLM polish) |
| `trust_ratio_enforcer` | `agents/trust_ratio_enforcer.py` | `enforce(findings) -> TrustReport` | Enforces ≥85% sourced claims (D/E/R/O/A tags) · ≤15% LLM-creation (L tag) |
| `differential_thinking` | `agents/differential_thinking.py` | `ensure_differential(finding)`, `enforce_all(findings)` | Guarantees every finding ships with ≥3 ranked alternative causes (HIGH/MED/LOW confidence) |
| `founder_review` | `agents/founder_review.py` | `run_founder_review(ctx) -> FounderReview`, `format_founder_review(review)` | Senior-PMM lint pass · 6 heuristic checks (credibility · priority · specificity · trajectory realism · tone · festive applicability) |
| `qa_gate` | `agents/qa_gate.py` | `run_qa_gate(ctx, rendered_html=None) -> QAReport`, `format_qa_report(report)` | 7-check QA pass (trust ratio · math reconciliation · banned words · vendor neutrality · placeholders · brand consistency · required slots) |

### L5 · Delivery (5 agents · `composer` lives at root)

| Agent | File | Entry function(s) | Role |
|---|---|---|---|
| `composer` | `composer.py` *(root · not in /agents/)* | `render_playbook(ctx) -> str`, `save_playbook(ctx, path) -> Path` | HTML render · 16 pages · cream/ink/orange brand template · returns string (in-memory) or writes file. Also exposes `_buyer_safe()` scrubber + 6 chart helpers |
| `pdf_emitter` | `agents/pdf_emitter.py` | `emit_pdf(html_path, output_path)`, `emit_via_system_chrome()` | HTML → A4 PDF · Chrome headless → Playwright → WeasyPrint fallback chain |
| `email_sender` | `agents/email_sender.py` | `send_playbook(req: EmailRequest) -> EmailResult`, `build_delivery_html()` | Branded delivery email via Zoho SMTP (when wired · needs `ZOHO_SMTP_USER/PASS` env) |
| `customer_notifier` | `agents/customer_notifier.py` | `notify_run_started(ctx)`, `notify_run_complete(ctx)`, `notify_run_failed(ctx, error)`, `notify_rerun_reminder(ctx)` | In-app + email notifications around run lifecycle |
| `run_scheduler` | `agents/run_scheduler.py` | `enqueue(base, run)`, `pending_runs(base)`, `mark_running/complete/failed()`, `schedule_rerun(base, brand_id, cadence)` | Cadence-based re-run queue (weekly/biweekly/monthly/quarterly/on_demand) · file-backed |

### L6 · Feedback (4 agents · `run_history` folded into `context_loader`)

| Agent | File | Entry function(s) | Role |
|---|---|---|---|
| `customer_memory` | `agents/customer_memory.py` | `load_memory(base, brand_id)`, `save_memory(base, mem)`, `update_after_run()`, `mark_closed()`, `mark_wontfix()` | Per-brand accumulated `context.json` across runs · the moat vs ChatGPT+MCP |
| `feedback_loop` | `agents/feedback_loop.py` | `record_feedback(base, entry)`, `aggregate_signals(base)`, `write_tuning_report(base, path)` | Customer marks findings (closed/wontfix/retest/valuable/noisy) · aggregates per-check signals |
| `model_evaluator` | `agents/model_evaluator.py` | `evaluate(base, window_days)`, `write_report(base, path)` | Nightly eval pass · precision/recall per check · flags low-precision checks for tuning |
| `anonymizer` | `agents/anonymizer.py` | `scrub_text()`, `scrub_finding(d, mode)`, `scrub_brand_profile(p, mode)`, `k_anonymous_export(profiles, k_min=10)`, `hash_id(v)` | Light + hard scrub modes · k-anonymity ≥10 enforcement for aggregated benchmarks |

---

## 5 · Public API · the only functions you call

```python
from adx_engine import (
    # Engine core
    run_engine,                  # returns AuditReport · in-memory · use THIS for pm_agency
    
    # Orchestrator (writes files · DON'T use for pm_agency · use lower-level pieces)
    ship_playbook,               # sync · full chain · writes HTML + PDF
    ship_playbook_async,         # async wrapper · for FastAPI
    deliver_playbook,            # ship + email + memory + scheduler
    ShipResult, DeliverResult,
    
    # Adapter
    to_legacy_audit_report,      # ShipResult → pm_agency AuditReport dict
    
    # FastAPI viewer mount (optional)
    register_playbook_routes,    # mounts /playbook/{run_id} · auth_dependency=Depends(...)
    
    # Schemas
    EngineInput, AuditReport, DetectedProblem,
    
    # Utilities
    set_logger,                  # route adx_engine.* logs through your logger
    __version__,                 # "0.1.5"
    SCHEMA_VERSION,              # "0.1.0"
)

# Lower-level pieces (for in-memory integration · skip the orchestrator)
from adx_engine.agents import context_assembler
from adx_engine import composer
from adx_engine.schemas import MetaAdsData, GoogleAdsData, GA4Data, ShopifyData
from adx_engine.orchestrator import ShipResult
```

**Adapter signature:**
```python
to_legacy_audit_report(
    ship_result: ShipResult,
    brand_id: UUID | str,
    *,
    audit_id: Optional[UUID] = None,
    currency: str = "USD",
    currency_symbol: str = "$",
    market: str = "us",
    monthly_spend: Optional[float] = None,
    audit_window_days: Optional[int] = None,
) -> dict  # matches pm_agency.schemas.audit.AuditReport Pydantic shape
```

**Viewer signature:**
```python
register_playbook_routes(
    app: FastAPI,
    mount_path: str = "/playbook",
    auth_dependency=None,  # pass Depends(get_current_user) to gate
) -> None
```

---

## 6 · In-memory integration (your case · zero persistence)

### 6.1 · Schema gap · your `scan_data` vs our `EngineInput`

**Honest disclosure before the code:** your pm_agency `scan_data` is a **flat aggregate dict** with keys like `meta_spend`, `meta_cpa`, `meta_roas`, `meta_avg_frequency`, `meta_fatigue_replace_now`, `meta_health_score`, `google_total_campaigns`, etc. (verified against `pm_agency/backend/src/services/audit/engine.py`).

Our `EngineInput` expects **nested per-creative + per-adset arrays** like `creative_performance: [{name, frequency, hook_rate, spend}, ...]` and `ad_sets: [{name, spend, frequency, reach_pct}, ...]`.

**These don't line up directly.** Three resolution paths:

| Path | What it requires | Cost |
|---|---|---|
| **A · Extend your scanner** (recommended) | Your `_scan_and_diagnose_meta` adds 2-3 fields: `meta_top_creatives` (list of 5-10 creative dicts) + `meta_top_adsets` (list of 5-10 adset dicts) + `meta_campaigns_list` (list of campaign names) · pull from Meta `/adcreatives` and `/adsets` endpoints which your scanner already touches | ~1-2 hours · existing API surface |
| **B · Engine works on aggregates only** | Our engine produces fewer/coarser findings · we lose per-creative verdicts on Page 12 · audience pulse becomes generic · ~60% of value | Free · degraded output |
| **C · Engine calls Meta directly** | Bypass your scan_data · we call Meta API ourselves from within `_build_engine_input` · adds OAuth complexity our side · breaks our "stateless · no API auth in engine" design | Avoid · breaks separation of concerns |

**My recommendation: Path A.** You extend your scanner once · we both benefit (your existing engine can also use the richer data later for ClappX evolution).

### 6.2 · The integration code (assuming Path A · extended scan_data)

```python
# In your services/audit/engine.py
from adx_engine import run_engine, to_legacy_audit_report
from adx_engine.agents import context_assembler
from adx_engine import composer
from adx_engine.orchestrator import ShipResult
from adx_engine.schemas import EngineInput, MetaAdsData

async def run_audit(brand_id, current_user, session, meta_account_id, google_account_id):
    try:
        # 1. Your existing scanner pulls live · returns dict in memory
        scan_data = await _scan_and_diagnose_meta(session, brand_id, meta_account_id, {})
        # scan_data has YOUR existing flat aggregate keys (meta_spend, meta_cpa, etc.)
        # PLUS new fields you'd add for full integration: meta_top_creatives, meta_top_adsets, meta_campaigns_list
        
        # 2. Map dict → EngineInput (pure function · in-memory · ~30 lines)
        eng = EngineInput(
            brand_id=str(brand_id),
            brand_name=brand.name,
            conversion_goal=brand.conversion_goal or "sales",
            primary_geo=brand.market or "US",
            audit_window_days=90,
            meta=MetaAdsData(
                account_id=meta_account_id,
                monthly_spend=float(scan_data.get("meta_spend", 0)),
                pixel_diagnostics={
                    # Use whatever YOUR scanner produces · these are example field names
                    "purchase_events_count": scan_data.get("meta_purchases_pixel", 0),
                    "backend_conversions": scan_data.get("meta_backend_conversions", 0),
                    "event_match_quality": scan_data.get("meta_emq_score", 0),
                    "status": scan_data.get("meta_pixel_status", "active"),
                    # Aggregate signals you already have:
                    "fatigue_replace_now": scan_data.get("meta_fatigue_replace_now", 0),
                    "fatigue_refresh_soon": scan_data.get("meta_fatigue_refresh_soon", 0),
                    "avg_frequency": scan_data.get("meta_avg_frequency", 0),
                    "stuck_adsets": scan_data.get("meta_stuck_adsets", 0),
                },
                capi_status={"event_match_quality": scan_data.get("meta_emq_score", 0)},
                creative_performance=scan_data.get("meta_top_creatives", []),   # ← Path A: you add this
                ad_sets=scan_data.get("meta_top_adsets", []),                   # ← Path A: you add this
                campaigns=scan_data.get("meta_campaigns_list", []),             # ← Path A: you add this
            ),
        )
        
        # 3. Run engine · in-memory · no file write
        report = run_engine(eng)
        
        # 4. Compose Playbook HTML as string · in-memory · no file write
        ctx = context_assembler.assemble(eng, report)
        html_string = composer.render_playbook(ctx)
        
        # 5. Convert to pm_agency AuditReport Pydantic shape · in-memory
        legacy_dict = to_legacy_audit_report(
            ShipResult(ok=True, report=report, html_path=None, pdf_path=None),
            brand_id=current_user.brand_id,
            currency=brand.currency or "USD",
            currency_symbol={"USD":"$","GBP":"£","EUR":"€","AUD":"A$","INR":"₹","CAD":"C$"}.get(brand.currency, "$"),
            market=brand.market or "us",
        )
        
        # 6. Return both · caller serves HTML via HTTPResponse · no disk
        return legacy_dict, html_string
        
    except Exception as e:
        logger.warning("adx engine failed · using legacy", exc_info=e)
        return await _legacy_run_audit(brand_id, current_user, session,
                                        meta_account_id, google_account_id)
```

**If you go Path B (aggregates only):** skip the `creative_performance / ad_sets / campaigns` lines. Engine still runs · produces 5-10 findings instead of 14 · Page 12 Creative Pulse falls back to "Connect creative-level data to unlock per-concept verdicts" empty-state.

**Privacy guarantee:** the only thing our engine reads is the `EngineInput` you pass. The only thing it writes (via `composer.render_playbook()`) is an HTML string in memory. Files are written ONLY if you call `ship_playbook()` orchestrator (you don't · you call the lower-level pieces).

---

## 7 · Privacy + compliance

| Data | Our engine's behavior |
|---|---|
| Raw Meta/Google ad spend · per-creative metrics · per-adset frequency | Read once · in-memory · GC at request end |
| Pixel diagnostics · EMQ · CAPI status | Same · in-memory only |
| Customer email · brand_id · account IDs | Pass-through in dict · we don't extract or store |
| Findings (`AuditReport.detected_problems`) | Returned to caller · caller decides persistence |
| HTML output | Returned as string · caller decides persistence |
| Optional file-write paths | Only via `ship_playbook()` orchestrator (which you DON'T call in your integration) |

The orchestrator writes files. **You bypass it entirely.** Call `run_engine()` + `composer.render_playbook()` directly · zero file writes from our code.

---

## 8 · Engine internals · 8 critical design decisions

### 8.1 · `RecoverableSummary` single-source-of-truth

Every `$ recoverable` number across the 16 pages comes from ONE place: `ctx.recoverable_summary` (computed by `context_assembler._compute_recoverable_summary()`). Prevents divergence between hero leak ($3,290) and cover stats ($4,675).

```python
@dataclass
class RecoverableSummary:
    total: float                # always · headline number
    ad_spend: float             # capped at 80% of monthly_spend
    revenue: float              # uncapped · funnel-side gains
    monthly_spend: float
    pct_of_spend: int
    has_split: bool             # true if both ad_spend AND revenue > 0
    headline_label: str         # "$3,054/mo"
    type_qualifier: str
    cover_stat_label: str
```

### 8.2 · 80% spend cap on recoverable

`scoring.cap_recoverable_at_spend(recoverable, monthly_spend, cap_pct=0.80)` enforces that ad-spend-side recoverable can never exceed 80% of monthly spend. Revenue uplift recoverable stays uncapped. Memory lock: "ad-spend savings capped 80% of spend · revenue uplift uncapped (both shown separately)".

### 8.3 · Currency-aware rendering (6 currencies)

`context_assembler._currency_for_eng(eng)` maps `primary_geo` → currency symbol:
- US/USA/CA-USD → `$`
- UK/GB → `£`
- DE/FR/ES/IT/NL/AT/EU → `€`
- AU → `A$`
- NZ → `NZ$`
- CH → `CHF`
- IN → `₹`

Plumbed through every renderer · final defense via `_final_currency_sweep(html, currency_symbol)` that catches any bare `$NNN` that slipped past per-call scrubbing (only fires for non-USD brands).

### 8.4 · Hand-coded vs bulk · 2x priority boost

`scoring.prioritize_findings()` applies a 2x multiplier to `priority_score` for findings with `source_tag != "R"` (i.e., hand-coded over bulk-research). Prevents the engine from fixating on bulk evaluators that fire on shared category triggers (e.g., all 14 Cat-B Meta checks firing on the same fatigue signal).

### 8.5 · Cluster dedup

Same-cluster `(platform, category, subdomain)` findings deduped to top-priority only. Prevents seeing 5 budget-related findings when one is enough.

### 8.6 · `_buyer_safe()` centralized scrubber

Every render boundary passes through `composer._buyer_safe(text, currency_symbol)`. Strips:
- Internal IDs · `PROB-XXX`, `GPROB-XXX`, `GA4-PROB-XXX`, `SHOP-PROB-XXX`, `XP-PROB-XXX`, `UX-NNN`, `ORG-PROB-XXX`
- Banned nouns · "audit" (the noun · referring to our product · vocab lock) · "forensic"
- LLM filler · "leverage synergies", "best-in-class", "world-class", "cutting-edge", "revolutionary", "game-changing", "paradigm shift"
- Bare `$NNN` → `{currency_symbol}NNN` for non-USD brands

### 8.7 · Source-tagged claims · trust ratio enforcement

Every finding ships with a `source_tag`:

| Tag | Meaning |
|---|---|
| D | Data · directly from connected platform |
| E | Engine · deterministic check output |
| R | Research · from taxonomy / industry research |
| O | Observed · visible state from screenshots |
| A | Assumption · clearly marked estimate |
| L | LLM-creation · must stay ≤15% of claims |

`trust_ratio_enforcer.enforce()` blocks render if sourced ratio drops below 85%.

### 8.8 · Top-N prioritization · "fire all · surface top 14"

`scoring.prioritize_findings(findings, monthly_spend, top_n=14)` is the architecture for handling 259 evaluators firing:
1. Drop findings with `impact_estimate == 0`
2. Apply hand-coded 2x priority boost (8.4)
3. Cluster-dedup by `(platform, category, subdomain)` (8.5)
4. Sort by boosted priority
5. Take top 14 as `surfaced` · rest go to `deferred`
6. All scoring/recoverable math uses `surfaced` only (matches buyer view · prevents over-firing dilution)

---

## 9 · Schema reference

### EngineInput (full · verified against `schemas.py`)

```python
class EngineInput(BaseModel):
    brand_id: UUID | str
    brand_name: str = ""
    industry: str = ""
    business_model: str = ""

    # Goal · drives metric language, benchmarks, recommendations, event calendar
    conversion_goal: Literal["sales","leads","subscriptions","trials","bookings","downloads"] = "sales"

    primary_geo: str = "US"     # ISO-2 · drives currency + festive calendar

    # Optional target metrics
    target_cpa: float | None = None
    target_roas: float | None = None
    target_cpl: float | None = None
    aov: float | None = None
    typical_deal_size: float | None = None     # B2B context

    lifecycle_stage: Literal["launch","growth","mature","revival","unknown"] = "unknown"

    # Compliance · suppresses recommendations that would create platform risk
    regulated_category: Literal[
        "none","healthcare","supplements","financial",
        "alcohol","cannabis_cbd","adult_dating"
    ] = "none"

    # Channel mix · what brand ALREADY runs (informs scale_moves)
    runs_email_marketing: bool = False
    runs_sms_marketing: bool = False
    runs_organic_social: bool = False
    runs_affiliate: bool = False
    runs_influencer: bool = False

    # Platform data · at least ONE required
    meta: MetaAdsData | None = None
    google: GoogleAdsData | None = None
    ga4: GA4Data | None = None
    shopify: ShopifyData | None = None

    fast_mode: bool = False     # skip optional agents
    audit_window_days: int = 90
```

### Platform data shapes (full · verified)

```python
class MetaAdsData(BaseModel):
    account_id: str
    currency: str = "USD"
    monthly_spend: float = 0.0
    window_days: int = 90
    campaigns: list[dict] = []            # [{name, objective, status, ...}]
    ad_sets: list[dict] = []              # [{name, spend, frequency, reach_pct, ...}]
    ads: list[dict] = []                  # [{id, name, status, ...}] (optional)
    pixel_diagnostics: dict = {}          # {purchase_events_count, backend_conversions, event_match_quality, status, ...}
    capi_status: dict = {}                # {event_match_quality, purchase_events_count, active}
    creative_performance: list[dict] = [] # [{name, frequency, hook_rate, spend, similarity_score}]
    attribution_settings: dict = {}

class GoogleAdsData(BaseModel):
    account_id: str
    currency: str = "USD"
    monthly_spend: float = 0.0
    window_days: int = 90
    campaigns: list[dict] = []            # [{name, type, status, ...}]
    ad_groups: list[dict] = []
    keywords: list[dict] = []
    conversion_actions: list[dict] = []   # [{name, enhanced_conversions_enabled}]
    pmax_assets: list[dict] = []
    quality_scores: dict = {}

class GA4Data(BaseModel):
    property_id: str
    window_days: int = 90
    events_summary: dict = {}             # {purchase: {has_transaction_id, has_value, has_currency, has_items}, ...}
    conversion_paths: list[dict] = []
    landing_pages: list[dict] = []
    attribution_models: dict = {}

class ShopifyData(BaseModel):
    store_url: str
    currency: str = "USD"
    window_days: int = 90
    orders_summary: dict = {}
    cart_funnel: dict = {}                # {cart_to_checkout_rate, checkout_to_purchase_rate, ...}
    customer_ltv: dict = {}
    product_performance: list[dict] = []
```

### AuditReport (output contract)

Matches `pm_agency.schemas.audit.AuditReport` (Pydantic v2) when passed through `to_legacy_audit_report()`. Key fields:
- `id`, `brand_id` (UUID)
- `audit_score` (0-100), `audit_label` (excellent/good/warning/poor/critical)
- `platforms_audited[]`, `monthly_spend`, `currency`, `currency_symbol`, `market`
- `current_phase` (foundation/efficiency/scale/optimize)
- `retrospective` (RetrospectiveAnalysis), `quick_wins[]`, `current_problems[]`, `predicted_problems[]`
- `layer_health[]` (LayerHealthScore), `narrative_clusters[]`
- `top_action`, `next_steps[]`
- `total_problems_detected`, `total_risk_exposure`
- `adx_playbook_url`, `adx_short_id` (extras · requires `ConfigDict(extra="allow")` to pass through)

---

## 10 · PageContext component classes

Every dataclass in `page_context.py`:

| Class | Used by which page |
|---|---|
| `HeroLeak` | Page 1 cover |
| `TopThreeFinding` | Page 1 cover (×3) |
| `RecoverableSummary` | Page 1 + every page that shows $ |
| `RunDeltaCard` | Page 16 baseline (first run) or Page 1 (re-runs) |
| `DimensionRow` | Page 2 dimensions (×5 dimensions) |
| `CategoryCheckBreakdown` | Page 2 deck |
| `FindingDeepDive` | Pages 3-5 (×3 deep dives) |
| `DifferentialCause` | Pages 3-5 (×3 alt causes per deep dive) |
| `WarningRow` | Page 6 warnings |
| `HoldingUpItem` | Page 6 "what's holding up" |
| `TrajectoryPoint` | Page 7 line chart (today/30/90 etc.) |
| `WaterfallStep` | Page 7 waterfall |
| `CompetitorEntry` | Page 8 |
| `HookPattern` | Page 8 |
| `ScaleMove` | Page 9 |
| `WatchSignal` | Page 9 alerts |
| `PlatformUpdate` | Page 10 intel briefing |
| `ActionItem` | Page 11 action plan |
| `StressScenarioCard` | Page 11 stress test |
| `CreativeAngle` | Page 13 |
| `BudgetAllocation` | Page 14 (rendered with `_budget_pie`) |
| `PathScenario` | Page 14 path scenarios |
| `VisibilityScore` | Page 15 (×4 score donuts) |
| `OrganicFix` | Page 15 |
| `BuyerQueryResult` | Page 15 buyer-query results table |
| `FestivePhase` | Page 16 (×3 phases) |
| `RunHistoryUnlock` | Page 16 |

Plus inline fields like `creative_pulse_rows`, `audience_pulse_rows`, `creative_format_rec`, `creative_structure_rec`, `creative_next_concepts`, `audience_takeaway_expand`, `audience_takeaway_retire` for Page 12.

---

## 11 · File map · what's where

```
adx-engine/                          # private repo · vinayrajchouhan/adx-engine
├── pyproject.toml                   # pip-installable · v0.1.5
├── README.md                        # entry point (this doc supersedes details)
├── ARCHITECTURE.md                  # ← you're reading this · canonical
├── INTEGRATION.md                   # 3-change integration spec (referenced from issue #481)
├── PRUDHVI_BUILD_ENGINE_INPUT.py    # pre-written `_build_engine_input` mapper (drop-in)
└── adx_engine/
    ├── __init__.py                  # public API surface
    ├── pipeline.py                  # run_engine() · the core
    ├── orchestrator.py              # ship_playbook() · standalone (you DON'T use this)
    ├── composer.py                  # render_playbook() · HTML render · chart helpers · _buyer_safe
    ├── scoring.py                   # compute_score · prioritize_findings · cap_recoverable · etc.
    ├── schemas.py                   # EngineInput · AuditReport · DetectedProblem · platform data
    ├── page_context.py              # PageContext (16-page slot definitions · 30+ component classes)
    ├── adapters/
    │   ├── __init__.py
    │   └── pm_agency.py             # to_legacy_audit_report()
    ├── viewer/
    │   ├── __init__.py
    │   └── fastapi_router.py        # register_playbook_routes()
    ├── agents/                      # 30 agent files
    │   ├── data_ingest.py
    │   ├── data_fallback.py
    │   ├── operational_context_intake.py
    │   ├── vertical_classifier.py
    │   ├── benchmark_library.py
    │   ├── festival_calendar.py
    │   ├── context_loader.py
    │   ├── ux_researcher.py
    │   ├── scale_moves.py
    │   ├── stress_test.py
    │   ├── competitive_set.py
    │   ├── intel_briefing.py
    │   ├── visibility_audit.py
    │   ├── creative_brief.py
    │   ├── live_ai_visibility.py       # v0.1.5 NEW · Google/Bing/Perplexity scraper
    │   ├── organic_search_ingest.py    # v0.1.5 NEW · stub contract
    │   ├── context_assembler.py
    │   ├── narrative_writer.py
    │   ├── trust_ratio_enforcer.py
    │   ├── differential_thinking.py
    │   ├── founder_review.py
    │   ├── qa_gate.py
    │   ├── pdf_emitter.py
    │   ├── email_sender.py
    │   ├── customer_notifier.py
    │   ├── run_scheduler.py
    │   ├── customer_memory.py
    │   ├── feedback_loop.py
    │   ├── model_evaluator.py
    │   └── anonymizer.py
    └── taxonomy/                    # 259 evaluators across 5 platforms
        ├── _base.py                 # CheckSpec · Tier · EffortCategory · ActionType
        ├── meta.py + _meta_factory.py + _meta_bulk.py    # 84 Meta evaluators
        ├── google_ads.py + _google_bulk.py               # 100 Google evaluators
        ├── ga4.py + _ga4_bulk.py                         # 35 GA4 evaluators
        ├── shopify.py + _shopify_bulk.py                 # 30 Shopify evaluators
        └── cross_platform.py + _xp_bulk.py               # 10 XP evaluators
```

---

## 12 · Version history

| Tag | What shipped |
|---|---|
| **v0.1.5** *(current)* | Top-finding diversity boost · hand-coded 2x over bulk · cluster dedup uses boosted score · 7/11 unique top findings on test suite · Uptik real Playbook validated |
| **v0.1.4** | Trajectory + waterfall chart parsers currency-aware (£/€/A$/₹/C$) · all non-sales personas render charts |
| **v0.1.3** | Zero currency leaks across 4 personas · 3-layer defense (SVG charts · `_buyer_safe()` · `_final_currency_sweep()`) |
| **v0.1.2** | `saas_b2b` UK Page 8 fallback chain · 4-tier competitor lookup · zero TODO on edge verticals |
| **v0.1.1** | 4 self-review fixes · `max_seconds` actually implemented · auth-dependency on viewer route · `ship_playbook_async` for FastAPI · Linux env var compat |
| **v0.1.0** | Initial package · 259 checks · 36 agents · 16-page Playbook · pm_agency adapter + FastAPI viewer · INTEGRATION.md spec |

---

## 13 · How to evaluate · 5 paths

| Path | Time | What you see |
|---|---|---|
| **1 · GitHub Pages** | 5 seconds | https://vinayrajchouhan.github.io/adx-engine-samples/ · 5 real Playbooks · click any · scroll 16 pages |
| **2 · Sandbox demo** | 5 minutes | `mkdir ~/adx-sandbox && python3 -m venv venv && source venv/bin/activate && pip install git+https://github.com/vinayrajchouhan/adx-engine.git@v0.1.5` · run the demo one-liner · open generated HTML |
| **3 · `pm_to_adx` bridge** | 10 minutes | Your existing scanner dumps `scan_data` dict in-memory · standalone script in sandbox maps to `EngineInput` · runs engine · opens Playbook. **Zero pm_agency changes except one optional `json.dump` line.** |
| **4 · In-memory integration in staging branch** | 30 minutes | Apply the 3 changes in a throwaway `adx-engine-staging-test` branch · run staging server on port 8001 · test through real flow with Uptik or any test customer · `git branch -D` to discard |
| **5 · Production integration** | 60 minutes | Merge to main · deploy · monitor `/audit/run` for any failures · legacy fallback fires if anything breaks |

Recommended order: 1 → 2 → 3 → 4 → (decide on 5 after seeing 4).

---

## 14 · FAQ

**Q: Does this replace my engine?**
No. Yours is purpose-built for ClappX continuous monitoring (multi-tenant SaaS · DB-heavy · stateful). Ours is purpose-built for AdX wedge one-shot Playbook (output-first · per-customer per-run). Both coexist.

**Q: What if integration breaks something?**
Try/except wrapping ensures your legacy engine fires on any AdX failure. Customer sees current behavior. Zero downtime.

**Q: Does the engine require disk writes?**
No · if you use `run_engine()` + `composer.render_playbook()` directly (the in-memory path). Disk writes happen only via the `ship_playbook()` orchestrator (which you don't call).

**Q: Will it slow down my `/audit/run` endpoint?**
Engine runs ~1-3 seconds on Mac. Expect similar on Linux. We support `max_seconds=N` parameter to skip optional PDF render if you have a tight UI timeout.

**Q: GPL contamination?**
None. Engine is proprietary Clapp B.V. (private repo, MIT-style for internal use only). Public sample repo is MIT-licensed for samples only. We reviewed OpenOutreach (GPL-v3) for patterns but did NOT fork code · only adopted concepts (ICP-fit scoring, lifecycle state machine).

**Q: Why not just call my engine for everything?**
Yours is optimized for continuous monitoring. AdX needs different output (16-page rendered Playbook) and different runtime semantics (per-customer per-run stateless). One-engine-fits-both = compromise.

**Q: What happens to the `adx_playbook_url` field?**
Without `ConfigDict(extra="allow")` on your Pydantic schema, it's silently dropped. Either add the config OR return the HTML string back as a separate field in your API response (which the in-memory integration does anyway).

**Q: How do I see this running without committing to integration?**
Path 3 (the `pm_to_adx` bridge). Production untouched. You see real Playbook from real data. Decide after.

**Q: What if I want to fork the engine and own it?**
Talk to Vinay. Engine is private Clapp B.V. IP. License terms negotiable.

---

## 15 · Where things live · quick reference

- **Engine code (private · invite required):** https://github.com/vinayrajchouhan/adx-engine
- **Public samples + GitHub Pages live demo:** https://vinayrajchouhan.github.io/adx-engine-samples/
- **Integration issue + threaded discussion:** https://github.com/poornagurram/pm_agency/issues/481
- **This doc (canonical · public mirror):** [`ARCHITECTURE.md`](ARCHITECTURE.md) in [`adx-engine-samples`](https://github.com/vinayrajchouhan/adx-engine-samples)
- **All 259 evaluators · ID-by-ID:** [`EVALUATORS.md`](EVALUATORS.md)
- **Integration spec (3 code changes):** [`INTEGRATION.md`](INTEGRATION.md)
- **Pre-written adapter:** [`PRUDHVI_BUILD_ENGINE_INPUT.py`](PRUDHVI_BUILD_ENGINE_INPUT.py)

---

🤖 Maintained by Rey · acting on Vinay's direction · v0.1.5 · 2026-05-20

If anything's missing or wrong · reply on issue #481 · I correct same-day.
