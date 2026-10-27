# OBJECTIONS — likely questions per persona, answered in four moves

Each answer: **Acknowledge → Clarify → Reframe to business value → Small next step.**
Figures below are from RESULTS.md. Never improvise a number live — if asked for one not in
RESULTS.md, use the "I don't know" pattern at the bottom.

## Daniel Osei, Chief Data Officer

1. **"How do I know this margin number is the same one finance uses?"**
   Acknowledge: that's exactly the trust problem you described. Clarify: every page, the Genie
   space, and the app read the same gold table with one written definition — net margin = sales
   after discounts, less returns, less cost of goods sold. Reframe: the board gets one number,
   not a different one depending on who ran the query. Next step: in the pilot, we point this at
   your actual POS/loyalty export and the finance team's definition is the one we encode.

2. **"Who can actually see customer-level loyalty data today?"**
   Acknowledge: that's a fair governance question before any pilot starts. Clarify: Unity Catalog
   grants (sql/grants.sql) control table and schema access per principal; we haven't built
   enforcement workflows or row-level masking in this sample. Reframe: the pilot is the place to
   design that access model against your real org chart. Next step: bring your security/governance
   contact to the pilot kickoff.

3. **"What's actually different about this vs. what IT already reports?"**
   Acknowledge: you already get reports today. Clarify: the difference isn't the chart, it's the
   governed definition underneath it — one margin rate, traceable to one query, reused everywhere.
   Reframe: it's not more dashboards, it's fewer different numbers. Next step: bring your current
   report to the pilot and we compare definitions side by side.

4. **"How much does this cost?"**
   Acknowledge: a fair question. Clarify: pricing is out of scope for this working session — the
   account team covers that. Reframe: today is about whether the approach solves the trust
   problem; cost is a separate conversation. Next step: happy to set that up as a follow-on.

5. **"What happens to this data after the pilot?"**
   Acknowledge: reasonable to ask before committing data. Clarify: this build used only synthetic
   data; real data in the pilot stays in your workspace under your Unity Catalog governance.
   Reframe: nothing leaves your environment as part of this exercise. Next step: confirm your
   data-residency requirements at kickoff.

## Tomas Rivera, VP of Engineering

1. **"What happens when the same file lands twice in production, not just in a demo?"**
   Acknowledge: that's the exact incident you described. Clarify: the pipeline reconciles on every
   run — bronze rows = silver rows + quarantined rows + duplicates removed (647,502 = 642,908 +
   1,318 + 3,276 on our run). Reframe: duplicates are counted and removed, not silently
   double-counted into revenue. Next step: in the pilot we point this at your real file-arrival
   pattern and watch it reconcile on your data.

2. **"How would I test a pipeline change before it goes live?"**
   Acknowledge: you said you found out from finance last time, not before. Clarify: we haven't
   built a CI/test harness in this sample — that's a pilot addition. Reframe: the pipeline's
   idempotent, rerunnable design (CREATE OR REPLACE, no destructive steps) is what makes safe
   testing possible once that harness exists. Next step: we scope the test harness together in
   the pilot.

3. **"Why not just use our existing warehouse/ETL tool?"**
   Acknowledge: you have something today. Clarify: this isn't about replacing it wholesale — it's
   about one governed layer for the business questions you named. Reframe: the design is open
   formats (Delta), not a lock-in black box. Next step: the pilot can run alongside your current
   tool, not instead of it, for the two-week window.

4. **"What alerts me when something breaks?"**
   Acknowledge: good operational question. Clarify: alerting and schema-change detection are not
   built in this sample — they're pilot additions. Reframe: what is built is that breaks are
   visible and explained (quarantine table with a reason column), not hidden. Next step: we design
   the alerting channel with your team in the pilot.

5. **"How much does this cost to run?"**
   Acknowledge: fair, but out of scope today — the account team covers pricing. Reframe: today is
   about whether the reprocessing and trust problem is solved. Next step: follow-on conversation
   with the account team.

## Maria Santos, Chief Operating Officer

1. **"Can this tell me which specific products to reorder right now, not just that stock-outs
   happened historically?"**
   Acknowledge: that's the real ask — action, not history. Clarify: today's build shows stock-out
   exposure by category (an ESTIMATE: $65,160 across the sample), not yet a store/SKU reorder
   list. Reframe: the gold table (gold_stockout_exposure) is already at store/SKU/week grain — a
   reorder view is a short next step, not a new build. Next step: scope that exact view in the
   pilot's adjustment week.

2. **"How far in advance would this have warned us last December?"**
   Acknowledge: that's the six-week-out planning problem you named. Clarify: we haven't run this
   against last December's real data — this sample is synthetic. Reframe: the stock-out and
   promotion views are built so a leading-indicator check against your real peak is the pilot's
   first output. Next step: bring last December's actuals to the pilot for that comparison.

3. **"Which promotions should I cut next peak, concretely?"**
   Acknowledge: this is the guesswork you're trying to end. Clarify: 8 of 30 promotions in the
   sample verdict "margin dilutive" — margin below a modeled baseline (ESTIMATE), worst being a
   32% discount with only 1.25x volume lift. Reframe: the worst-promotions table on the dashboard
   is exactly the cut list, ranked by dollars below baseline. Next step: run the same query against
   your real promotion calendar before the next peak.

4. **"Is the stock-out number real or a guess?"**
   Acknowledge: important distinction. Clarify: it's explicitly labelled ESTIMATE — modeled from
   expected units × days out × unit margin, because this synthetic sample doesn't generate a real
   sales dip during a stock-out. Reframe: on real data, this becomes measurable; here it's a
   credible placeholder for the shape of the answer. Next step: pilot runs this on real weekly
   inventory snapshots.

5. **"What do I tell my team to change first, Monday morning?"**
   Acknowledge: that's the "what to change first" ask from the brief. Clarify: today's view points
   to two things — the categories with highest stock-out exposure (Apparel, Electronics) and the
   specific promotions below baseline. Reframe: it's a short list, not a dashboard to get lost in.
   Next step: the pilot's first deliverable is that short list against your real data.

## Answering "I don't know"
Say so directly: "I don't have that number in front of me — I don't want to guess." Then redirect:
"That's exactly the kind of question the pilot is built to answer against your real data," or
"Let me note that and confirm it with the account team." Never estimate a figure live that isn't
already in RESULTS.md.

## Technical choice → business problem it serves

| Technical choice | Business problem it serves |
|---|---|
| Bronze/silver/quarantine layering, reconciled every run | Tomas: duplicate files double-counting revenue |
| One margin definition as a dataset-level measure, reused everywhere | Daniel: a different number every time he asks |
| Promotion verdict (margin dilutive/accretive) vs. a 28-day baseline | Maria: which promotions to cut before the next peak |
| Stock-out exposure at store/SKU/week grain, labelled ESTIMATE | Maria: where empty shelves cost the most |
| Unity Catalog grants (sql/grants.sql) per principal | Daniel: who can see customer data |
| Idempotent CREATE OR REPLACE pipeline, no destructive steps | Tomas: safe reprocessing and testability |
| Genie space with instructions pinning the margin definition | Daniel and Maria: self-service without re-deriving the formula wrong |

## What I am NOT claiming
- This is synthetic data, generated with a fixed seed — not Birchwood's real transactions.
- Stock-out dollar figures and promotion-vs-baseline figures are modeled ESTIMATES, not measured
  losses — sales are not generated to dip during a stock-out in this sample.
- No alerting, schema-change detection, access-control enforcement, or attribution modeling is
  built — these are named as pilot additions, not demonstrated live.
- Pipeline latency figures (median 2.6 min, p95 4.8 min) come from the synthetic data's own
  generated timestamps, not a measurement of live production throughput — never present them as
  "how fast our pipeline runs."
- "Reconciles on our run" — not a claim that every run, on all data, will always reconcile cleanly.
