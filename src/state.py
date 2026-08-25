import streamlit as st

def init_session_state():
    defaults = {
        "history": [],
        "current_result": None,
        "total_explanations": 0,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default