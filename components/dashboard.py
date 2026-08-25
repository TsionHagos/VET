import streamlit as st
import pandas as pd

def render():
    st.title("VET Dashboard")

    history_df = pd.DataFrame(st.session_state.history)

    if history_df.empty:
        st.info("Explain a concept to see your dashboard.")
        return

    total_concepts = history_df["term"].nunique()
    parent_count = history_df["parent_mode"].sum()
    parent_pct = round((parent_count / len(history_df)) * 100)
    avg_score = history_df["vet_score"].dropna().mean()
    avg_score_value = round(avg_score) if pd.notna(avg_score) else None

    if "dashboard_snapshot" not in st.session_state:
        st.session_state.dashboard_snapshot = {
            "total_concepts": total_concepts,
            "avg_score": avg_score_value,
            "parent_pct": parent_pct
        }

    snapshot = st.session_state.dashboard_snapshot
    concepts_delta = total_concepts - snapshot["total_concepts"]
    score_delta = (
        avg_score_value - snapshot["avg_score"]
        if avg_score_value is not None and snapshot["avg_score"] is not None
        else None
    )
    parent_delta = parent_pct - snapshot["parent_pct"]

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Concepts",
        total_concepts,
        delta=concepts_delta if concepts_delta != 0 else None
    )
    col2.metric(
        "VET Score",
        f"{avg_score_value}%" if avg_score_value is not None else "N/A",
        delta=f"{score_delta}%" if score_delta not in (None, 0) else None
    )
    col3.metric(
        "Parent Mode",
        f"{parent_pct}%",
        delta=f"{parent_delta}%" if parent_delta != 0 else None
    )

    st.session_state.dashboard_snapshot = {
        "total_concepts": total_concepts,
        "avg_score": avg_score_value,
        "parent_pct": parent_pct
    }

    st.subheader("Concepts Explained")
    concept_counts = history_df["term"].value_counts()
    st.bar_chart(concept_counts)