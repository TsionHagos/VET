import streamlit as st
from google import genai
from src.state import init_session_state
from components import translator, voice_vet, visual_vet, compare, dashboard, history, about

st.set_page_config(
    page_title = "VET | Very Easy Tech",
    layout = "wide"
)
init_session_state()
api_key = st.secrets["GEMINI_API_KEY"]
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key = api_key)
pages = [
    st.Page(translator.render, title = "Translator", url_path = "translator", default = True),
    st.Page(voice_vet.render, title = "Voice VET", url_path = "voice-vet"),
    st.Page(visual_vet.render, title = "Visual VET", url_path = "visual-vet"),
    st.Page(compare.render, title = "Compare", url_path = "compare"),
    st.Page(dashboard.render, title = "Dashboard", url_path = "dashboard"),
    st.Page(history.render, title = "History", url_path = "history"),
    st.Page(about.render, title = "About VET", url_path = "about")
]
st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    order: 2;
}
[data-testid="stSidebarUserContent"] {
    order: 1;
}
section[data-testid="stSidebar"] > div {
    display: flex;
    flex-direction: column;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("VET")
st.sidebar.subheader("Very Easy Tech")
nav = st.navigation(pages)
nav.run()