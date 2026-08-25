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
    avg_score_display = f"{round(avg_score)}%" if pd.notna(avg_score) else "N/A"

    col1, col2, col3 = st.columns(3)
    col1.metric("Concepts", total_concepts)
    col2.metric("VET Score", avg_score_display)
    col3.metric("Parent Mode", f"{parent_pct}%")

    st.subheader("Concepts Explained")
    concept_counts = history_df["term"].value_counts()
    st.bar_chart(concept_counts)