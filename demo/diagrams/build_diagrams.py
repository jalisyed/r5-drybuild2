"""Generate architecture.jpg, data_model.jpg and toolchain.jpg: simple box diagrams with
strictly orthogonal connectors and no line crossing a box, for the deck's hidden backup slides."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

NAVY = "#1D425C"
BLUE = "#2272B4"
GREY = "#8A8F98"
LIGHT = "#F2F4F7"
TEXT = "#11171C"


def box(ax, x, y, w, h, text, fc=LIGHT, ec=NAVY, fontsize=10, fontweight="normal"):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
        linewidth=1.5, edgecolor=ec, facecolor=fc
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, color=TEXT, fontweight=fontweight, wrap=True)


def h_arrow(ax, x1, x2, y, color=NAVY):
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5))


def v_arrow(ax, x, y1, y2, color=NAVY):
    ax.annotate("", xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5))


def save(fig, name):
    fig.savefig(f"demo/diagrams/{name}.jpg", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved demo/diagrams/{name}.jpg")


# ---------- Architecture: built vs assumed ----------
fig, ax = plt.subplots(figsize=(12, 4.5))
ax.set_xlim(0, 12)
ax.set_ylim(0, 4.5)
ax.axis("off")

box(ax, 0.3, 1.8, 2.2, 1.4, "Sources\n(assumed)\nPOS daily export\nWeekly inventory\nLoyalty file\nPromotions calendar", fc="#EDEFF2", fontsize=8.5)
box(ax, 3.0, 1.8, 2.2, 1.4, "Land & clean\nBronze → Silver\nquarantine, dedupe", fc=LIGHT, fontsize=9)
box(ax, 5.7, 1.8, 2.2, 1.4, "Business-ready\n7 gold tables\n(margin, promo,\nstock-out, loyalty)", fc=LIGHT, fontsize=8.5)
box(ax, 8.4, 1.8, 3.2, 1.4, "What you use\nAI/BI dashboard (5 pages)\nGenie space • Streamlit app", fc=LIGHT, fontsize=9)

h_arrow(ax, 2.5, 3.0, 2.5)
h_arrow(ax, 5.2, 5.7, 2.5)
h_arrow(ax, 7.9, 8.4, 2.5)

ax.add_patch(mpatches.Rectangle((0.3, 0.3), 1.0, 0.5, fc="#EDEFF2", ec=NAVY))
ax.text(1.5, 0.55, "Assumed / not built", va="center", fontsize=9)
ax.add_patch(mpatches.Rectangle((5.5, 0.3), 1.0, 0.5, fc=LIGHT, ec=NAVY))
ax.text(6.7, 0.55, "Built and shown today", va="center", fontsize=9)

ax.set_title("Birchwood Retail — Architecture: built vs. assumed", fontsize=13, color=NAVY, pad=15)
save(fig, "architecture")

# ---------- Data model: star schema ----------
fig, ax = plt.subplots(figsize=(10, 7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis("off")

box(ax, 3.6, 3.3, 2.8, 1.4, "silver_sales_lines\n(fact: 1 row per\nsale line)", fc=NAVY, ec=NAVY, fontsize=9, fontweight="bold")
for t in ax.texts[-1:]:
    t.set_color("white")

dims = [
    ("dim_store\n(store, region, banner)", 0.3, 5.6),
    ("dim_product\n(category, brand, cost/price)", 7.0, 5.6),
    ("dim_customer\n(loyalty flag)", 0.3, 1.0),
    ("dim_date\n(calendar)", 7.0, 1.0),
    ("dim_promotion\n(promo calendar)", 3.6, 0.6),
]
for text, x, y in dims:
    box(ax, x, y, 2.6, 1.2, text, fc=LIGHT, fontsize=8.5)

cx, cy = 3.6 + 1.4, 3.3 + 0.7
h_arrow(ax, 1.6, 3.6, 5.9, color=GREY)   # store -> fact (approx)
v_arrow(ax, 1.6, 5.6, 4.7, color=GREY)
h_arrow(ax, 6.4, 7.0, 5.9, color=GREY)
v_arrow(ax, 8.3, 5.6, 4.7, color=GREY)
v_arrow(ax, 1.6, 2.2, 3.3, color=GREY)
v_arrow(ax, 8.3, 2.2, 3.3, color=GREY)
v_arrow(ax, cx, 1.8, 3.3, color=GREY)

box(ax, 0.3, 7.0, 9.3, 0.8,
    "Gold tables (one per business question): margin_leakage • promo_effectiveness • stockout_exposure • loyalty_cohorts • basket_affinity • data_trust",
    fc="#EDEFF2", fontsize=8)

ax.set_title("Birchwood Retail — Data model (star schema → gold)", fontsize=13, color=NAVY, pad=10)
save(fig, "data_model")

# ---------- Toolchain ----------
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 3.2)
ax.axis("off")

box(ax, 0.3, 1.0, 2.1, 1.2, "Claude Code\n(this build)", fontsize=9)
box(ax, 2.9, 1.0, 2.1, 1.2, "Databricks CLI\n+ skills", fontsize=9)
box(ax, 5.5, 1.0, 2.1, 1.2, "Databricks\n(UC, SQL warehouse,\nApps, Genie)", fontsize=8.5)
box(ax, 8.1, 1.0, 1.6, 1.2, "Git\nrepo", fontsize=9)

h_arrow(ax, 2.4, 2.9, 1.6)
h_arrow(ax, 5.0, 5.5, 1.6)
h_arrow(ax, 7.6, 8.1, 1.6)
v_arrow(ax, 1.35, 1.0, 0.3, color=GREY)
ax.text(1.35, 0.15, "commits throughout the build", ha="center", fontsize=7.5, color=GREY)

ax.set_title("How this was built (for the debrief)", fontsize=13, color=NAVY, pad=10)
save(fig, "toolchain")
