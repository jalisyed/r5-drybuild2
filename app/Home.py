"""Home: Birchwood Retail pilot demo. Streamlit on Databricks Apps.
Three headline numbers under the fixed margin definition, a dashboard link, and two charts.
Synthetic data only. All figures come from workspace.r5_drybuild2 gold tables."""
import os
import pandas as pd
import streamlit as st
from databricks.sdk import WorkspaceClient

st.set_page_config(page_title="Birchwood Retail — Home", layout="wide")

WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID", "")
DASHBOARD_URL = os.environ.get(
    "DASHBOARD_URL",
    "https://dbc-be4eeba5-e3b8.cloud.databricks.com/sql/dashboardsv3/01f1d22c47d2198dbb66a7f52412e4ae",
)


@st.cache_resource
def client():
    return WorkspaceClient()


def run(sql: str) -> pd.DataFrame:
    w = client()
    r = w.statement_execution.execute_statement(statement=sql, warehouse_id=WAREHOUSE_ID, wait_timeout="30s")
    if r.status.state.value != "SUCCEEDED":
        raise RuntimeError(str(r.status.error))
    cols = [c.name for c in r.manifest.schema.columns]
    return pd.DataFrame(r.result.data_array or [], columns=cols).apply(pd.to_numeric, errors="ignore")


st.title("Birchwood Retail Group — Pilot Demo")
st.caption(
    "Synthetic sample: 24 months, 60 stores, ~400 products, ~30 promotions. "
    "All figures below are computed live from workspace.r5_drybuild2."
)

try:
    headline = run(
        "SELECT round(sum(margin),0) AS net_margin, "
        "round(sum(margin)/sum(net_sales),4) AS margin_rate "
        "FROM workspace.r5_drybuild2.gold_daily_store_category"
    )
    returns = run(
        "SELECT round(sum(returns_value),0) AS returns_value "
        "FROM workspace.r5_drybuild2.gold_margin_leakage"
    )
    net_margin = float(headline["net_margin"].iloc[0])
    margin_rate = float(headline["margin_rate"].iloc[0])
    returns_value = float(returns["returns_value"].iloc[0])

    c1, c2, c3 = st.columns(3)
    c1.metric("Net Margin", f"${net_margin:,.0f}")
    c2.metric("Margin Rate (fixed definition)", f"{margin_rate:.2%}")
    c3.metric("Returns Value", f"${returns_value:,.0f}")
    st.caption(
        "Net margin = sales after discounts, less returns, less cost of goods sold. "
        "Margin rate = net margin ÷ sales after returns."
    )
except Exception as e:
    st.error(f"Could not load headline figures: {e}")

st.markdown(f"[Open the full Executive dashboard →]({DASHBOARD_URL})")

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Where does profit come from?")
    try:
        df = run(
            "SELECT category, round(sum(margin),0) AS net_margin "
            "FROM workspace.r5_drybuild2.gold_daily_store_category "
            "GROUP BY category ORDER BY net_margin DESC"
        )
        st.bar_chart(df.set_index("category"))
    except Exception as e:
        st.error(f"Query failed: {e}")

with col_b:
    st.subheader("Which promotions lose money even though they sold more?")
    try:
        df = run(
            "SELECT promo_name, round(margin_change_per_day,0) AS margin_change_per_day "
            "FROM workspace.r5_drybuild2.gold_promo_effectiveness "
            "WHERE verdict = 'margin dilutive' "
            "ORDER BY margin_change_per_day ASC LIMIT 10"
        )
        st.bar_chart(df.set_index("promo_name"))
        st.caption("ESTIMATE — margin per day vs. the 28 days before the promotion started.")
    except Exception as e:
        st.error(f"Query failed: {e}")
