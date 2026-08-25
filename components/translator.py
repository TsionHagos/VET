import streamlit as st
from src.gemini_service import explain_concept
from components.ui import render_settings_sidebar

def render():
    st.title("Translator")
    st.write("Complex Technology. Very easy explanations.")
    difficulty, analogy_style, final_audience, parent_mode = render_settings_sidebar()
    term = st.text_input(
        "What technology concept do you want to understand?",
        placeholder = "Example: API, firewall, database..."
    )
    if st.button("Explain with VET"):
        if not term.strip():
            st.warning("Please enter a technology concept first.")
        else:
            with st.spinner("VET is simplifying the concept..."):
                result = explain_concept(
                    client = st.session_state.client,
                    term = term,
                    difficulty = difficulty,
                    analogy_style = analogy_style,
                    audience = final_audience
                )
            st.session_state.current_result = result
            st.markdown("### VET Explanation")
            st.write(result["audience_explanation"])
            st.session_state.history.append({
                "term": term,
                "difficulty": difficulty,
                "analogy_style": analogy_style,
                "audience": final_audience,
                "parent_mode": parent_mode,
                "vet_score": result.get("vet_score")
            })
            st.session_state.total_explanations += 1
            if result.get("vet_score") is not None:
                score = result["vet_score"]
                st.markdown("### VET SCORE")
                st.progress(score/100)
                st.markdown(f"**{score} / 100 - {result['rating_label']}**")
            with st.expander("See full breakdown"):
                st.write(f"**Definition:** {result['simple_definition']}")
                st.write(f"**Analogy:** {result['everyday_analogy']}")
                st.write(f"**Why it matters:** {result['why_it_matters']}")
                st.write(f"**Technical explanation**: {result['technical_explanation']}")
                st.write(f"**Key takeaway**: {result['key_takeaway']}")
                st.write(f"**Related concepts:** {', '.join(result['related_concepts'])}")