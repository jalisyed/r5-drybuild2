import json, uuid

def newid():
    return uuid.uuid4().hex

CATALOG_SCHEMA = "workspace.r5_drybuild2"

TABLES = [
    "gold_daily_store_category",
    "gold_promo_effectiveness",
    "gold_stockout_exposure",
    "gold_loyalty_cohorts",
    "gold_margin_leakage",
    "gold_basket_affinity",
    "gold_data_trust",
]

COLUMN_CONFIGS = {
    "gold_daily_store_category": [
        {"column_name": "category", "enable_format_assistance": True, "enable_entity_matching": True,
         "description": ["Product category: Grocery, Fresh, Apparel, Home, Electronics, Health & Beauty."]},
        {"column_name": "region", "enable_format_assistance": True, "enable_entity_matching": True,
         "description": ["Sales region: Ontario, Quebec, British Columbia, Prairies, Atlantic."]},
        {"column_name": "margin", "description": ["Net margin: sales after discounts, less returns, less cost of goods sold. Never subtract discount a second time."]},
    ],
    "gold_promo_effectiveness": [
        {"column_name": "verdict", "enable_format_assistance": True, "enable_entity_matching": True,
         "description": ["'margin dilutive' = margin per day during the promotion is below the 28 days before it started. 'margin accretive' = margin per day rose."]},
        {"column_name": "category", "enable_format_assistance": True, "enable_entity_matching": True},
    ],
    "gold_stockout_exposure": [
        {"column_name": "est_lost_margin", "description": ["ESTIMATE only (expected weekly units x days out x unit margin) - always say so, never claim a measured loss."]},
        {"column_name": "category", "enable_format_assistance": True, "enable_entity_matching": True},
    ],
    "gold_margin_leakage": [
        {"column_name": "category", "enable_format_assistance": True, "enable_entity_matching": True},
    ],
}

TEXT_INSTRUCTIONS_CONTENT = [
    "## PURPOSE",
    "- Answer business questions about Birchwood Retail Group's margin, promotions, stock-outs, loyalty retention, basket affinity and data trust, for a retail leadership working session.",
    "- Users are a Chief Data Officer, a VP of Engineering, and a COO - assume business fluency, not necessarily SQL fluency.",
    "",
    "## DISAMBIGUATION",
    "- Currency is CAD.",
    "- 'Margin' or 'net margin' means sales after discounts, less returns, less cost of goods sold - never subtract discount a second time.",
    "- 'Margin rate' means net margin divided by sales after returns. On this data it is 30.83%. A different denominator (net margin over gross_net_sales in gold_margin_leakage) gives 28.95% - if asked, call that 'the same dollars, a different denominator', never a second headline rate.",
    "- 'Net sales' already reflects discounts and returns.",
    "- A promotion is 'margin dilutive' when its margin per day during the promotion is below the 28 days before it started (see gold_promo_effectiveness.verdict).",
    "- Default groupings are month and category unless the user asks for a different grain.",
    "",
    "## DATA QUALITY NOTES",
    "- gold_stockout_exposure.est_lost_margin and est_lost_units are ESTIMATES (expected weekly units x days out x unit margin). Sales are not generated to dip during a stock-out in this synthetic sample - always say 'estimate', never 'measured' or 'lost'.",
    "- A promotion's 'margin change per day' (gold_promo_effectiveness.margin_change_per_day) compares actual margin to a modeled 28-day-prior baseline - call this comparison an ESTIMATE too.",
    "- gold_data_trust and silver_quarantine describe pipeline freshness and data quality (latency, late share, duplicates, quarantined rows) - use these for any question about whether the data can be trusted.",
    "- Do NOT label figures from gold_daily_store_category (net_sales, margin, margin_rate), gold_margin_leakage (returns_value, discount_given, net_margin, return_rate, discount_rate), gold_loyalty_cohorts, or gold_basket_affinity as ESTIMATE - these are measured sums from the pipeline, not modeled estimates. Only gold_stockout_exposure figures and promotion-vs-baseline comparisons are ESTIMATES.",
    "",
    "## CONSTRAINTS",
    "- Never expose customer email or phone - these columns are not in any attached table, so do not attempt to join to tables that would expose them.",
    "- All data is synthetic, generated with a fixed seed. Say so if asked whether this is real customer data.",
    "",
    "## Instructions you must follow when providing summaries",
    "- Round percentages to two decimal places.",
    "- Label every stock-out or promotion dollar figure as an ESTIMATE when it comes from gold_stockout_exposure or involves a 'margin dilutive' baseline comparison in gold_promo_effectiveness.",
    "- State the margin rate as 30.83% using the fixed definition above unless the user explicitly asks for the other denominator.",
]

SAMPLE_QUESTIONS = [
    "Which categories earn our margin, and how is each trending?",
    "Which promotions lost us money, even though they sold more?",
    "Where are stock-outs costing us the most (estimated)?",
    "How does sales compare by region?",
    "How many loyalty customers are still buying 1, 3, 6 and 12 months after their first purchase?",
    "Which products are bought together most often?",
    "Where do returns and discounts eat into sales?",
    "How fresh and complete is the data behind these numbers?",
    "Which rows were rejected and why?",
]

EXAMPLE_SQLS = [
    ("Which categories earn our margin, and how is each trending?",
     f"SELECT category, round(sum(net_sales),0) AS net_sales, round(sum(margin),0) AS margin, round(sum(margin)/sum(net_sales),3) AS margin_rate FROM {CATALOG_SCHEMA}.gold_daily_store_category GROUP BY category ORDER BY margin DESC"),
    ("Which promotions lost us money, even though they sold more?",
     f"SELECT promo_name, discount_pct, round(lift,2) AS volume_lift, round(margin_change_per_day,0) AS margin_change_per_day, verdict FROM {CATALOG_SCHEMA}.gold_promo_effectiveness ORDER BY margin_change_per_day LIMIT 10"),
    ("Where are stock-outs costing us the most (estimated)?",
     f"SELECT category, count(*) AS store_sku_weeks_out, round(sum(est_lost_units),0) AS est_lost_units, round(sum(est_lost_margin),0) AS est_lost_margin FROM {CATALOG_SCHEMA}.gold_stockout_exposure GROUP BY category ORDER BY est_lost_margin DESC"),
    ("How does sales compare by region?",
     f"SELECT region, round(sum(net_sales),0) AS net_sales, round(sum(margin),0) AS margin, sum(transactions) AS transactions FROM {CATALOG_SCHEMA}.gold_daily_store_category GROUP BY region ORDER BY net_sales DESC"),
    ("How many loyalty customers are still buying 1, 3, 6 and 12 months after their first purchase?",
     f"WITH c0 AS (SELECT cohort_month, active_customers AS n0 FROM {CATALOG_SCHEMA}.gold_loyalty_cohorts WHERE months_since = 0) SELECT g.months_since, round(avg(g.active_customers / c0.n0),3) AS share_still_buying FROM {CATALOG_SCHEMA}.gold_loyalty_cohorts g JOIN c0 ON g.cohort_month = c0.cohort_month WHERE g.months_since IN (0,1,3,6,12) GROUP BY g.months_since ORDER BY g.months_since"),
    ("Which products are bought together most often?",
     f"SELECT sku_a, sku_b, together, round(lift,1) AS lift FROM {CATALOG_SCHEMA}.gold_basket_affinity ORDER BY lift DESC LIMIT 10"),
    ("Where do returns and discounts eat into sales?",
     f"SELECT category, round(sum(returns_value)/sum(gross_net_sales),3) AS return_rate_value, round(sum(discount_given)/(sum(gross_net_sales)+sum(discount_given)),3) AS discount_rate FROM {CATALOG_SCHEMA}.gold_margin_leakage GROUP BY category ORDER BY return_rate_value DESC"),
    ("How fresh and complete is the data behind these numbers?",
     f"SELECT bronze_rows, silver_rows, quarantined_rows, duplicates_removed_est, round(median_latency_min,1) AS median_latency_min, round(p95_latency_min,1) AS p95_latency_min, round(late_share,4) AS late_share, latest_event_ts FROM {CATALOG_SCHEMA}.gold_data_trust"),
    ("Which rows were rejected and why?",
     f"SELECT reason, count(*) AS rows, count(DISTINCT store_id) AS stores_affected FROM {CATALOG_SCHEMA}.silver_quarantine GROUP BY reason"),
]

tables_payload = []
for t in sorted(TABLES):
    entry = {"identifier": f"{CATALOG_SCHEMA}.{t}"}
    if t in COLUMN_CONFIGS:
        entry["column_configs"] = sorted(COLUMN_CONFIGS[t], key=lambda c: c["column_name"])
    tables_payload.append(entry)

payload = {
    "version": 2,
    "config": {
        "sample_questions": sorted(
            [{"id": newid(), "question": [q]} for q in SAMPLE_QUESTIONS], key=lambda x: x["id"]
        )
    },
    "data_sources": {"tables": tables_payload},
    "instructions": {
        "example_question_sqls": sorted(
            [{"id": newid(), "question": [q], "sql": [s]} for q, s in EXAMPLE_SQLS], key=lambda x: x["id"]
        ),
        "text_instructions": [{"id": newid(), "content": TEXT_INSTRUCTIONS_CONTENT}],
    },
}

with open("genie/serialized_space.json", "w") as f:
    json.dump(payload, f, indent=2)

print("Written genie/serialized_space.json")
print("Tables:", [t["identifier"] for t in tables_payload])
print("Sample questions:", len(payload["config"]["sample_questions"]))
print("Example SQLs:", len(payload["instructions"]["example_question_sqls"]))
