import streamlit as st

def render():
    st.title("About VET")
    st.write(
        "VET (Very Easy Tech) is an educational tool that explains "
        "computer science and IT concepts in plain, jargon-free language "
        "using everyday analogies tailored to your audience."
    )

    st.subheader("Features")
    st.markdown(
        "- **Translator** - explain any tech concept in text\n"
        "- **Voice VET** - ask a question by recording audio\n"
        "- **Visual VET** - analyze diagrams, slides, or code screenshots\n"
        "- **Compare** - see two concepts side-by-side\n"
        "- **VET Score** - a 0-100 rating of how easy each explanation is to understand\n"
        "- **Parent Mode** - tailors explanations for a non-technical parent"
    )