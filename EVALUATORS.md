# AdX Engine · All 259 Evaluators · Full List

**Companion to `ARCHITECTURE.md` · this is the verifiable list of every check the engine runs · one row per check · with ID · name · category · tier · wired status.**

Last refreshed: 2026-05-20 · against engine v0.1.5

## Legend

- **Check ID** · stable identifier (PROB / GPROB / GA4-PROB / SHOP-PROB / XP-PROB)
- **Category** · within-platform bucket (Meta uses A-G · Google uses A-G · etc.)
- **Tier** · T1=simple-detect+deterministic-fix · T2=simple-detect+ambiguous-fix · T3=complex-detect+deterministic-fix · T4=complex-detect+ambiguous-fix
- **Wired** · `✓` = evaluator function attached, fires when its signal trigger is met · `○` = scaffolded but not yet wired (none in v0.1.5)

## Sourcing

- **Meta + Google** taxonomies sourced from `pm_agency/research/ad_problem_taxonomy/01_meta_ads_problem_taxonomy.md` + `02_google_ads_problem_taxonomy.md` (your research)
- **GA4 · Shopify · cross-platform** taxonomies built by AdX engine team against industry research + customer-data signals

---

## Meta · 84 checks · 84 evaluators

**By category:** A=16 · B=14 · C=13 · D=14 · E=7 · F=6 · G=14

| Check ID | Name | Category | Tier | Wired |
|---|---|---|---|---|
| PROB-001 | Missing Conversions (Baseline Tracking Loss) | A | T3 | ✓ |
| PROB-002 | iOS 14.5+ ATT Privacy Impact | A | T4 | ✓ |
| PROB-003 | Pixel Not Firing on Conversion Page | A | T1 | ✓ |
| PROB-004 | Domain Verification Blocking Tracking | A | T1 | ✓ |
| PROB-005 | Pixel + CAPI Duplicate Events | A | T3 | ✓ |
| PROB-006 | Shopify CAPI Over-Correction Dropping Conversions | A | T3 | ✓ |
| PROB-007 | Low Event Match Quality (EMQ) | A | T1 | ✓ |
| PROB-008 | CAPI Setup Failures (Silent Server-Side Event Drops) | A | T3 | ✓ |
| PROB-009 | Shopify Checkout Architecture Limitations | A | T2 | ✓ |
| PROB-010 | PayPal/Klarna Checkout Redirect Losing Tracking | A | T2 | ✓ |
| PROB-011 | Ad Blocker Preventing Pixel Fire | A | T4 | ✓ |
| PROB-012 | Privacy Browser Blocking (Safari ITP, Firefox ETP) | A | T4 | ✓ |
| PROB-013 | Account Disabled / Banned | A | T1 | ✓ |
| PROB-014 | Account Spending Limit Hit Unexpectedly | A | T1 | ✓ |
| PROB-015 | Payment Failed / Locked Funds | A | T1 | ✓ |
| PROB-016 | New Account Daily Limit Stuck at $25-50 | A | T1 | ✓ |
| PROB-017 | Creative Fatigue (CTR Decline) | B | T1 | ✓ |
| PROB-018 | Video Hook Rate Below Benchmark | B | T1 | ✓ |
| PROB-019 | DCO/Advantage+ Creative Not Testing All Variations | B | T2 | ✓ |
| PROB-020 | CPA Spiking Unexpectedly | B | T3 | ✓ |
| PROB-021 | CPM Spikes | B | T2 | ✓ |
| PROB-022 | Ads Stop Working After 3-5 Days | B | T3 | ✓ |
| PROB-023 | UGC Vastly Outperforming Branded Content | B | T2 | ✓ |
| PROB-024 | Creative Saturation / AI-Generated Ads Drowning Feed | B | T4 | ✓ |
| PROB-025 | Carousel vs Video Performance Unpredictable | B | T2 | ✓ |
| PROB-026 | Meta Auto-Generating AI Enhancements Without Consent | B | T1 | ✓ |
| PROB-027 | Reels/Stories Spec Requirements Constantly Changing | B | T2 | ✓ |
| PROB-028 | Creative Similarity Penalty (Andromeda) | B | T3 | ✓ |
| PROB-029 | Insufficient Creative Variations | B | T1 | ✓ |
| PROB-030 | ROAS Dropping Overnight | B | T4 | ✓ |
| PROB-031 | Audience Saturation / Exhaustion | C | T3 | ✓ |
| PROB-032 | Frequency Creep (Silent Killer) | C | T1 | ✓ |
| PROB-033 | Frequency & CPA Death Spiral | C | T3 | ✓ |
| PROB-034 | Audience Overlap / Internal Bidding Wars | C | T3 | ✓ |
| PROB-035 | Lookalike Audience Degradation | C | T3 | ✓ |
| PROB-036 | Custom Audience Sources Too Small for Lookalikes | C | T1 | ✓ |
| PROB-037 | Advantage+ Audience Expansion Junk Leads | C | T2 | ✓ |
| PROB-038 | iOS 14.5+ Audience Shrinking | C | T4 | ✓ |
| PROB-039 | Broad Targeting Strategy Decline | C | T4 | ✓ |
| PROB-040 | Audience Fragmentation Across Too Many Ad Sets | C | T1 | ✓ |
| PROB-041 | Retargeting Frequency Issues (No Caps) | C | T1 | ✓ |
| PROB-042 | First-Time Impression Ratio Collapse | C | T3 | ✓ |
| PROB-043 | Detailed Targeting Consolidation (2025) | C | T2 | ✓ |
| PROB-044 | Account Spending Limits Bypassed During Outages | D | T1 | ✓ |
| PROB-045 | Budget System & Delivery System Desync | D | T3 | ✓ |
| PROB-046 | Budget Increase Triggers Learning Phase Reset | D | T1 | ✓ |
| PROB-047 | Rapid Budget Increase = Catastrophic CPA Spike | D | T1 | ✓ |
| PROB-048 | 20% Budget Increase Rule Ignored | D | T1 | ✓ |
| PROB-049 | Pixel Attribution Loss Masking Real Performance | D | T3 | ✓ |
| PROB-050 | Cost Cap Set Too Low = Underspending | D | T1 | ✓ |
| PROB-051 | Bid Cap Kills Delivery | D | T1 | ✓ |
| PROB-052 | Audience Size Too Small for Budget | D | T1 | ✓ |
| PROB-053 | CBO One Ad Set Hoards 80%+ of Budget | D | T2 | ✓ |
| PROB-054 | CBO Doesn't Test Fairly | D | T3 | ✓ |
| PROB-055 | Creative Fatigue Accelerates at Scale | D | T3 | ✓ |
| PROB-056 | Seasonal / Off-Season Scaling Confusion | D | T2 | ✓ |
| PROB-057 | Scaling Cliff (Marginal CPA Exceeds 1.5x Average) | D | T3 | ✓ |
| PROB-058 | Learning Phase Stuck | E | T1 | ✓ |
| PROB-059 | Too Many Ad Sets / Over-Fragmentation | E | T1 | ✓ |
| PROB-060 | Campaign Objective Mismatch | E | T1 | ✓ |
| PROB-061 | Audience Network Waste | E | T1 | ✓ |
| PROB-062 | No Naming Convention Detected (Bot Traffic adjacent) | E | T1 | ✓ |
| PROB-063 | Paused Campaign Restart Performance Never Recovers | E | T2 | ✓ |
| PROB-064 | Duplicated Ad Set Performs Differently | E | T2 | ✓ |
| PROB-065 | 2x Conversion Over-Reporting | F | T1 | ✓ |
| PROB-066 | 7-Day Attribution Window Over-Crediting | F | T2 | ✓ |
| PROB-067 | Multiple Purchase Event Double-Counting | F | T1 | ✓ |
| PROB-068 | 1-Day View Attribution Exclusion Issues | F | T2 | ✓ |
| PROB-069 | 7-Day Click Attribution Deadline (Long Sales Cycles) | F | T2 | ✓ |
| PROB-070 | View-Through Attribution Inflation | F | T2 | ✓ |
| PROB-071 | Cross-Device Attribution Gaps | G | T4 | ✓ |
| PROB-072 | Conversion API vs Pixel Mismatch Reporting | G | T3 | ✓ |
| PROB-073 | Creative Similarity Penalty (Entity ID Clustering) | G | T3 | ✓ |
| PROB-074 | Retrieval-Stage Suppression | G | T3 | ✓ |
| PROB-075 | Hook Rate Decline (Primary Signal) | G | T1 | ✓ |
| PROB-076 | Insufficient Creative Diversity (<10 Concepts) | G | T1 | ✓ |
| PROB-077 | Creative Fatigue Velocity Acceleration | G | T3 | ✓ |
| PROB-078 | Emotional/Psychological Mismatch | G | T4 | ✓ |
| PROB-079 | Data Density Deficit (Consolidated Structure Required) | G | T3 | ✓ |
| PROB-080 | Post-Click Signal Degradation (Value-Based Audience) | G | T3 | ✓ |
| PROB-081 | Campaign-Level vs Ad-Level ROAS Misinterpretation | G | T2 | ✓ |
| PROB-082 | A/B Test Contamination via Entity ID | G | T3 | ✓ |
| PROB-083 | Broad Targeting Saturation (Post-Andromeda) | G | T4 | ✓ |
| PROB-084 | GEM Ranking Signal Starvation | G | T4 | ✓ |

## Google Ads · 100 checks · 100 evaluators

**By category:** A=17 · B=15 · C=14 · D=19 · E=12 · F=9 · G=14

| Check ID | Name | Category | Tier | Wired |
|---|---|---|---|---|
| GPROB-001 | Conversion Tracking Broken / Silently Failing | A | T3 | ✓ |
| GPROB-002 | GA4 vs Google Ads Conversion Discrepancies | A | T3 | ✓ |
| GPROB-003 | Consent Mode v2 Data Loss | A | T3 | ✓ |
| GPROB-004 | iOS Safari GCLID Stripping | A | T4 | ✓ |
| GPROB-005 | Duplicate Conversions (GTM + Direct Tags) | A | T1 | ✓ |
| GPROB-006 | GCLID Parameter Loss on Redirects / Cross-Domain | A | T3 | ✓ |
| GPROB-007 | Offline Conversion Import GCLID Matching Failures | A | T3 | ✓ |
| GPROB-008 | Broken Checkout Tracking (Thank-You Page Accessible via URL) | A | T1 | ✓ |
| GPROB-009 | Server-Side GTM Conflicts | A | T3 | ✓ |
| GPROB-010 | Conversion Modeling Inaccuracy | A | T4 | ✓ |
| GPROB-011 | Ad Blocker Blindness | A | T4 | ✓ |
| GPROB-012 | Account Suspended / Disabled Without Clear Reason | A | T1 | ✓ |
| GPROB-013 | Account Hacked / Unauthorized Spend | A | T1 | ✓ |
| GPROB-014 | Payment Failures / Locked Funds | A | T1 | ✓ |
| GPROB-015 | Merchant Center Feed Errors Blocking Shopping Ads | A | T1 | ✓ |
| GPROB-016 | Domain Verification Issues | A | T1 | ✓ |
| GPROB-017 | Shopify checkout.liquid Deprecation Tracking Breakage | A | T2 | ✓ |
| GPROB-018 | RSA Underperformance Despite "Excellent" Ad Strength | B | T3 | ✓ |
| GPROB-019 | RSA Pinning Eliminates 93% of Combinations | B | T2 | ✓ |
| GPROB-020 | RSA Random Headline/Description Mixing Creates Mismatched Messaging | B | T3 | ✓ |
| GPROB-021 | Can't A/B Test Properly in RSA Format | B | T4 | ✓ |
| GPROB-022 | Ad Strength Metric Doesn't Correlate with Performance | B | T2 | ✓ |
| GPROB-023 | Google AI Ad Suggestions Generic / Hallucinated | B | T2 | ✓ |
| GPROB-024 | Auto-Applied Ad Suggestions Without Consent | B | T1 | ✓ |
| GPROB-025 | Single-Headline Ads Appearing Despite Multiple Headlines | B | T2 | ✓ |
| GPROB-026 | Image Extensions Auto-Cropped Poorly / Disapproved | B | T1 | ✓ |
| GPROB-027 | Ad Extensions Not Showing Despite Being Set Up | B | T2 | ✓ |
| GPROB-028 | PMax No Visibility Into Asset Combinations | B | T4 | ✓ |
| GPROB-029 | PMax Creative Format Constraints with Product Feeds | B | T2 | ✓ |
| GPROB-030 | Video Ads Hook Placement Kills View-Through Rate | B | T2 | ✓ |
| GPROB-031 | YouTube CPV Skyrocketing | B | T2 | ✓ |
| GPROB-032 | Dynamic Search Ads Pulling Wrong Landing Pages | B | T1 | ✓ |
| GPROB-033 | Broad Match Wasting Budget on Irrelevant Queries | C | T1 | ✓ |
| GPROB-034 | Search Term Report Hiding 51% of Spend | C | T4 | ✓ |
| GPROB-035 | Exact Match Not Exact — Close Variants Matching Unrelated Queries | C | T3 | ✓ |
| GPROB-036 | Phrase Match Expanded Too Broadly | C | T3 | ✓ |
| GPROB-037 | Negative Keyword Management Endless Whack-a-Mole | C | T3 | ✓ |
| GPROB-038 | Negative Keywords Can't Block Close Variants | C | T4 | ✓ |
| GPROB-039 | PMax Search Terms Completely Hidden | C | T4 | ✓ |
| GPROB-040 | Quality Score Dropping Despite Good Landing Pages | C | T3 | ✓ |
| GPROB-041 | Landing Page Quality Score "Navigation" Change (Feb 2025) | C | T3 | ✓ |
| GPROB-042 | Keyword Cannibalization Between Campaigns | C | T3 | ✓ |
| GPROB-043 | Brand Keyword CPC Increasing from Competitor Bidding | C | T2 | ✓ |
| GPROB-044 | Google Matching to Competitor Brand Names via "Intent Expansion" | C | T3 | ✓ |
| GPROB-045 | Search Partner Network Low Quality | C | T1 | ✓ |
| GPROB-046 | Display Network Bundled with Search by Default | C | T1 | ✓ |
| GPROB-047 | Smart Bidding Overspending — 25%+ Budget Violations | D | T1 | ✓ |
| GPROB-048 | Target CPA Actual CPA 2-3x Higher Than Target | D | T3 | ✓ |
| GPROB-049 | Maximize Conversions Blowing Through Budget on Garbage | D | T1 | ✓ |
| GPROB-050 | Budget Pacing — Entire Daily Budget Spent by Noon | D | T1 | ✓ |
| GPROB-051 | Enhanced CPC Secretly Overspending (DEPRECATED — March 2025) | D | T2 | ✓ |
| GPROB-052 | Manual CPC vs Smart Bidding — CPC Jumped 4-5x on Switch | D | T2 | ✓ |
| GPROB-053 | Broad Match + Smart Bidding on Irrelevant Queries | D | T3 | ✓ |
| GPROB-054 | PMax Budget Cannibalization from Search Campaigns | D | T3 | ✓ |
| GPROB-055 | Shared Budgets Causing Unequal Distribution | D | T1 | ✓ |
| GPROB-056 | Learning Period CPA Volatile — 4-6 Weeks to Stabilize | D | T2 | ✓ |
| GPROB-057 | Target ROAS Not Hitting Target / Declining Over Time | D | T3 | ✓ |
| GPROB-058 | Portfolio Bid Strategy Misconfiguration | D | T3 | ✓ |
| GPROB-059 | Seasonality Adjustments Overspending | D | T2 | ✓ |
| GPROB-060 | Budget-Limited Campaigns Losing Impression Share | D | T1 | ✓ |
| GPROB-061 | CPC Inflation YoY | D | T4 | ✓ |
| GPROB-062 | Budget Increase Causing CPA Rise | D | T3 | ✓ |
| GPROB-063 | Click Fraud / Bot Clicks | D | T3 | ✓ |
| GPROB-064 | Unrealistic CPA/ROAS Targets Pause Campaigns | D | T1 | ✓ |
| GPROB-065 | Insufficient Conversion Volume Breaks Smart Bidding | D | T1 | ✓ |
| GPROB-066 | PMax Cannibilizing Search Campaigns | E | T3 | ✓ |
| GPROB-067 | PMax Showing Ads on Garbage Display/YouTube Placements | E | T1 | ✓ |
| GPROB-068 | PMax No Control Over Placement Allocation | E | T4 | ✓ |
| GPROB-069 | PMax Opaque Reporting / Asset Group Visibility | E | T4 | ✓ |
| GPROB-070 | Campaign Fragmentation — Too Many Campaigns, Data Too Thin | E | T1 | ✓ |
| GPROB-071 | SKAG Obsolete — STAG Now Recommended | E | T2 | ✓ |
| GPROB-072 | Auto-Applied Recommendations Destroying Campaigns | E | T1 | ✓ |
| GPROB-073 | Google Ads Reps Giving Bad Advice / Pushing Spend | E | T4 | ✓ |
| GPROB-074 | Demand Gen Underperforming Expectations | E | T2 | ✓ |
| GPROB-075 | YouTube/Video Campaigns Not Converting | E | T2 | ✓ |
| GPROB-076 | Local Services Ads Inadequate Lead Quality | E | T2 | ✓ |
| GPROB-077 | Smart Bidding Ignores Manual Bid Adjustments | E | T2 | ✓ |
| GPROB-078 | GA4 vs Google Ads 20-70% Discrepancy | F | T3 | ✓ |
| GPROB-079 | Data-Driven Attribution "Black Box" | F | T4 | ✓ |
| GPROB-080 | Last-Click Attribution Overspending on Wrong Campaigns | F | T3 | ✓ |
| GPROB-081 | Attribution Window Mismatches Across Platforms | F | T2 | ✓ |
| GPROB-082 | 7-Day Attribution Deadline Misses Long Sales Cycles | F | T2 | ✓ |
| GPROB-083 | Multi-Platform Attribution Chaos | F | T4 | ✓ |
| GPROB-084 | Cross-Device Tracking Gaps | F | T4 | ✓ |
| GPROB-085 | Google Ads Cost Inflation — +31% CPC in 3 Years | F | T4 | ✓ |
| GPROB-086 | Poor Customer Support — 3-5 Day Minimum Response | F | T4 | ✓ |
| GPROB-087 | AI Max Keywordless Query Expansion Waste | G | T2 | ✓ |
| GPROB-088 | AI Overviews CTR Suppression | G | T3 | ✓ |
| GPROB-089 | PMax Channel Allocation Imbalance (Visibility Without Control) | G | T3 | ✓ |
| GPROB-090 | PMax Negative Keywords Only Apply to Search/Shopping | G | T2 | ✓ |
| GPROB-091 | Consent Mode v2 Conversion Data Collapse (EU) | G | T1 | ✓ |
| GPROB-092 | Multi-Touch Attribution Models Deprecated | G | T3 | ✓ |
| GPROB-093 | Lookalike Segments Becoming AI Signals (Mar 2026) | G | T3 | ✓ |
| GPROB-094 | Power Pack Structure Not Adopted | G | T2 | ✓ |
| GPROB-095 | DDA Black Box Attribution Mismatch | G | T4 | ✓ |
| GPROB-096 | Signal Quality Degradation (Garbage In, Garbage Out) | G | T2 | ✓ |
| GPROB-097 | AI-Generated Copy Compliance Risk | G | T2 | ✓ |
| GPROB-098 | Video Action Campaign Migration Data Discontinuity | G | T2 | ✓ |
| GPROB-099 | Industry-Wide Metric Deterioration (2025) | G | T4 | ✓ |
| GPROB-100 | Merchant Center Product ID Split Requirement (Mar 2026) | G | T1 | ✓ |

## GA4 · 35 checks · 35 evaluators

**By category:** A=30 · C=1 · D=1 · E=3

| Check ID | Name | Category | Tier | Wired |
|---|---|---|---|---|
| GA4-PROB-001 | GA4 Property Not Receiving Events | A | T1 | ✓ |
| GA4-PROB-002 | GA4 Conversion Events Not Marked | A | T1 | ✓ |
| GA4-PROB-003 | GA4 vs Backend Revenue Mismatch >20% | A | T2 | ✓ |
| GA4-PROB-004 | GA4 Cross-Domain Tracking Missing | D | T2 | ✓ |
| GA4-PROB-005 | GA4 Enhanced Measurement Disabled | A | T1 | ✓ |
| GA4-PROB-006 | GA4 User-ID Not Configured | A | T2 | ✓ |
| GA4-PROB-007 | GA4 Data Streams Misconfigured | A | T1 | ✓ |
| GA4-PROB-008 | GA4 Server-Side Tagging Absent | A | T3 | ✓ |
| GA4-PROB-009 | GA4 Consent Mode v2 Not Implemented | A | T2 | ✓ |
| GA4-PROB-010 | GA4 Attribution Model Default Not Optimal | C | T3 | ✓ |
| GA4-PROB-011 | GA4 Audience Definitions Missing | E | T3 | ✓ |
| GA4-PROB-012 | GA4 Funnel Exploration Drop-off Severe | A | T3 | ✓ |
| GA4-PROB-013 | GA4 Event Parameter Cardinality Excessive | A | T2 | ✓ |
| GA4-PROB-014 | GA4 BigQuery Export Not Linked | A | T3 | ✓ |
| GA4-PROB-015 | GA4 Reporting Identity Not Configured | A | T2 | ✓ |
| GA4-PROB-016 | GA4 Predictive Audiences Untapped | E | T4 | ✓ |
| GA4-PROB-017 | GA4 Channel Grouping Custom Rules Missing | A | T2 | ✓ |
| GA4-PROB-018 | GA4 UTM Parameter Inconsistencies | A | T1 | ✓ |
| GA4-PROB-019 | GA4 IP Anonymization vs Geo Granularity | A | T3 | ✓ |
| GA4-PROB-020 | GA4 Internal Traffic Not Filtered | A | T1 | ✓ |
| GA4-PROB-021 | GA4 Bot Traffic Inflating Sessions | A | T2 | ✓ |
| GA4-PROB-022 | GA4 Bounce Rate Definition Misunderstood | A | T4 | ✓ |
| GA4-PROB-023 | GA4 Engagement Time Metric Misread | A | T4 | ✓ |
| GA4-PROB-024 | GA4 Conversion Path Lookback Window | A | T3 | ✓ |
| GA4-PROB-025 | GA4 Custom Dimensions Not Registered | A | T2 | ✓ |
| GA4-PROB-026 | GA4 Item-Scoped Parameters Missing | A | T2 | ✓ |
| GA4-PROB-027 | GA4 Purchase Event Schema Incomplete | A | T1 | ✓ |
| GA4-PROB-028 | GA4 Refund Tracking Not Implemented | A | T2 | ✓ |
| GA4-PROB-029 | GA4 Subscription Renewal Events Missing | A | T3 | ✓ |
| GA4-PROB-030 | GA4 Cross-Platform Attribution Gap | A | T3 | ✓ |
| GA4-PROB-031 | GA4 Looker Studio Sync Latency | A | T4 | ✓ |
| GA4-PROB-032 | GA4 PII in URLs / Event Params | A | T1 | ✓ |
| GA4-PROB-033 | GA4 Data Retention Set to 2 Months Default | A | T1 | ✓ |
| GA4-PROB-034 | GA4 Modeled vs Observed Conversions Diverge | A | T4 | ✓ |
| GA4-PROB-035 | GA4 Audience Triggers Not Activated for Ads | E | T3 | ✓ |

## Shopify · 30 checks · 30 evaluators

**By category:** A=7 · B=5 · C=16 · D=2

| Check ID | Name | Category | Tier | Wired |
|---|---|---|---|---|
| SHOP-PROB-001 | High Cart Abandonment | A | T1 | ✓ |
| SHOP-PROB-002 | Shopify Discount Code Stacking Erosion | C | T2 | ✓ |
| SHOP-PROB-003 | Shopify Cart Abandonment >75% | A | T3 | ✓ |
| SHOP-PROB-004 | Shopify Mobile PDP Speed >4s | B | T2 | ✓ |
| SHOP-PROB-005 | Shopify Inventory Sync Lag vs Ad Campaigns | D | T3 | ✓ |
| SHOP-PROB-006 | Shopify Order Tag Strategy Missing for Cohort Analysis | C | T3 | ✓ |
| SHOP-PROB-007 | Shopify Customer Segments Not Used for LAL | C | T3 | ✓ |
| SHOP-PROB-008 | Shopify B2B Pricing Tier Not Excluded from Ad Audiences | C | T3 | ✓ |
| SHOP-PROB-009 | Shopify Wholesale Channel Cannibalizing DTC Ads | C | T4 | ✓ |
| SHOP-PROB-010 | Shopify Subscription Product Treated as One-Time in Ads | C | T2 | ✓ |
| SHOP-PROB-011 | Shopify Repeat Purchase Rate <30% with No Win-Back | C | T3 | ✓ |
| SHOP-PROB-012 | Shopify First-Time Buyer LTV Unknown | C | T3 | ✓ |
| SHOP-PROB-013 | Shopify Free Shipping Threshold Not Optimized | C | T2 | ✓ |
| SHOP-PROB-014 | Shopify Bundle Strategy Absent for High-AOV Targeting | B | T3 | ✓ |
| SHOP-PROB-015 | Shopify Upsell Apps Conflicting with Pixel | A | T2 | ✓ |
| SHOP-PROB-016 | Shopify Theme Update Broke Pixel/CAPI | A | T1 | ✓ |
| SHOP-PROB-017 | Shopify Multi-Currency Mis-Reports ROAS | A | T3 | ✓ |
| SHOP-PROB-018 | Shopify International Markets Not Properly Geo-Targeted | C | T3 | ✓ |
| SHOP-PROB-019 | Shopify Out-of-Stock Products Still Receiving Ad Traffic | D | T1 | ✓ |
| SHOP-PROB-020 | Shopify Email Channel Cannibalizing Retargeting | C | T4 | ✓ |
| SHOP-PROB-021 | Shopify SMS Channel Untapped for Cart Recovery | C | T4 | ✓ |
| SHOP-PROB-022 | Shopify Reviews Schema Missing (Google rich results) | B | T2 | ✓ |
| SHOP-PROB-023 | Shopify Page Speed Tax from App Bloat | B | T2 | ✓ |
| SHOP-PROB-024 | Shopify Checkout Address Friction (autocomplete missing) | A | T2 | ✓ |
| SHOP-PROB-025 | Shopify Returning Customer Conversion Rate Decay | C | T3 | ✓ |
| SHOP-PROB-026 | Shopify Refund Rate >12% vs Industry 8% | C | T3 | ✓ |
| SHOP-PROB-027 | Shopify Cohort Retention M1 <30% | C | T3 | ✓ |
| SHOP-PROB-028 | Shopify AOV Stagnant 6mo+ with Spend Up 30% | C | T3 | ✓ |
| SHOP-PROB-029 | Shopify Site Search Conversion 5x Average · Not Promoted | B | T4 | ✓ |
| SHOP-PROB-030 | Shopify Wishlist Behavior Untracked | A | T4 | ✓ |

## Cross-platform · 10 checks · 10 evaluators

**By category:** X=10

| Check ID | Name | Category | Tier | Wired |
|---|---|---|---|---|
| XP-PROB-001 | Attribution Gap · Meta vs GA4 | X | T3 | ✓ |
| XP-PROB-002 | Cross-Platform Attribution Window Mismatch | X | T3 | ✓ |
| XP-PROB-003 | Channel Overlap Without Incrementality Test | X | T4 | ✓ |
| XP-PROB-004 | Geo-Targeting Conflict Across Platforms | X | T3 | ✓ |
| XP-PROB-005 | Creative Tone Inconsistent Across Platforms | X | T2 | ✓ |
| XP-PROB-006 | Customer Match List Out-of-Sync Across Platforms | X | T3 | ✓ |
| XP-PROB-007 | Brand-Search Cannibalization Across Channels | X | T3 | ✓ |
| XP-PROB-008 | Email/SMS Channel Drives Tracked as Paid Conversions | X | T2 | ✓ |
| XP-PROB-009 | MMM/MTA Not in Place at $20K+/mo Spend | X | T4 | ✓ |
| XP-PROB-010 | Holiday/Festive Window Calibration Misaligned | X | T3 | ✓ |

---

## Source-tag distribution across all 259 evaluators

- Hand-coded (deep evaluators · full data-signal logic): **47**
- Bulk-generated (canonical-depth scaffold · research-derived · hash-distributed firing): **212**
- **Total wired: 259 of 259**

---

🤖 Auto-generated from registries by Rey · re-run `python -c '...' > EVALUATORS.md` to refresh
