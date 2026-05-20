# AdX Playbook · Page Mapping + Quality Gates

**Companion to [`ARCHITECTURE.md`](ARCHITECTURE.md) · field-level reference.**

If `ARCHITECTURE.md` is the strategic single-source-of-truth (read once, top to bottom), this doc is the **field-level reference** you keep open while wiring the integration. For every visible element on every page, you can trace: `visible UI → PageContext slot → agent → evaluator(s) → scan_data field(s) → fallback when missing`.

Two parts:
- **Part A · Quality Gates Catalog** — 20 gates that run between raw `scan_data` and final HTML. The moat. Read once.
- **Part B · Per-page mapping** — 16 sections, one per Playbook page, with 4 blocks each (visual elements · data flow table · quality gates applied · empty-state behavior).

Cross-refs: [`ARCHITECTURE.md`](ARCHITECTURE.md) (strategic) · [`EVALUATORS.md`](EVALUATORS.md) (all 259 check IDs) · [`INTEGRATION.md`](INTEGRATION.md) (wiring) · [`PRUDHVI_BUILD_ENGINE_INPUT.py`](PRUDHVI_BUILD_ENGINE_INPUT.py) (drop-in adapter).

---

## Part A · Quality Gates Catalog

Twenty gates fire between raw `scan_data` and final Playbook HTML. They're what separates a shippable product from internal debug output. **Do not bypass.**

### Canonical signatures · the only functions you call

Every entry-point function used during emission, with full type signature. Each is verified against source.

```python
# ── ENGINE ENTRY (you call these) ─────────────────────────────────────
def run_engine(eng: EngineInput) -> AuditReport
def ship_playbook(eng: EngineInput, max_seconds: int = 8) -> ShipResult
async def ship_playbook_async(eng: EngineInput, max_seconds: int = 8) -> ShipResult
def deliver_playbook(eng: EngineInput, ...) -> DeliverResult
def to_legacy_audit_report(ship: ShipResult, brand_id: str, currency_symbol: str = "$") -> AuditReport
def set_logger(logger: logging.Logger) -> None
def register_playbook_routes(app: FastAPI, auth_dependency: Callable | None = None) -> None

# ── ASSEMBLY (engine calls these · documented so you know the chain) ──
# pipeline.py
def run_engine(eng: EngineInput) -> AuditReport         # detects problems, scores, prioritizes

# scoring.py
def compute_score(findings: list[DetectedProblem],
                  platforms_connected: set[str] | None = None
) -> tuple[int, dict[str, int]]                          # → (overall_score, per_category_scores)

def prioritize_findings(findings: list[DetectedProblem],
                        monthly_spend: float,
                        top_n: int = 14
) -> tuple[list[DetectedProblem], list[DetectedProblem], dict]   # → (surfaced, deferred, stats)

def cap_recoverable_at_spend(recoverable: dict,
                             monthly_spend: float,
                             cap_pct: float = 0.80) -> dict      # G7 80% cap

def compute_recoverable(findings: list[DetectedProblem]) -> dict[str, float]   # G8 SOT
def cumulative_recovery_trajectory(findings: list[DetectedProblem]) -> dict[str, float]

# agents/context_assembler.py
def assemble(eng: EngineInput, report: AuditReport) -> PageContext

# composer.py
def render_playbook(ctx: PageContext) -> str             # → final HTML
def _buyer_safe(text: str, currency_symbol: str = "$") -> str          # G1
def _final_currency_sweep(html: str, currency_symbol: str) -> str      # G2

# ── PRE-EMISSION QUALITY GATES (engine calls these · do NOT skip) ─────
# agents/founder_review.py
def run_founder_review(ctx: PageContext) -> FounderReview            # G11 · returns 6 FounderCheckResult

# agents/qa_gate.py
def run_qa_gate(ctx: PageContext,
                rendered_html: str | None = None) -> QAReport         # G12 · returns 7 QACheckResult

# agents/differential_thinking.py
def enforce_all(findings: list[DetectedProblem]) -> list[DetectedProblem]   # G9

# agents/trust_ratio_enforcer.py
def enforce(findings: list[DetectedProblem]) -> TrustReport                  # G3

# agents/context_loader.py (run-history + delta)
def compute_delta(eng: EngineInput, current_report: AuditReport) -> RunDelta
def save_run(eng: EngineInput, report: AuditReport) -> Path
def load_prior_run(brand_id: str) -> dict | None

# agents/anonymizer.py (samples only · G20 · NEVER on customer Playbooks)
def hash_id(value: str, salt: str = "adx-clapp-2026") -> str
def scrub_text(text: str) -> str
def scrub_finding(finding_dict: dict, mode: str = "light") -> dict
def scrub_brand_profile(profile: dict, mode: str = "light") -> dict
```

**Pre-emission call order** (inside `ship_playbook()`):
```
  eng = EngineInput(...)
  → run_engine(eng) → AuditReport
  → differential_thinking.enforce_all(findings)        # G9
  → trust_ratio_enforcer.enforce(findings)             # G3
  → assemble(eng, report) → PageContext
  → founder_review.run_founder_review(ctx) → FounderReview     # G11 · 6 checks
  → composer.render_playbook(ctx) → str                 # G1 fires per-element inside; G2 fires last
  → qa_gate.run_qa_gate(ctx, rendered_html=html) → QAReport   # G12 · 7 checks
  → return ShipResult(ok=True, html=html, report=report, founder_review=fr, qa_report=qa)
```

If `FounderReview.critical_count > 0` OR `QAReport.hard_fails > 0` → `ship.ok = False` and the orchestrator surfaces the failure list. You can still inspect `ship.html_path` for debugging, but the file should not ship to a customer.

---



### Category 1 · Always-on global scrubbers (8)

| # | Gate | Where | Purpose | Failure behavior |
|---|---|---|---|---|
| G1 | `_buyer_safe(text, currency_symbol)` | `composer.py:81` | Strip banned vocab ("audit" · "forensic"), internal IDs (`UX-NNN`, `PROB-###`, `ORG-PROB`), personal names ("Prudhvi"), 30-day prescriptive timing. Currency normalization. | Returns scrubbed text. Silent — by design. |
| G2 | `_final_currency_sweep(html, currency_symbol)` | `composer.py:1563` | Last-pass: any bare `$NNN` that slipped past per-call scrubbing for non-USD brands → replaced with the brand's actual currency symbol. | Runs only when `currency_symbol != "$"`. |
| G3 | Trust ratio ≥ 85% | `agents/trust_ratio_enforcer.py` + QA gate | Every claim source-tagged D/E/R/O/A/L (Data · Engine · Research · Observed · Aggregate · LLM). Sourced (non-L) must ≥85%. | QA gate flag, optional fail. |
| G4 | Cluster dedup | `scoring.prioritize_findings()` | Findings sharing the same `category` + impact band cluster · only top-1 surfaces. Prevents 3 Meta-attribution findings stacking. | Lower-ranked siblings drop. |
| G5 | Top-N=14 prioritization | `scoring.prioritize_findings()` | Fire all 259 evaluators · surface top 14 by severity × $ recoverable. Pages 3-5 take rank 1-3 · Page 6 takes 4-14. | Findings beyond 14 stay in `report.detected_problems` for memory but don't render. |
| G6 | Hand-coded 2x boost | `scoring.prioritize_findings()` | Evaluators with `source_tag != "R"` (i.e. hand-coded, not bulk) get 2× priority weight. Prevents bulk-rules monopolizing top 3. | Bulk evaluators de-prioritized vs hand-coded. |
| G7 | 80% spend cap | `scoring.cap_recoverable_at_spend()` | `recoverable_per_finding ≤ 0.80 × monthly_spend`. Prevents "$50K recoverable" claims on $20K spend. | Recoverable clamped, logged. |
| G8 | `RecoverableSummary` single-source-of-truth | `scoring.compute_recoverable()` | All $ figures on cover, warnings, trajectory, action plan derive from the same `RecoverableSummary` object. Prevents page-to-page math drift. | Cross-page numbers stay consistent by construction. |

### Category 2 · Composition-time gates (6)

| # | Gate | Where | Purpose | Failure behavior |
|---|---|---|---|---|
| G9 | Differential thinking | `agents/differential_thinking.py` | Pages 3-5 (top 3 deep dives) MUST present 3 ranked differential causes per finding (`DifferentialCause` with HIGH/MED-HIGH/MEDIUM/LOW confidence). Forces engine to never claim single cause. | If <3 causes generated, fallback "INVESTIGATE" placeholder. |
| G10 | Narrative composition | `agents/narrative_writer.py:narrative_for_finding()` + `page_intro()` + `deep_dive_lead()` | Generates narrative prose for each finding + per-section page intros + deep-dive leads from structured finding data. NOT a hard gate — its output is the input to gates G11 (founder review) and G12 (QA banned-words check). Tone is enforced in templates, not as a runtime gate. | Falls back to `_fallback_narrative(p)` if structured fields are sparse. |
| G11 | Founder review · 6 gut-checks | `agents/founder_review.py` | `_credibility_check` · `_priority_check` · `_specificity_check` · `_trajectory_realism` · `_tone_alignment` · `_festive_math`. Pre-emission "would VRC ship this?" simulation. | Each gate returns `FounderCheckResult` with severity. Critical = block. |
| G12 | QA gate · 7 checks | `agents/qa_gate.py:run_qa_gate()` | `_check_trust_ratio` · `_check_math_reconciliation` · `_check_banned_words` · `_check_vendor_neutrality` · `_check_no_placeholders` · `_check_brand_consistency` · `_check_required_slots`. | Each returns `QACheckResult`. Hard fails block emission. |
| G13 | Vendor neutrality | `qa_gate._check_vendor_neutrality()` | No app/tool recommendations (Klaviyo, Triple Whale, judge.me etc.). Only capabilities referenced. Per locked rule. | Hard fail if vendor name detected outside allowed contexts (citations, competitors, platform context). |
| G14 | PageContext completeness | `qa_gate._check_required_slots()` | Every required slot for every page either has data OR falls to documented empty-state. No `None.attribute` runtime crashes. | Empty-state copy renders (see per-page tables below). |

### Category 3 · Domain-specific gates (4)

| # | Gate | Where | Purpose | Failure behavior |
|---|---|---|---|---|
| G15 | Vertical-specific selection | `agents/vertical_classifier.py` + `competitive_set.find_competitors()` + `creative_brief.generate_creative_angles()` | Page 8 competitors + Page 13 angles must match brand vertical. No "luxury watch" hook in a B2B SaaS Playbook. | 4-tier vertical lookup chain. Final fallback = "generic DTC" with degraded specificity warning. |
| G16 | Persona-fit consistency | `agents/creative_brief.py` | Before any persona-targeted artifact ships, cross-check every metric / CTA / $ / vocab fits the vertical's persona (e.g. apparel ≠ leads). | Vertical-mismatch errors block creative_angles. |
| G17 | Competitor discovery protocol · 6 phases | `agents/competitive_set.py` | Customer-agnostic · engine-driven · reproducible. Never LLM-recall competitors. Every Playbook ships with Discovery Method appendix. | 6-phase protocol failure → "competitor discovery pending" empty state. |
| G18 | Festival calendar overlay | `agents/festival_calendar.py:primary_festival_for()` | Page 16 phases must match brand's region + vertical festive calendar. India Diwali ≠ Australia Christmas. | If no festival in next 90 days, Page 16 phases section hides. |

### Category 4 · Output integrity (2)

| # | Gate | Where | Purpose | Failure behavior |
|---|---|---|---|---|
| G19 | `AuditReport` Pydantic validation | `schemas.py` at engine boundary | Every emission validates against `AuditReport` schema (matches your pm_agency contract). | Pydantic raises before HTML is returned to caller. |
| G20 | Anonymizer · sample-only | `agents/anonymizer.py:hash_id()` / `scrub_text()` / `scrub_finding()` / `scrub_brand_profile()` | Only fires when generating public samples. Hashes brand name, scrubs PII, replaces specific $ with banded ranges. **Never runs on customer-facing Playbooks.** | Two modes: `light` (brand-name + URL only) · `heavy` (also bands $ values). |

**Gate ordering at emission time:**
```
  scan_data
    → EngineInput (G19 partial)
    → run_engine() [evaluators fire]
    → G4 cluster dedup
    → G6 hand-coded boost
    → G5 top-N=14
    → G7 80% cap
    → G8 RecoverableSummary computed
    → context_assembler.assemble() → PageContext
    → G9 differential thinking
    → G10 narrative pass
    → G15-G18 domain gates per page
    → G11 founder review (6 checks)
    → render_playbook() → HTML
    → G1 _buyer_safe (per element, in-renderer)
    → G2 _final_currency_sweep (whole HTML)
    → G12 qa_gate (7 checks against rendered HTML)
    → G19 final AuditReport validation
    → return to caller
```

If you implement Path B (aggregates only · per ARCHITECTURE.md §6.1), gates G9, G15, G16 degrade gracefully — empty states render. Gates G1-G8, G10-G14, G19-G20 still fire normally.

---

## Part B · Per-page mapping

Each page below has 4 blocks:
1. **Visual elements** — what the viewer sees
2. **Data flow** — element → PageContext slot → agent → evaluator(s) → scan_data field
3. **Quality gates applied** — which of G1-G20 fire on this page
4. **Empty-state behavior** — what renders when required inputs are missing

All renderer functions live in `composer.py`. All PageContext dataclasses live in `page_context.py`. All agents live in `agents/`.

---

### Page 1 · Cover

**Renderer:** `_page1_cover(ctx)` · `composer.py:799`

**Visual elements:**
- Brand name + tagline (top)
- Hero leak: kicker · `$NNN/mo` amount · qualifier (e.g. "Revenue left on table · not ad-spend bleed") · confidence line
- Credibility callout (only shown if recoverable > 50% of spend · explains the math)
- Top 3 finding cards · each shows: rank · name · verdict tags · status tag (FIXABLE/PARTIAL/STRUCTURAL/TIME-BOUND) · impact label
- Cover stats strip (e.g. "9 platforms · 259 signals · 3 min")
- `RecoverableSummary` visual bar

**Data flow:**

| Visible element | PageContext slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Brand name · tagline | `hero_leak.brand_tagline` | `context_assembler` | — | `eng.brand_name` |
| Hero kicker | `hero_leak.headline_kicker` | `context_assembler` | derived from top finding category | top finding's category |
| Leak amount | `hero_leak.leak_amount_label` | `scoring` → `context_assembler` | aggregate of top-14 findings | `meta_spend`, `meta_fatigue_replace_now`, `meta_health_score`, `google_*` (Path A) OR aggregate `report.total_recoverable_usd` (Path B) |
| Qualifier line | `hero_leak.leak_qualifier` | `context_assembler` | category dominance heuristic | category mix of top-3 findings |
| Confidence line | `hero_leak.confidence_line` | `trust_ratio_enforcer` | trust ratio % | source tags D/E/R/O/A/L across top-14 |
| Credibility callout | `hero_leak.credibility_callout` | `context_assembler` | conditional render: `recoverable > 0.5 × spend` | computed in `assemble()` |
| Top finding rank N name | `top_three[N].name` | `scoring.prioritize_findings()` | top N of 259 (post G4/G5/G6/G7) | depends on which evaluator fires |
| Top finding rank N impact | `top_three[N].impact_label` | `scoring` | individual finding `recoverable_per_month_usd` | finding-specific |
| Top finding rank N status | `top_three[N].status_tag` | `context_assembler` | maps `verdict_class` (`fixable` / `partial_fixable` / `structural`) to badge | finding's `verdict_class` field |
| `RecoverableSummary` bar | `recoverable_summary` (full object) | `scoring.compute_recoverable()` | sum of top-14 capped at G7 80% | all detected_problems |

**Quality gates applied:** G1 (buyer_safe on all text), G2 (currency sweep), G4 (cluster dedup), G5 (top-N=14), G6 (hand-coded boost), G7 (80% cap), G8 (RecoverableSummary SOT), G9 (differential thinking for top-3), G11 founder `_credibility_check` + `_priority_check`, G12 `_check_required_slots` + `_check_no_placeholders`.

**Empty-state behavior:**
- No top findings detected (clean account) → "No critical issues found · Playbook shifts to scale-mode" + Page 9 (Scale Moves) becomes primary.
- Missing `eng.brand_tagline` → tagline line hides; rest renders normally.
- Recoverable = $0 → leak amount shows "—" · credibility callout hides · top-3 cards remain (using non-$ findings like tracking config).

---

### Page 2 · Where problems live (Dimensions)

**Renderer:** `_page2_dimensions(ctx)` · `composer.py:839` + `_radar_chart(dimensions)` · `composer.py:149`

**Visual elements:**
- Radar/spider chart · 5 dimensions plotted 0-100 (Tracking · Creative · Audience · Budget · Funnel)
- 5 dimension rows below the chart · each: name · status (HOLDING/BREAKING/DRIFTING/UNTAPPED) · status qualifier · severity band
- Category check breakdown deck (e.g. "22 checks · clean", "14 checks · 6 breaking")
- "X checks run" label

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Radar chart 5 axis scores | `dimensions[].severity_band` + numeric | `scoring.compute_score()` | category aggregates of all 259 | all platform scan_data |
| Dimension row name | `dimensions[N].name` | `scoring` | category constants (A-G + X) | — (fixed labels) |
| Dimension status | `dimensions[N].status` | `scoring.compute_score()` | category fail-rate thresholds | category fail-rate from evaluators |
| Status qualifier | `dimensions[N].status_qualifier` | `context_assembler` | top metric per dimension (e.g. ROAS, EMQ, frequency, cart-to-checkout %) | dimension-specific |
| Category breakdown row | `category_breakdowns[N]` | `scoring.compute_score()` | check_count per category, fail_count per category | evaluator results |
| Checks run label | `checks_run_label` | `scoring` | `len(detected_problems) + clean_checks` | engine output |

**Quality gates applied:** G1, G2, G5 (top-14 cap upstream), G7 (cap applied upstream), G12 `_check_math_reconciliation` (dimension scores must reconcile with category breakdowns).

**Empty-state behavior:**
- Single-platform connect (e.g. Meta only) → unconnected platforms shown grayed in radar with "Connect to unlock" label.
- All 5 dimensions HOLDING → chart shows solid healthy band · page narrative shifts to "Where you're strong" framing.

---

### Pages 3-5 · Top 3 deep dives

**Renderer:** `_critical_deep_dive(d, page_num, currency_symbol)` · `composer.py:900` · called 3× (once per top finding)

**Visual elements:**
- Page kicker (e.g. "CRITICAL · 01 OF 03 · FUNNEL COLLAPSE")
- Issue ID line · headline · share-of-leak share bar
- Stat row: recoverable · effort · confidence · sample size
- "What we found" narrative + bullets
- 5-row evidence table (canonical)
- 3 differential causes (HIGH / MED-HIGH / MEDIUM / LOW confidence)
- "Why it matters" closing
- Recommended action

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Page kicker | `critical_findings[N].page_kicker` | `context_assembler` | — | derived from finding category |
| Issue ID line | `critical_findings[N].issue_id_line` | `context_assembler` | finding's `problem_id` (then scrubbed by G1) | — |
| Headline | `critical_findings[N].headline` | `context_assembler` + `narrative_writer` | finding's `name` + first metric | finding-specific scan_data fields |
| Recoverable | `critical_findings[N].recoverable` | `scoring` | finding's `recoverable_per_month_usd` (G7-capped) | finding-specific |
| Effort | `critical_findings[N].effort` | `context_assembler` | finding's `effort_class` | finding metadata |
| Confidence | `critical_findings[N].confidence` | `trust_ratio_enforcer` | source-tag-derived confidence | finding's `source_tag` |
| Sample size | `critical_findings[N].sample_size` | `context_assembler` | finding's `sample_size` field | scan_data window |
| Share of leak | `critical_findings[N].share_of_leak` + `share_pct` | `scoring` | `finding.recoverable / report.total_recoverable` | — |
| What we found narrative | `critical_findings[N].what_we_found_narrative` | `narrative_writer` | finding's `evidence_lines` | finding-specific |
| Bullets | `critical_findings[N].what_we_found_bullets` | `narrative_writer` | finding's `evidence_lines` | — |
| 5-row evidence table | `critical_findings[N].evidence_detail_rows[]` | `context_assembler` | finding's `evidence_detail_rows` (canonical schema) | finding-specific (raw metrics) |
| 3 differential causes | `critical_findings[N].differential_causes[]` | `differential_thinking.enforce_all()` | candidate causes per finding | finding's `differential_candidates` |
| Why it matters | `critical_findings[N].why_it_matters` | `narrative_writer` | category impact mapping | — |

**Quality gates applied:** G1, G2, G9 (MANDATORY — 3 differential causes), G10 (narrative tone), G11 `_specificity_check` (no generic claims), G12 `_check_math_reconciliation`, `_check_no_placeholders`.

**Empty-state behavior:**
- <3 findings detected → only as many deep-dives as findings exist (1 or 2 pages instead of 3).
- Finding lacks `evidence_detail_rows` → fallback to derived rows from `metrics_observed` (lower richness).
- Finding lacks `differential_candidates` → `differential_thinking` synthesizes 3 generic causes with LOW confidence + flag.

---

### Page 6 · Warnings · What's holding you up

**Renderer:** `_page6_warnings(ctx)` · `composer.py:966`

**Visual elements:**
- "Next 8-11 warnings" header
- FIX warning rows · each: name · impact · effort · FIX action tag
- GROW play rows · each: name · impact · effort · GROW action tag (separate from FIX warnings)
- "What's holding you up" section · `holding_up_headline` (title) + list of HoldingUpItem strengths (e.g. "4.18× Meta ROAS · 2.7× above F&B median")
- `warnings_deck` (lede paragraph)

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Warning row N (FIX) | `warnings[N]` (`WarningRow`) | `context_assembler` | rank 4-14 from `scoring.prioritize_findings()` filtered to `action_tag == "FIX"` | finding-specific |
| Growth play N (GROW) | `growth_plays[N]` (`WarningRow`) | `context_assembler` | findings tagged `verdict_class` opportunity / GROW | finding-specific |
| Warning impact | `warnings[N].impact_label` | `scoring` | `finding.recoverable_per_month_usd` (G7-capped) | — |
| Warning effort | `warnings[N].effort_label` | `context_assembler` | finding's effort class | — |
| FIX/GROW tag | `warnings[N].action_tag` | `context_assembler` | finding's `verdict_class` | — |
| Holding-up section title | `holding_up_headline` | `context_assembler` | summary line | — |
| Holding-up item | `holding_up_items[].label` | `context_assembler._holding_up_signals()` (`context_assembler.py:1249`) | inverse of detected_problems (clean checks above benchmark) | full `report` + `eng` + classified vertical |
| Warnings deck | `warnings_deck` | `narrative_writer.page_intro()` | section lead | top warnings list |

**Quality gates applied:** G1, G2, G5 (rank 4-14), G7 (cap), G12 `_check_required_slots`.

**Empty-state behavior:**
- <8 warnings → only existing warnings render · "What's holding up" gets larger share of page.
- Zero strengths above benchmark → "What's holding up" section hides; page note reads "All warnings have actionable fixes — see Page 11."

---

### Page 7 · Trajectory

**Renderer:** `_page7_trajectory(ctx)` · `composer.py:1013` + `_waterfall_chart(steps, currency_symbol)` · `composer.py:271`

**Visual elements:**
- Revenue trajectory line chart · today → +N fixes → festive uplift → projected
- Waterfall chart · $ impact per finding (today → −X funnel fix → −Y email flow → end state)
- Stress-test scenario chips (SAFE / TIGHT / UNDERWATER bands)

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Trajectory point N label | `trajectory_points[N].label` | `scoring.cumulative_recovery_trajectory()` | sequenced fixes | top-14 ranked |
| Trajectory point N revenue | `trajectory_points[N].revenue_value` | `scoring.cumulative_recovery_trajectory()` | cumulative recovery + baseline revenue | `report.total_recoverable_usd`, `eng.shopify.aov_data` |
| Trajectory point N delta | `trajectory_points[N].delta` | `scoring` | per-step delta + festive overlay | `festival_calendar.primary_festival_for()` if relevant |
| Waterfall step label | `waterfall_steps[N].label` | `scoring` | top finding names abbreviated | — |
| Waterfall step value | `waterfall_steps[N].value` | `scoring` | per-finding $ recoverable | — |
| Stress scenario | `stress_scenarios[]` (`StressScenarioCard`) | `stress_test.generate_stress_scenarios()` | CPM ±20%, ±40% deltas applied to current ROAS/CAC | `eng.meta.monthly_spend`, `report.computed_metrics` |

**Quality gates applied:** G1, G2, G7 (cap applied upstream), G8 (RecoverableSummary SOT — every $ figure traces back), G11 `_trajectory_realism` check (no fantasy projections), G12 `_check_math_reconciliation`.

**Empty-state behavior:**
- No festive overlay in next 90 days → trajectory shows only fix-driven uplifts.
- Stress scenarios unstable (e.g. ROAS underwater at +20% CPM) → "UNDERWATER" band visible, narrative shifts to "fix first, scale second."

---

### Page 8 · Competitive

**Renderer:** `_page8_competitive(ctx)` · `composer.py:1052`

**Visual elements:**
- `competitive_headline` (page title) + `competitive_deck` (lede paragraph)
- 3-5 competitor entries · each: name · relationship (direct/adjacent/aspirational) · threat level · one-liner · notable strength · domain
- Hook patterns section · 3-5 pattern cards · each: pattern name · example quotes · why it works · use when

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Competitive headline | `competitive_headline` | `competitive_set.detect_moat()` + `narrative_writer` | vertical positioning analysis | `eng.brand.vertical` |
| Competitive deck | `competitive_deck` | `competitive_set` + `narrative_writer.page_intro()` | aggregate winner/loser metrics | benchmark library |
| Competitor N | `competitors[N]` (`CompetitorEntry`) | `competitive_set.find_competitors()` | 6-phase discovery protocol (G17) | `eng.brand.vertical` + `eng.primary_geo` |
| Hook pattern N | `hook_patterns[N]` (`HookPattern`) | `competitive_set.find_hook_patterns()` | curated patterns per vertical | vertical mapping |

**Quality gates applied:** G1, G2, G15 (vertical-specific), G17 (6-phase discovery — never LLM-recall), G18 not relevant.

**Empty-state behavior:**
- Vertical not in benchmark library → 4-tier fallback chain: exact vertical → parent category → "generic DTC" → curated "comparable scale brand" set. Visible "Discovery Method" appendix on Page 8 footer.
- <3 competitors found → renders existing; remaining slots show "Discovery in progress · refines on re-run."

---

### Page 9 · Scale moves

**Renderer:** `_page9_scale(ctx)` · `composer.py:1096`

**Visual elements:**
- `scale_moves_headline` (page title) + `scale_moves_deck` (lede)
- 5 ranked scale moves · each: rank · title · description · impact label · effort label · prerequisite
- Watch signals section · each: title · description · threshold · status (WATCH/URGENT)

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Headline + deck | `scale_moves_headline`, `scale_moves_deck` | `context_assembler` + `narrative_writer.page_intro()` | summary line | top-3 finding categories |
| Scale move N | `scale_moves[N]` (`ScaleMove`) | `scale_moves.generate_scale_moves()` | post-fix opportunity heuristics | full `report`, `eng.meta.monthly_spend`, `eng.shopify` |
| Prerequisite | `scale_moves[N].prerequisite` | `scale_moves` | dependencies on top-3 findings | finding IDs |
| Watch signal N | `watch_signals[N]` (`WatchSignal`) | `scale_moves.generate_watch_signals()` | post-fix monitoring triggers | top-3 findings + scan_data thresholds |

**Quality gates applied:** G1, G2, G10 (narrative tone), G11 `_priority_check` (right order: fix first, scale second).

**Empty-state behavior:**
- Clean account (no critical findings on Page 1) → Page 9 becomes primary value section · 5 scale moves expanded with more detail.
- Brand pre-product-market-fit → scale_moves replaced with "Pre-scale checklist" template.

---

### Page 10 · Intel briefing

**Renderer:** `_page10_intel(ctx)` · `composer.py:1142`

**Visual elements:**
- `intel_headline` (page title) + `intel_deck` (lede)
- 3-5 platform updates · each: platform tag · date line · headline · description · "AFFECTS YOU" line
- "Why AdX beats LLMs + MCP alone" comparison paragraph

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Headline + deck | `intel_headline`, `intel_deck` | `context_assembler` + `narrative_writer.page_intro()` | summary line | platform mix + vertical |
| Platform update N | `platform_updates[N]` (`PlatformUpdate`) | `intel_briefing.relevant_for_brand()` | curated platform-update DB filtered by brand vertical + platforms connected | `eng.brand.vertical`, `eng.platforms_connected` |
| "Affects you" line | `platform_updates[N].affects_you` | `intel_briefing` | brand-specific impact mapping | brand profile |
| Why-AdX-vs-LLM paragraph | `why_adx_vs_chatgpt` | `context_assembler` (curated) | static + brand-specific weave | top finding category |

**Quality gates applied:** G1, G2, G15 (vertical filtering).

**Empty-state behavior:**
- No relevant platform updates in last 60 days → section shows fallback `_todo()` placeholder (which IS caught by G12 `_check_no_placeholders` → would block emission · so empty intel_briefing means the page won't ship cleanly. Fix: ensure `intel_briefing.relevant_for_brand()` always returns ≥1 update; the curated DB has evergreen entries.)
- Note: `watch_signals` render on **Page 9** (Scale moves), not here.

---

### Page 11 · Action plan

**Renderer:** `_page11_action(ctx)` · `composer.py:1159`

**Visual elements:**
- 3 priority bands · each: bucket name + bucket impact label
- Action items per bucket · each: finding ID · title · effort · impact

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Bucket | `action_items[N].bucket` | `context_assembler` (inline) | 3-band grouping logic: TIME-BOUND / FIXABLE / STRATEGIC | finding's `verdict_class` + `effort_class` |
| Bucket impact | `action_items[N].bucket_impact` | `context_assembler` | sum of $ within bucket | per-bucket aggregate |
| Action title | `action_items[N].title` | `context_assembler` + `narrative_writer` | finding's `recommended_action` | finding |
| Effort | `action_items[N].effort` | finding metadata | — | — |
| Impact | `action_items[N].impact` | `scoring` (G7-capped) | finding's recoverable | — |

**Quality gates applied:** G1, G2, G7 (cap), G8 (sum reconciles to RecoverableSummary), G11 `_priority_check`, G12 `_check_math_reconciliation`.

**Empty-state behavior:**
- All findings in one bucket → renders single bucket fully; other 2 buckets hide.
- No festive window → strategic bucket fills with longer-horizon items.

---

### Page 12 · Creative + Audience Pulse

**Renderer:** `_page12_copilot_intro(ctx)` · `composer.py:1241`

**Visual elements:**
- Page kicker · "Creatives + Audience" · "12 / 16"
- Page title · "What's working · creatives + audience."
- Page deck (static line about creative + audience signals)
- **TOP HALF · CREATIVE PULSE** label
- Creative pulse table · 4 columns: Concept · Hook Rate · `creative_pulse_secondary_label` (default "CPM") · Verdict (colored by `verdict_class`)
- Creative summary line ("N winning · M fatigued · X to retire · …")
- **BOTTOM HALF · AUDIENCE PULSE** label
- Audience pulse table · 5 columns: Audience · Reach % · Frequency · `audience_pulse_secondary_label` (default "CPA") · Verdict
- `audience_takeaway_expand` line ("→ expand this …")
- `audience_takeaway_retire` line ("→ retire this …")

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Creative pulse row N | `creative_pulse_rows[N]` (dict: `name`, `hook_rate_label`, `cpm_label`, `verdict`, `verdict_class`) | `context_assembler` (per-creative verdict logic) | Meta hand-coded evaluators (hook rate · frequency · spend · CPM) | `eng.meta.creative_performance[]` (Path A) — **breaks gracefully on Path B** |
| Audience pulse row N | `audience_pulse_rows[N]` (dict: `name`, `reach_label`, `freq_label`, `cpa_label`, `verdict`, `verdict_class`) | `context_assembler` (per-audience verdict logic) | Meta hand-coded evaluators (frequency · reach % · spend) | `eng.meta.ad_sets[]` (Path A) — breaks on Path B |
| Creative pulse secondary metric label | `creative_pulse_secondary_label` (default `"CPM"`) | `context_assembler` (conversion-goal-aware) | `vertical_classifier.infer_conversion_goal()` mapping | conversion goal · lead-gen → CPL · app → CPI |
| Audience pulse secondary metric label | `audience_pulse_secondary_label` (default `"CPA"`) | `context_assembler` (conversion-goal-aware) | same as above | same |
| Audience takeaway (expand) | `audience_takeaway_expand` | `context_assembler` | top performer per CPA + headroom | best-CPA audience row |
| Audience takeaway (retire) | `audience_takeaway_retire` | `context_assembler` | worst performer per CPA + over-frequency | worst-CPA / fatigued audience row |

**Quality gates applied:** G1, G2, G15 (vertical-aware verdicts — e.g. CPL not CPA for lead-gen), G16 (persona-fit), G12 `_check_required_slots`.

**Empty-state behavior:**
- **Path B integration** (aggregates only, no `creative_performance` per-row) → table replaced with: "Connect creative-level data to unlock per-concept verdicts. Aggregate signals shown on Pages 6-7." Page still renders, just shallower.
- No Meta data at all (Google-only brand) → page replaced with Google equivalent: per-ad-group verdicts + keyword pulse.

---

### Page 13 · Creative angles

**Renderer:** `_page13_creative(ctx)` · `composer.py:1322`

**Visual elements:**
- 3 creative angle cards · each: rank · angle label · title · hook line · pattern name · format (video/static/carousel/UGC) · body copy · CTA · when to use · rationale · hypothesis · brief for team

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Angle N | `creative_angles[N]` (`CreativeAngle`) | `creative_brief.generate_creative_angles()` | vertical-specific pattern library + brand gaps | `eng.brand.vertical`, current creative mix |
| Hook line | `creative_angles[N].hook_line` | `creative_brief` | hook pattern application | matched pattern + brand context |
| Hypothesis | `creative_angles[N].hypothesis` | `creative_brief` | expected-lift math | benchmark deltas |
| Brief for team | `creative_angles[N].brief_for_team` | `creative_brief` + `narrative_writer` | production guidance | format + budget context |
| Test against | `creative_angles[N].test_against` | `creative_brief` | identifies prior creative to refresh (not repeat) | `eng.meta.creative_performance[]` history |

**Quality gates applied:** G1, G2, G15 (vertical-specific patterns), G16 (persona-fit consistency — hard rule per locked memory).

**Empty-state behavior:**
- No creative_performance history → angles still generate (vertical-only inputs) but `test_against` shows "First creative test."
- Brand vertical not in pattern library → fallback to "generic DTC" patterns with degraded specificity warning.

---

### Page 14 · Budget allocation

**Renderer:** `_page14_budget(ctx)` · `composer.py:1349` + `_budget_pie(allocations, size, currency_symbol)` · `composer.py:349`

**Visual elements:**
- Budget pie chart · current allocation
- Recommended allocation table · channel · current · recommended (with %) · delta · rationale · priority
- Headline + context line

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Allocation N · channel | `budget_allocations[N].channel` | `creative_brief.generate_budget_allocations()` | channel-spend extraction | `eng.meta.monthly_spend`, `eng.google.monthly_spend`, etc. |
| Current | `budget_allocations[N].current_label` | — | — | — |
| Recommended | `budget_allocations[N].recommended_label` | `creative_brief` | rebalance heuristic (poor-ROAS channels lose share) | per-channel ROAS, CAC |
| Delta | `budget_allocations[N].delta_label` | `creative_brief` | recommended − current | — |
| Rationale | `budget_allocations[N].rationale` | `narrative_writer` | per-channel reason | channel metrics |
| Headline | `budget_headline` | `context_assembler` | summary across all channels | — |
| Context line | `budget_context_line` | `context_assembler` | one-line WHY | — |

**Quality gates applied:** G1, G2, G7 (no recommended channel >80% of total), G11 `_priority_check`, G12 `_check_math_reconciliation` (totals must sum to current monthly_spend).

**Empty-state behavior:**
- Single-channel brand (Meta-only) → recommended split surfaces 2nd channel as "untested · pilot $X/mo".
- Cross-channel data missing → "Connect Google + Shopify to unlock budget allocation. Single-channel optimization on Page 11."

---

### Page 15 · AI Visibility (SEO · AEO · GEO · AIV)

**Renderer:** `_page15_visibility(ctx)` · `composer.py:1401` + `_donut_chart(value, max, color)` · `composer.py:330` × 4

**Visual elements:**
- 4 donut charts · one per pillar (SEO · AEO · GEO · AIV) · each shows score 0-100 with band label
- Per-pillar qualifier line (e.g. "10+ pages indexed · strong on brand queries")
- Organic fixes table · each: fix_id · type (FIXABLE/STRUCTURAL) · headline · description · fix action · impact · effort
- Buyer queries section · each: query · surface tested (Google AI Overviews / Perplexity / ChatGPT / Claude) · result · brand appears (YES/NO/PARTIAL/PENDING) · competitor winning · status (PASS/FAIL/WHITE_SPACE/PENDING) · note

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| SEO donut | `visibility_scores[0].score` | `visibility_audit.assess_visibility_scores()` | search visibility evaluators | brand domain · GSC data if connected |
| AEO donut | `visibility_scores[1].score` | `visibility_audit` + `live_ai_visibility` | answer-engine query tests | brand vertical + buyer-query corpus |
| GEO donut | `visibility_scores[2].score` | `visibility_audit` | generative-engine ranking tests | live_ai_visibility query results |
| AIV donut | `visibility_scores[3].score` | `live_ai_visibility.build_visibility_profile()` | ChatGPT + Claude + Gemini + Perplexity probes | brand name + vertical queries |
| Pillar qualifier | `visibility_scores[N].qualifier` | `visibility_audit` | top finding per pillar | per-pillar evaluator outputs |
| Measurement method | `visibility_scores[N].measurement_method` | `visibility_audit` | "measured" if real probes ran · "derived" / "estimated" otherwise | API call success state |
| Organic fix N | `organic_fixes[N]` (`OrganicFix`) | `visibility_audit.generate_organic_fixes()` | structural + content gap rules | brand site scan + GSC if connected |
| Buyer query N | `buyer_query_results[N]` (`BuyerQueryResult`) | `visibility_audit.generate_buyer_queries()` + `live_ai_visibility.build_visibility_profile()` | curated query corpus × live probes | vertical + region |

**Quality gates applied:** G1, G2, G15 (vertical-aware query selection), G12 `_check_required_slots`, G11 `_specificity_check` (no generic AEO claims).

**Empty-state behavior:**
- `live_ai_visibility` probes failed / not run → `BuyerQueryResult.brand_appears = "PENDING"`, `status = "PENDING"`, `note = "Live probe unavailable this run · refreshes next re-run."` Page still renders with measured scores marked.
- Brand has no website → entire page replaced with "AI Visibility audit requires a public domain. Add and re-run."

---

### Page 16 · What's next · Strategic + Re-run cadence + Baseline lock

**Renderer:** `_page16_strategic(ctx)` · `composer.py:1463`

**Visual elements:**
- Festive phases (if relevant) · 3-4 phase cards · each: phase label · role · description
- Re-run history unlocks · each: run label · what new analysis unlocks on that re-run
- Baseline locked card (first run only) OR run delta card (re-runs) · current baseline metrics + lock confirmation
- "What ships in next re-run" preview

**Data flow:**

| Element | Slot | Agent | Evaluator(s) | scan_data input |
|---|---|---|---|---|
| Festive phase N | `festive_phases[N]` (`FestivePhase`) | `festival_calendar.primary_festival_for()` | regional festive calendar | `eng.primary_geo` + `eng.brand.vertical` + today's date |
| Run history unlock N | `run_history_unlocks[N]` (`RunHistoryUnlock`) | `context_assembler` | per-re-run unlock map | `eng.run_number` |
| Baseline / run delta | `run_delta` (`RunDeltaCard`) | `context_loader.compute_delta(eng, report)` (`agents/context_loader.py:107`) — wraps `load_prior_run()` + diff. Persists current run via `context_loader.save_run()`. | comparison vs prior run (none if first) | prior run file in `customers/{brand_id}/history/` |
| Next re-run preview | (inline) | `context_assembler` | scheduled deltas + unlocks | run_history + scheduled jobs |

**Quality gates applied:** G1, G2, G18 (festival calendar overlay), G11 `_festive_math` check (festive uplift claims realistic).

**Empty-state behavior:**
- First run → `run_delta.has_prior_run = False` → "BASELINE LOCKED" card renders · phases section emphasized.
- Re-runs → `run_delta` shows since-last-run deltas · baseline card replaced with delta card.
- No festive window in next 90 days → phases section hides · run_history_unlocks gets larger share.

---

## Cross-references

- **Engine architecture (strategic, read once):** [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **All 259 evaluators by ID (Ctrl-F lookup):** [`EVALUATORS.md`](EVALUATORS.md)
- **Integration spec (3 code changes):** [`INTEGRATION.md`](INTEGRATION.md)
- **Pre-written `_build_engine_input` adapter:** [`PRUDHVI_BUILD_ENGINE_INPUT.py`](PRUDHVI_BUILD_ENGINE_INPUT.py)
- **Engine repo (private · invite required):** https://github.com/vinayrajchouhan/adx-engine
- **Public samples + GitHub Pages live demo:** https://vinayrajchouhan.github.io/adx-engine-samples/
- **Integration discussion:** https://github.com/poornagurram/pm_agency/issues/481

---

## Notes for the integrator

1. **Path A vs Path B vs Path C** (per `ARCHITECTURE.md` §6.1) is decided at `_build_engine_input()` time. This doc shows what each page renders under each path:
   - **Path A · extended scan_data:** all 16 pages render fully · Page 12 per-creative verdicts surface.
   - **Path B · aggregates only:** Page 12 falls back to empty state · Pages 1, 2, 6, 7, 11, 14, 16 render normally · Pages 3-5 may show fewer differential causes if `evidence_detail_rows` aren't populated.
   - **Path C · engine calls Meta direct:** all pages render fully · ~3-5s additional latency for live API calls.

2. **Empty-state copy is intentional.** Do not replace it with `"TODO"` or `"Coming soon"` — those fail G12 `_check_no_placeholders`. Empty states are first-class UX.

3. **Customer Memory writes** (post-emission) hook from `agents/customer_memory.py`. The `RunDeltaCard` on Page 16 reads from this file on subsequent runs.

4. **Currency** flows from `eng.currency` → composer's `currency_symbol` parameter → propagated to every chart + scrubber. Six supported: `$` (USD) · `£` (GBP) · `€` (EUR) · `A$` (AUD) · `₹` (INR) · `C$` (CAD). Adding a new currency = add to `_buyer_safe()` and `_final_currency_sweep()` regex lists.

5. **Anonymizer (G20)** never runs on customer-facing Playbooks. It's a separate code path triggered only via `anonymizer.scrub_brand_profile(mode="heavy")` for sample generation.

---

🤖 Maintained by Rey · acting on Vinay's direction · v0.1.5 · 2026-05-20

If anything's missing, wrong, or you need deeper drill on a specific page → reply on issue #481 · same-day correction.
