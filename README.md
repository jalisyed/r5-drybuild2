# Birchwood Retail Group — pre-sales demo (dry run 5)

## Problem
Three Birchwood Retail Group leaders need to plan their next peak season (six weeks out) with
better information than last year: the board can't get a trusted number on loyalty retention or
margin, best sellers ran out at last December's peak with January clearance promotions following,
a file arriving twice double-counts revenue, and untested changes have reached production.

## Approach
One governed margin definition (net margin = sales after discounts, less returns, less cost of
goods sold; margin rate = net margin ÷ sales after returns), computed once and reused everywhere:
a 5-page AI/BI dashboard, a Genie space, and a Streamlit app. Built on `retail_kit`'s synthetic
retail dataset (24 months, 60 stores, ~400 products, ~30 promotions), run through a
bronze/silver/quarantine pipeline that reconciles duplicates and late arrivals on every run.

## What's real vs. assumed
- **Real (built and verified)**: all data is synthetic (fixed seed), but every figure quoted
  anywhere comes from a query run against the pipeline's output — see `RESULTS.md` for each figure
  and the exact SQL that produced it. The pipeline's reconciliation (bronze = silver + quarantine +
  duplicates removed), the dashboard, the Genie space, and the app are all live and tested.
- **Assumed (stated, not built)**: the data sources — POS daily export, weekly inventory snapshot,
  loyalty file from the program vendor, promotions calendar — are assumptions I can explain, not
  confirmed integrations. Alerting, schema-change detection, access-control enforcement, and
  promotion attribution modeling are named as pilot additions, not demonstrated live.
- **Labelled estimates**: stock-out exposure dollars and promotion-vs-baseline margin figures are
  modeled ESTIMATES (this synthetic sample doesn't generate a measurable sales dip during a
  stock-out) — always called ESTIMATE or "below baseline," never "lost" or "saved."

## How to run
1. Prerequisites: Databricks CLI, profile `default` (see `~/.databrickscfg`), catalog `workspace`.
2. Pipeline: notebooks already run — `retail_kit/notebooks/00_setup.ipynb`,
   `02_pipeline.ipynb`, `03_validate_results.ipynb` (notebook 01, data generation, is **not** run
   — the data was generated once and backed up; see `~/r5-notes.txt` for source row counts).
3. Dashboard: "Birchwood Retail: Performance and Trust" — draft view (publishing works on Free
   Edition but the `/published` URL 404s, so always present from draft):
   `https://dbc-be4eeba5-e3b8.cloud.databricks.com/sql/dashboardsv3/01f1d22c47d2198dbb66a7f52412e4ae`
4. Genie: space "Birchwood Retail: Margin, Promotions, Loyalty and Trust"
   (`01f1d22ebf4217ca9ca00cabefb2a93f`) — see `genie/GENIE_VALIDATION.md` for validated questions.
5. App: `r5-drybuild2-retail` —
   `https://r5-drybuild2-retail-7474657164729936.aws.databricksapps.com` — 3 pages (Home, Ask the
   Data, Ask the Genie). If it's been idle ~24 hours (Free Edition limit), restart it:
   Compute → Apps → r5-drybuild2-retail → Start.
6. Grants: `sql/grants.sql` — rerun after any `CREATE OR REPLACE` of the pipeline tables.

## Repo layout
- `RESULTS.md` / `DECISIONS.md` — every figure with its query; every build decision with its why.
- `dashboards/` — the AI/BI dashboard JSON and working reference.
- `genie/` — the Genie space build script and validation log.
- `app/` — the Streamlit app (Home, Ask the Data, Ask the Genie).
- `deck/` — `Presales_Deck.pptx` (6 visible slides, 10 hidden backup slides, all 6 fallback
  screenshots embedded) and its build script.
- `story/` — `STORYLINE.md` (minute map), `OBJECTIONS.md`, `DEBRIEF.md`.
- `demo/` — `DEMO_SCRIPT.md` (click path), `diagrams/`, `fallback/` (screenshot checklist).
- `sql/grants.sql` — Unity Catalog grants for the user, the app, and Genie.
