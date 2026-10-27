"""Ask the Genie: natural-language questions over the retail gold tables, powered by the
Birchwood Retail Genie space (validated in genie/GENIE_VALIDATION.md)."""
import os
import time
import pandas as pd
import streamlit as st
from databricks.sdk import WorkspaceClient

st.set_page_config(page_title="Ask the Genie", layout="wide")

GENIE_SPACE_ID = os.environ.get("GENIE_SPACE_ID", "01f1d22ebf4217ca9ca00cabefb2a93f")

PREFILLED = [
    "Which categories earn our margin, and how is each trending?",
    "Where are stock-outs costing us the most (estimated)?",
    "How many loyalty customers are still buying 1, 3, 6 and 12 months after their first purchase?",
    "Which promotions lost us money, even though they sold more?",
    "How fresh and complete is the data behind these numbers?",
]


@st.cache_resource
def client():
    return WorkspaceClient()


def ask_genie(question: str, timeout_s: int = 60):
    w = client()
    start = w.api_client.do(
        "POST", f"/api/2.0/genie/spaces/{GENIE_SPACE_ID}/start-conversation",
        body={"content": question},
    )
    conv_id = start["conversation_id"]
    msg_id = start["message_id"]
    waited = 0
    while waited < timeout_s:
        msg = w.api_client.do(
            "GET",
            f"/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conv_id}/messages/{msg_id}",
        )
        status = msg.get("status")
        if status in ("COMPLETED", "FAILED", "CANCELLED"):
            return msg, conv_id, msg_id
        time.sleep(2)
        waited += 2
    raise TimeoutError("Genie did not respond in time")


def fetch_query_result(conv_id: str, msg_id: str, attachment_id: str) -> pd.DataFrame:
    w = client()
    resp = w.api_client.do(
        "GET",
        f"/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conv_id}/messages/{msg_id}"
        f"/attachments/{attachment_id}/query-result",
    )
    sr = resp["statement_response"]
    cols = [c["name"] for c in sr["manifest"]["schema"]["columns"]]
    rows = sr["result"].get("data_array", [])
    return pd.DataFrame(rows, columns=cols).apply(pd.to_numeric, errors="ignore")


def render_answer(msg: dict, conv_id: str, msg_id: str):
    if msg.get("status") != "COMPLETED":
        st.error(f"Genie status: {msg.get('status')} — {msg.get('error', {})}")
        return
    attachments = msg.get("attachments", [])
    text_parts = [a["text"]["content"] for a in attachments if "text" in a]
    for t in text_parts:
        st.markdown(t)
    query_attachments = [a for a in attachments if "query" in a]
    for qa in query_attachments:
        try:
            df = fetch_query_result(conv_id, msg_id, qa["attachment_id"])
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load the result table: {e}")
        with st.expander("Show the generated SQL"):
            st.code(qa["query"]["query"], language="sql")
    if not text_parts and not query_attachments:
        st.warning("Genie returned no text or query attachment for this question.")


st.title("Ask the Genie")
st.caption(
    "Natural-language questions over margin, promotions, stock-outs, loyalty and data trust. "
    "Synthetic data only."
)

st.subheader("Pick a question")
picked = st.selectbox("Choose a tested question", PREFILLED, key="genie_picklist")
if st.button("Ask Genie", type="primary"):
    st.session_state["genie_question"] = picked

st.subheader("Or type your own")
typed = st.text_input("Your question", key="genie_typed")
if st.button("Ask", type="primary"):
    if typed:
        st.session_state["genie_question"] = typed

question = st.session_state.get("genie_question")
if question:
    st.markdown(f"**Asking:** {question}")
    try:
        with st.spinner("Genie is thinking..."):
            msg, conv_id, msg_id = ask_genie(question)
        render_answer(msg, conv_id, msg_id)
    except Exception as e:
        st.error(f"Genie call failed: {e}")
