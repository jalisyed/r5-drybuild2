# DEBRIEF — 5-minute story for the 15-minute debrief

## Tools used
- **Claude Code** — paired through the whole build: planning, Databricks CLI operations,
  dashboard/Genie/app JSON authoring, deck generation via python-pptx, this story pack.
- **Databricks CLI + skills** (`databricks-core`, `databricks-aibi-dashboards`,
  `databricks-genie-agents`, `databricks-apps-python`, `databricks-unity-catalog`) — every SQL
  statement, dashboard deploy, Genie space create/update, and app deploy ran through the CLI, not
  the workspace UI, except the two steps the CLI doesn't cover (dashboard widget binding fallback,
  and attaching the app's SQL warehouse/Genie resources).
- **Databricks Free Edition (serverless)** — one 2X-Small SQL warehouse, Unity Catalog, AI/BI
  dashboards, Genie, and Apps, all on the free tier.

## What I checked in AI output, and how
- **Every number before it reached a slide, the dashboard, or the app**: ran the query myself
  against the warehouse first, wrote it to RESULTS.md with the exact SQL, and only then referenced
  it elsewhere — never let a generated figure go unverified.
- **The dashboard's field bindings**: canary-first build order — one page, one dataset, two
  widgets — verified with `lakeview get` before building the full 20-widget dashboard, per the
  project's own lessons-learned from earlier dry runs.
- **A real bug the user caught, not me**: the Executive page's Net Sales, Margin Rate, and
  Transactions KPIs failed with "circular reference detected" because a dataset-level measure
  named "Transactions" collided case-insensitively with the raw source column `transactions`.
  Found the root cause, renamed the measure, redeployed, and the user confirmed the fix.
- **Genie's own answers**: ran 5 of its 9 sample questions against the Genie space and compared
  every figure to RESULTS.md by hand. Caught a real quality issue this way — Genie's first answer
  mislabeled a measured figure (margin by category) as "ESTIMATE." Fixed by tightening the
  space's text instructions to name exactly which tables are modeled estimates vs. measured sums,
  then re-tested and confirmed.
- **The app**: after the user reported "is not a valid endpoint id," diagnosed that the running
  app process had started before the SQL warehouse/Genie resources were attached in the UI, so it
  never picked up the injected environment variables — fixed with a stop/start, not a code change.

## What I assumed
- Data sources: POS transaction files (daily export), a weekly inventory snapshot feed, a loyalty
  file from the program vendor, and a promotions calendar — stated as assumptions in the deck's
  backup assumptions slide and in RESULTS.md/the dashboard glossary, not asserted as fact.
- The fixed margin definition and the pilot dates (Mon 2 Nov – Fri 13 Nov 2026 POC, 16–20 Nov
  adjustment, week of 23 Nov go-live) came directly from the project's standing instructions, not
  invented.

## What I would do next
- Build the CI/test-harness piece for pipeline changes (named as a pilot addition, not built) —
  this is Tomas's second-biggest ask after safe reprocessing.
- Add a store/SKU-level reorder view on top of `gold_stockout_exposure` — Maria's follow-up ask
  for something actionable, not just historical.
- Design the access-control enforcement workflow with Daniel's team, building on the Unity Catalog
  grants already in `sql/grants.sql`.
- Re-run the whole pipeline against a real (not synthetic) sample as the pilot's first step, and
  reconcile the fixed margin definition against finance's own number.
