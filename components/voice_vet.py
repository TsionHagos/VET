import streamlit as st
from src.gemini_service import transcribe_and_explain
from components.ui import render_settings_sidebar

def render():
    st.title("Voice VET")
    st.write("Ask VET anything - just record your question.")

    difficulty, analogy_style, final_audience, parent_mode = render_settings_sidebar()

    audio_value = st.audio_input("Record your question")

    if audio_value is not None:
        if st.button("Explain this question"):
            with st.spinner("VET is listening and simplifying..."):
                audio_bytes = audio_value.getvalue()
                transcribed_term, result = transcribe_and_explain(
                    client=st.session_state.client,
                    audio_bytes=audio_bytes,
                    mime_type=audio_value.type,
                    difficulty=difficulty,
                    analogy_style=analogy_style,
                    audience=final_audience
                )

            st.session_state.current_result = result
            st.markdown(f"**You asked:** {transcribed_term}")

            st.markdown("### VET Explanation")
            st.write(result["audience_explanation"])

            st.session_state.history.append({
                "term": transcribed_term,
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
                st.progress(score / 100)
                st.markdown(f"**{score} / 100 - {result['rating_label']}**")

            with st.expander("See full breakdown"):
                st.write(f"**Definition:** {result['simple_definition']}")
                st.write(f"**Analogy:** {result['everyday_analogy']}")
                st.write(f"**Why it matters:** {result['why_it_matters']}")
                st.write(f"**Technical explanation:** {result['technical_explanation']}")
                st.write(f"**Key takeaway:** {result['key_takeaway']}")
                st.write(f"**Related concepts:** {', '.join(result['related_concepts'])}")