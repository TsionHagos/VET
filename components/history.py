import streamlit as st
import pandas as pd

def render():
    st.title("History")

    history_df = pd.DataFrame(st.session_state.history)

    if history_df.empty:
        st.info("No history yet. Explain a concept to get started.")
        return

    st.data_editor(history_df, use_container_width=True)