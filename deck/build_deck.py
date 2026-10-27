"""Fill Presales_Deck_Template_v3.pptx placeholders for the Birchwood Retail Group pre-sales
role-play. Run from the repo root: python3 deck/build_deck.py
Only replaces exact-match run text (template placeholders are single runs), so existing
formatting (Calibri, white background, layout) is untouched. Does not touch slides a human
has hand-edited (checked via HAND_EDITED_MARKER in slide notes before running, if present)."""
import copy
from pptx import Presentation
from pptx.util import Emu

SRC = "deck/Presales_Deck_Template_v3.pptx"
OUT = "deck/Presales_Deck.pptx"

# Exact-match single-run replacements, keyed by the literal placeholder text in the template.
REPLACEMENTS = {
    "[Customer]: [their outcome]":
        "Birchwood Retail Group: Plan the next peak with one trusted view",
    "[Dashboard / app / Genie], on data shaped like yours.":
        "An AI/BI dashboard, a Genie space and an app, on data shaped like yours.",
    "Syed Javed Ali  |  Databricks Solutions Architect  |  [Date]":
        "Syed Javed Ali  |  Databricks Solutions Architect  |  Thursday 29 October 2026",

    # Slide 2 - personas
    "[Name, title]": None,  # handled positionally below (appears 3x, same text)
    "You said: [quote or paraphrase]": None,
    "You said: [quote]": None,
    "Success: [what they want]": None,

    # Slide 4 - solution map
    "[assumed: e.g. POS, e-commerce, loyalty]":
        "POS daily export, weekly inventory snapshot, loyalty file, promotions calendar (assumed; all synthetic)",
    "[problem it solves]": None,  # 4x, positional
    "[Delta tables, quality checks]":
        "Bronze (raw + lineage) → silver (typed, deduped, quarantined)",
    "[curated, governed]":
        "7 gold tables: margin leakage, promotions, stock-outs, loyalty, basket affinity, data trust",
    "[Dashboard / Genie / App]":
        "AI/BI dashboard (5 pages), Genie space, Streamlit app",

    # Slide 5 - pilot plan
    "[Start date] to [+2 weeks]": "Mon 2 Nov to Fri 13 Nov 2026",
    "[One workload, one dataset]":
        "Margin, promotions and stock-out exposure on this dataset",
    "[Named people on both sides]":
        "Named owner on both sides, agreed at kickoff",
    "[1 week]": "16 to 20 Nov 2026 (1 week)",
    "[Tweaks from what we learn]":
        "Tweaks from what we learn",
    "[Review against the measure]":
        "Review against the measure",
    "[Week of Thanksgiving]": "Week of 23 Nov 2026",
    "[Rollout to the first teams]":
        "Rollout to the first teams",
    "[Owners and support]":
        "Owners and support",
    "Success at day 14: [measure 1]  |  [measure 2]  |  [measure 3]":
        "Success at end of pilot: one governed margin number in use  |  promotion verdicts available within days of a promotion ending  |  every pipeline break explained",
    "What I need from you: [data access]  |  [two named people]  |  [a decision date]":
        "What I need from you: read access to a POS / inventory / loyalty / promotions sample  |  two named owners (data and business)  |  a go/no-go decision by Fri 13 Nov 2026",

    # Slide 6 - next steps
    "[Date]": None,  # positional, 2x
    "[Date + 2 wks]": "Fri 13 Nov 2026",
    "Day-14 review": "End-of-pilot review",
    "[Owner on both sides]": "Owner on both sides",
    "[First teams]": "First teams",
    "Anything that would stop us starting on [date]?":
        "Anything that would stop us starting on Mon 2 Nov 2026?",

    # Slide 7 backup - architecture / data model / toolchain image placeholders
    "[Insert architecture diagram image]":
        "See demo/diagrams/architecture.jpg",
    "[Insert data model image]":
        "See demo/diagrams/data_model.jpg",
    "[Insert toolchain diagram: Claude Code, Databricks CLI, Databricks, Git]":
        "See demo/diagrams/toolchain.jpg — Claude Code, Databricks CLI, Databricks, Git",
}

# Slide 2 persona rows, in shape order (Executive, Technical leader, Business/analytics leader)
PERSONA_FILLS = [
    ("Daniel Osei, Chief Data Officer",
     "You said: “I cannot tell the board whether it keeps customers... I don't know which file to trust.”",
     "Success: One trusted view of loyalty retention and margin, and clarity on who can see customer data."),
    ("Tomas Rivera, VP of Engineering",
     "You said: “When a file arrives twice we reprocess and revenue is counted twice... I have no good way to test a change before it goes live.”",
     "Success: Safe reprocessing, a way to test changes before release, early warning on bad data, open formats."),
    ("Maria Santos, Chief Operating Officer",
     "You said: “Every December we run out of our best sellers... I am guessing.”",
     "Success: See where stock-outs and promotions cost margin, ahead of the next peak, and what to change first."),
]

# Slide 4 "why it matters" fills, in shape order (Sources, Land and clean, Business-ready data, What you use)
WHY_IT_MATTERS_FILLS = [
    "Explains why a file landing twice can double-count revenue (Tomas's concern)",
    "Duplicates and bad rows are counted and explained, not silently dropped",
    "One governed margin definition, used on every page, for every persona",
    "Each persona's question answered in the format they will actually use",
]

# Slide 6 date fills, in shape order (kickoff date, adjustment-complete date)
SLIDE6_DATES = ["Mon 2 Nov 2026", "Fri 20 Nov 2026"]

VALUE_TABLE = [
    ["Who", "Today", "With this", "Business value, and how we will know"],
    ["Executive",
     "A different number every time I ask for loyalty retention or margin",
     "One governed margin definition (30.83%) and one loyalty retention curve, from the same gold tables every time",
     "One number the board can trust: measured by the margin rate reading the same on every page"],
    ["Technical leader",
     "A file landing twice means revenue counted twice; changes reach production untested",
     "A pipeline that counts and reconciles duplicates, late arrivals and bad rows automatically",
     "Safe reprocessing and a way to test changes: measured by every run reconciling (bronze = silver + quarantine + duplicates removed) on our run"],
    ["Business / analytics",
     "Planning the next peak six weeks out, guessing which products stock out and which promotions to repeat",
     "Stock-out exposure by category (ESTIMATE) and a verdict on every promotion, ahead of the peak",
     "Decisions made sooner, before the peak: measured by promotion verdicts available within days of a promotion ending"],
]

ASSUME_TABLE = [
    ["Assumption", "Why it is reasonable", "What changes if wrong"],
    ["POS transaction files land as a daily export; inventory is a weekly snapshot per store and product",
     "Matches the prompt's own description of the sources",
     "Add a connector for the real cadence; pipeline design is unchanged"],
    ["Loyalty file comes from the program vendor, separate from POS",
     "Matches the prompt's description of a loyalty program",
     "Point the pipeline at the real vendor export"],
    ["All data in this build is synthetic, generated with a fixed seed",
     "No customer data used before a signed pilot agreement",
     "Re-run the same pipeline on real data in the pilot"],
]


def replace_exact_runs(slide, mapping):
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if run.text in mapping and mapping[run.text] is not None:
                    run.text = mapping[run.text]


def fill_positional(slide, placeholder_text, values):
    """Replace each occurrence of placeholder_text, in shape order, with successive values."""
    it = iter(values)
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if run.text == placeholder_text:
                    try:
                        run.text = next(it)
                    except StopIteration:
                        return


def fill_table(shape, rows):
    table = shape.table
    for r, row_vals in enumerate(rows):
        for c, val in enumerate(row_vals):
            cell = table.cell(r, c)
            # preserve formatting of first run, replace its text, clear the rest
            tf = cell.text_frame
            if tf.paragraphs and tf.paragraphs[0].runs:
                tf.paragraphs[0].runs[0].text = val
                for extra in tf.paragraphs[0].runs[1:]:
                    extra.text = ""
            else:
                tf.text = val


def set_slide_hidden(slide, hidden=True):
    sp = slide._element
    if hidden:
        sp.set("show", "0")
    elif sp.get("show") is not None:
        del sp.attrib["show"]


def main():
    prs = Presentation(SRC)
    slides = prs.slides

    # Slide 1
    replace_exact_runs(slides[0], REPLACEMENTS)

    # Slide 2 - personas (3 groups of Name/Said/Success)
    s2 = slides[1]
    name_it = iter(PERSONA_FILLS)
    groups = list(PERSONA_FILLS)
    gi = 0
    for shape in s2.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if run.text == "[Name, title]":
                    run.text = groups[min(gi, 2)][0]
                elif run.text in ("You said: [quote or paraphrase]", "You said: [quote]"):
                    run.text = groups[min(gi, 2)][1]
                elif run.text == "Success: [what they want]":
                    run.text = groups[min(gi, 2)][2]
                    gi += 1  # advance after the last field of each group

    # Slide 3 - value table + footnote
    s3 = slides[2]
    for shape in s3.shapes:
        if shape.has_table and shape.name == "valuetable":
            fill_table(shape, VALUE_TABLE)
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if run.text == "Faster is the means. The value is: [what faster lets the business do].":
                        run.text = "Faster is the means. The value is: decisions made before the peak, not after it."
                    if run.text == "Targets are agreed with you at the start of the pilot. Figures marked ASSUMPTION are mine.":
                        run.text = "All figures are from a synthetic sample."

    # Slide 4 - solution map
    s4 = slides[3]
    replace_exact_runs(s4, REPLACEMENTS)
    fill_positional(s4, "[problem it solves]", WHY_IT_MATTERS_FILLS)

    # Slide 5 - pilot plan
    replace_exact_runs(slides[4], REPLACEMENTS)

    # Slide 6 - next steps
    s6 = slides[5]
    replace_exact_runs(s6, REPLACEMENTS)
    fill_positional(s6, "[Date]", SLIDE6_DATES)

    # Slide 7 - assumptions table
    s7 = slides[6]
    for shape in s7.shapes:
        if shape.has_table and shape.name == "assume":
            fill_table(shape, ASSUME_TABLE)

    # Slide 8, 9, 14 - diagram placeholders (architecture, data model, toolchain)
    replace_exact_runs(slides[7], REPLACEMENTS)
    replace_exact_runs(slides[8], REPLACEMENTS)
    replace_exact_runs(slides[13], REPLACEMENTS)

    # Slides 10-13 - screenshot backup slides: give them real names instead of generic numbers
    screenshot_titles = [
        "Backup: screenshot — Dashboard Executive page",
        "Backup: screenshot — Dashboard Key Figures page",
        "Backup: screenshot — App Home",
        "Backup: screenshot — App Ask the Genie",
    ]
    screenshot_bodies = [
        "See demo/fallback/SCREENSHOTS_TO_TAKE.md — Executive page (net sales, margin, margin rate, region)",
        "See demo/fallback/SCREENSHOTS_TO_TAKE.md — Key Figures page (margin at risk, loyalty retention, trust recap)",
        "See demo/fallback/SCREENSHOTS_TO_TAKE.md — App Home (headline KPIs, two charts)",
        "See demo/fallback/SCREENSHOTS_TO_TAKE.md — App Ask the Genie (a tested question, answered)",
    ]
    for idx, slide_idx in enumerate([9, 10, 11, 12]):
        slide = slides[slide_idx]
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if run.text.startswith("Backup: screenshot"):
                        run.text = screenshot_titles[idx]
                    elif run.text.startswith("[Insert screenshot"):
                        run.text = screenshot_bodies[idx]

    # Hide all backup slides (7-14, zero-indexed 6-13); keep 1-6 visible
    for i, slide in enumerate(slides):
        set_slide_hidden(slide, hidden=(i >= 6))

    # Embed the generated diagram images into their backup slides, on top of the text placeholder
    diagram_slots = [
        (7, "demo/diagrams/architecture.jpg"),
        (8, "demo/diagrams/data_model.jpg"),
        (13, "demo/diagrams/toolchain.jpg"),
    ]
    for slide_idx, img_path in diagram_slots:
        slide = slides[slide_idx]
        box_shape = next(s for s in slide.shapes if s.name == "ph")
        left, top, width, height = box_shape.left, box_shape.top, box_shape.width, box_shape.height
        slide.shapes.add_picture(img_path, left, top, width=width)

    prs.save(OUT)
    print(f"Saved {OUT}")

    # Verify show="0" survived the save
    prs2 = Presentation(OUT)
    for i, slide in enumerate(prs2.slides):
        show = slide._element.get("show")
        print(f"Slide {i+1}: show={show!r} ({'HIDDEN' if show == '0' else 'visible'})")


if __name__ == "__main__":
    main()
