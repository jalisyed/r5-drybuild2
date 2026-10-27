# Genie space validation — 5 test questions against RESULTS.md

Space: "Birchwood Retail: Margin, Promotions, Loyalty and Trust"
Space ID: `01f1d22ebf4217ca9ca00cabefb2a93f`
Workspace path: `/Workspace/Users/jalisyed@gmail.com/r5-drybuild2/genie_spaces`
Warehouse: `f461843f1d41af18` (Serverless Starter Warehouse, 2X-Small)
Tables attached (7): gold_daily_store_category, gold_promo_effectiveness, gold_stockout_exposure,
gold_loyalty_cohorts, gold_margin_leakage, gold_basket_affinity, gold_data_trust.

## Issue found and fixed
First test ("Which categories earn our margin...") came back with Genie labelling measured
figures (net sales, margin by category) as "ESTIMATE" — wrong, since only stock-out and
promotion-vs-baseline figures are modeled estimates. Fixed by adding an explicit text instruction
naming which tables/figures are NOT estimates, re-deployed via `update-space`, and re-tested.
After the fix, Genie correctly distinguishes measured figures (no label) from modeled ones
(ESTIMATE, stated explicitly).

## Test results (all COMPLETED, all figures match RESULTS.md)

| # | Question | Genie's figures | Matches RESULTS.md? |
|---|---|---|---|
| 1 | Which categories earn our margin, and how is each trending? | Apparel $3,661,048 (50.1%), Electronics $2,647,774 (16.9%), Home $2,074,942 | ✅ exact match, no spurious ESTIMATE label |
| 2 | Where are stock-outs costing us the most (estimated)? | Apparel $23,963, Electronics $19,289, Home $13,514 — "estimates...not measured losses" | ✅ exact match, correctly labelled ESTIMATE |
| 3 | How many loyalty customers are still buying 1, 3, 6, 12 months after first purchase? | 34.7% / 32.3% / 28.1% / 21.9% | ✅ exact match |
| 4 | Which promotions lost us money, even though they sold more? | Electronics promo 5 -$6,590, Apparel promo 5 -$3,244, Home promo 5 -$2,872, Health & Beauty promo 5 -$921, Electronics promo 2 -$912 — all labelled ESTIMATE | ✅ exact match, correctly labelled |
| 5 | How fresh and complete is the data behind these numbers? | bronze 647,502, silver 642,908, quarantined 1,318, duplicates 3,276, late share 1.94%, median latency 2.6 min, p95 4.8 min | ✅ exact match |

**Verdict: solid inside the 15-minute box.** Keeping it in the build and presenting it live.
