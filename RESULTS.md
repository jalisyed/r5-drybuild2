# RESULTS.md — every figure, with the query that produced it

All figures below are from the synthetic `workspace.r5_drybuild2` tables, queried through the
SQL warehouse (`f461843f1d41af18`, profile `default`) on 2026-10-27 after notebooks
00_setup, 02_pipeline and 03_validate_results were run. Source row counts were verified
against `~/r5-notes.txt` before the pipeline ran (see DECISIONS.md). Quote only the numbers
below; never estimate.

## 0. Source row counts (verified against ~/r5-notes.txt, pre-pipeline)

| Table | Count |
|---|---|
| customers | 15,000 |
| inventory_weekly | 615,472 |
| products | 400 |
| promotions | 30 |
| sales_lines | 647,502 |
| stores | 60 |

## 1. Pipeline reconciliation (bronze = silver + quarantine + duplicates removed)

```sql
SELECT bronze_rows, silver_rows, quarantined_rows, duplicates_removed_est,
       round(median_latency_min,1) AS median_latency_min,
       round(p95_latency_min,1) AS p95_latency_min,
       round(late_share,4) AS late_share, latest_event_ts
FROM workspace.r5_drybuild2.gold_data_trust;
```

| bronze_rows | silver_rows | quarantined_rows | duplicates_removed_est | median_latency_min | p95_latency_min | late_share | latest_event_ts |
|---|---|---|---|---|---|---|---|
| 647,502 | 642,908 | 1,318 | 3,276 | 2.55 | 4.83 | 0.0194 (1.94%) | 2026-10-24T21:58:10Z |

Reconciliation check: 642,908 + 1,318 + 3,276 = 647,502 = bronze_rows. ✅ No row-count growth (no join fan-out).

Quarantine reasons:
```sql
SELECT reason, count(*) AS rows, count(DISTINCT store_id) AS stores_affected
FROM workspace.r5_drybuild2.silver_quarantine GROUP BY reason;
```
| reason | rows | stores_affected |
|---|---|---|
| unknown_sku | 1,318 | 60 |

## 2. THE fixed margin definition (CLAUDE.md, non-negotiable)

**Net margin = sales after discounts, less returns, less cost of goods sold** (discount is not
subtracted a second time). **Margin rate = net margin ÷ sales after returns.**

```sql
SELECT round(sum(net_sales),0) AS total_net_sales,
       round(sum(margin),0) AS total_net_margin,
       round(sum(margin)/sum(net_sales),4) AS margin_rate
FROM workspace.r5_drybuild2.gold_daily_store_category;
```

| total_net_sales | total_net_margin | margin_rate |
|---|---|---|
| $34,917,571 | $10,765,102 | **30.83%** |

**Second figure, same dollars, different denominator** (net margin ÷ a different sales table's
total, which nets differently) — appears ONLY labelled this way, never as the headline rate:

```sql
SELECT round(sum(net_margin)/sum(gross_net_sales),4) AS margin_rate_other_denominator
FROM workspace.r5_drybuild2.gold_margin_leakage;
```
Result: **28.95%** — same dollars, different denominator. Do not use as the headline.

## 3. Margin by category (Executive page)

```sql
SELECT category, round(sum(net_sales),0) AS net_sales, round(sum(margin),0) AS margin,
       round(sum(margin)/sum(net_sales),4) AS margin_rate
FROM workspace.r5_drybuild2.gold_daily_store_category GROUP BY category ORDER BY margin DESC;
```

| category | net_sales | margin | margin_rate |
|---|---|---|---|
| Apparel | $7,303,511 | $3,661,048 | 50.13% |
| Electronics | $15,632,871 | $2,647,774 | 16.94% |
| Home | $5,389,834 | $2,074,942 | 38.50% |
| Health & Beauty | $2,846,486 | $1,276,588 | 44.85% |
| Fresh | $1,853,230 | $576,428 | 31.10% |
| Grocery | $1,891,639 | $528,322 | 27.93% |

## 4. Margin by region

```sql
SELECT region, round(sum(net_sales),0) AS net_sales, round(sum(margin),0) AS margin,
       sum(transactions) AS transactions
FROM workspace.r5_drybuild2.gold_daily_store_category GROUP BY region ORDER BY net_sales DESC;
```

| region | net_sales | margin | transactions |
|---|---|---|---|
| Ontario | $10,699,488 | $3,309,388 | 136,324 |
| Prairies | $8,397,407 | $2,589,051 | 106,270 |
| Quebec | $7,682,634 | $2,360,729 | 97,721 |
| British Columbia | $4,575,153 | $1,414,179 | 58,162 |
| Atlantic | $3,562,888 | $1,091,755 | 45,206 |

## 5. Promotions: which earn their margin

```sql
SELECT promo_name, discount_pct, round(lift,2) AS volume_lift,
       round(margin_change_per_day,0) AS margin_change_per_day, verdict
FROM workspace.r5_drybuild2.gold_promo_effectiveness ORDER BY margin_change_per_day LIMIT 10;
```

Worst 10 (by margin change per day vs. baseline):

| promo_name | discount_pct | volume_lift | margin_change_per_day | verdict |
|---|---|---|---|---|
| Electronics promo 5 | 32% | 1.25x | -$6,590 | margin dilutive |
| Apparel promo 5 | 31% | 1.10x | -$3,244 | margin dilutive |
| Home promo 5 | 37% | 1.08x | -$2,872 | margin dilutive |
| Health & Beauty promo 5 | 38% | 1.40x | -$921 | margin dilutive |
| Electronics promo 2 | 12% | 1.76x | -$912 | margin dilutive |
| Fresh promo 5 | 38% | 1.39x | -$870 | margin dilutive |
| Grocery promo 5 | 34% | 1.23x | -$686 | margin dilutive |
| Electronics promo 4 | 10% | 2.05x | -$160 | margin dilutive |
| Fresh promo 4 | 7% | 1.77x | $301 | margin accretive |
| Grocery promo 3 | 10% | 2.16x | $325 | margin accretive |

Total promotions: 30. Dilutive promotions (verdict = "margin dilutive"): **8 of 30**.

```sql
SELECT round(sum(CASE WHEN verdict='margin dilutive' THEN margin_change_per_day*promo_days ELSE 0 END),0)
       AS total_margin_below_baseline,
       count(CASE WHEN verdict='margin dilutive' THEN 1 END) AS dilutive_promo_count,
       count(*) AS total_promos
FROM workspace.r5_drybuild2.gold_promo_effectiveness;
```
**Total margin below baseline across dilutive promotions: −$221,409 (ESTIMATE — vs. a modeled baseline sell-through rate).**

## 6. Stock-out exposure (Merchandising page)

```sql
SELECT category, count(*) AS store_sku_weeks_out, round(sum(est_lost_units),0) AS est_lost_units,
       round(sum(est_lost_margin),0) AS est_lost_margin
FROM workspace.r5_drybuild2.gold_stockout_exposure GROUP BY category ORDER BY est_lost_margin DESC;
```

| category | store_sku_weeks_out | est_lost_units | est_lost_margin |
|---|---|---|---|
| Apparel | 6,038 | 957 | $23,963 |
| Electronics | 2,860 | 468 | $19,289 |
| Home | 4,500 | 1,030 | $13,514 |
| Health & Beauty | 3,720 | 375 | $4,529 |
| Fresh | 5,295 | 745 | $1,952 |
| Grocery | 6,914 | 837 | $1,913 |

```sql
SELECT round(sum(est_lost_margin),0) AS total_est_lost_margin,
       round(sum(est_lost_units),0) AS total_est_lost_units,
       count(*) AS total_store_sku_weeks
FROM workspace.r5_drybuild2.gold_stockout_exposure;
```
**Total estimated stock-out margin: $65,160 (ESTIMATE — sales are not generated to dip during a
stock-out in this synthetic data; this is a modeled estimate, not a measured effect).**

## 7. Margin at risk before the next peak (THE ONE measure)

Margin at risk = promotion margin below baseline (−$221,409, ESTIMATE) + estimated stock-out
margin ($65,160, ESTIMATE) = **$286,569 at risk (both components labelled ESTIMATE)**, alongside
the loyalty retention curve below.

## 8. Loyalty cohort retention

```sql
WITH c0 AS (SELECT cohort_month, active_customers AS n0 FROM workspace.r5_drybuild2.gold_loyalty_cohorts WHERE months_since = 0)
SELECT g.months_since, round(avg(g.active_customers / c0.n0),3) AS share_still_buying
FROM workspace.r5_drybuild2.gold_loyalty_cohorts g JOIN c0 ON g.cohort_month = c0.cohort_month
WHERE g.months_since IN (0,1,3,6,12) GROUP BY g.months_since ORDER BY g.months_since;
```

| months_since | share_still_buying |
|---|---|
| 0 | 100.0% |
| 1 | 34.7% |
| 3 | 32.3% |
| 6 | 28.1% |
| 12 | 21.9% |

## 9. Margin leakage: returns and discounts by category

```sql
SELECT category, round(sum(returns_value)/sum(gross_net_sales),3) AS return_rate_value,
       round(sum(discount_given)/(sum(gross_net_sales)+sum(discount_given)),3) AS discount_rate
FROM workspace.r5_drybuild2.gold_margin_leakage GROUP BY category ORDER BY return_rate_value DESC;
```

| category | return_rate_value | discount_rate |
|---|---|---|
| Electronics | 8.8% | 1.8% |
| Apparel | 6.2% | 4.9% |
| Home | 3.1% | 1.9% |
| Health & Beauty | 1.9% | 1.4% |
| Fresh | 1.5% | 2.0% |
| Grocery | 1.0% | 1.5% |

Confirms the prompt's own claim: returns are highest in Electronics and Apparel.

## 10. Basket affinity (top "bought together" pairs)

```sql
SELECT sku_a, sku_b, together, round(lift,1) AS lift
FROM workspace.r5_drybuild2.gold_basket_affinity ORDER BY lift DESC LIMIT 10;
```

| sku_a | sku_b | together (baskets) | lift |
|---|---|---|---|
| SKU00230 | SKU00317 | 160 | 40.4x |
| SKU00182 | SKU00385 | 174 | 37.7x |
| SKU00229 | SKU00346 | 186 | 34.8x |
| SKU00166 | SKU00280 | 207 | 32.4x |
| SKU00221 | SKU00279 | 181 | 31.6x |

## Caveats to say out loud (from retail_kit/README.md)
- Stock-out loss is an ESTIMATE; sales are not generated to dip during a stock-out, so do not claim a measured effect.
- Customer email/phone are synthetic placeholders for a governance conversation, not real data.
- All figures are from a synthetic sample.
