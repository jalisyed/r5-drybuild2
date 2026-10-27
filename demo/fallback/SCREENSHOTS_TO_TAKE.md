# Screenshots to take — fallback if live access fails

All 6 are taken and embedded in `deck/Presales_Deck.pptx` (slides 10–15). Retake and re-embed
after any label change to the dashboard or app.

| # | Screenshot | Page / location | Maps to |
|---|---|---|---|
| 1 | Dashboard Executive page | Dashboard → Executive (margin by category, net sales by month, region chart, KPI row) | Deck slide 10 |
| 2 | Dashboard Merchandising and Promotions page | Dashboard → Merchandising and inventory (stock-out bar, worst-promotions table) | Deck slide 11 |
| 3 | Trust tile | Dashboard → Store operations and customer, bottom section (duplicates, late share, quarantine) | Deck slide 12 |
| 4 | Dashboard Key Figures page | Dashboard → Key Figures (margin rate fixed + other-denominator, margin at risk, loyalty milestones) | Deck slide 13 |
| 5 | App Home | App → Home (3 KPIs, two charts) | Deck slide 14 |
| 6 | App Ask the Genie | App → Ask the Genie, after asking a tested question (narrative + table) | Deck slide 15 |

To retake: open each page/app URL (see README.md), set any filters to the default (no filter
selected), and capture the full page. Save as `demo/fallback/screenshot_N.png` and re-insert into
the matching backup slide with python-pptx (see `deck/build_deck.py`'s diagram-embedding pattern)
if you want them in the deck rather than referenced by file path.
