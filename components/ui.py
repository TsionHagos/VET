import streamlit as st

def render_settings_sidebar():
    st.sidebar.divider()
    st.sidebar.subheader("Settings")
    difficulty = st.sidebar.selectbox(
        "Explanation level",
        ["Very Simple", "Simple", "Intermediate"],
        key = "difficulty"
    )
    analogy_style = st.sidebar.selectbox(
        "Analogy style",
        ["Everyday Life", "Food", "School", "Travel", "Home", "Work", "Sports"],
        key = "analogy_style"
    )
    parent_mode = st.sidebar.toggle("Parent Mode", key = "parent_mode")
    audience = st.sidebar.selectbox(
        "Audience",
        [
            "A non-technical parent",
            "A friend with no technical background",
            "A high-school student",
            "A beginner B.Tech student"
        ],
        disabled = parent_mode,
        key = "audience"
    )
    final_audience = (
        "A non-technical parent who may have little or no understanding of computers."
        if parent_mode
        else audience
    )
    return difficulty, analogy_style, final_audience, parent_mode