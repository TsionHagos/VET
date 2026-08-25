import streamlit as st
import pandas as pd
from src.gemini_service import compare_concepts
from components.ui import render_settings_sidebar

def render():
    st.title("Compare")
    st.write("See two concepts explained side-by-side.")

    difficulty, analogy_style, final_audience, parent_mode = render_settings_sidebar()

    col_a, col_b = st.columns(2)
    with col_a:
        term_a = st.text_input("Concept A", placeholder="Example: API", key="compare_term_a")
    with col_b:
        term_b = st.text_input("Concept B", placeholder="Example: Database", key="compare_term_b")

    if st.button("Compare with VET"):
        if not term_a.strip() or not term_b.strip():
            st.warning("Please enter both concepts to compare.")
        else:
            with st.spinner("VET is comparing the concepts..."):
                result = compare_concepts(
                    client=st.session_state.client,
                    term_a=term_a,
                    term_b=term_b,
                    difficulty=difficulty,
                    analogy_style=analogy_style,
                    audience=final_audience
                )

            comparison = result.get("comparison", {})
            rows = []
            for row_label, values in comparison.items():
                rows.append({
                    "": row_label.replace("_", " ").title(),
                    result["concept_a"]: values.get("a", ""),
                    result["concept_b"]: values.get("b", "")
                })

            if rows:
                compare_df = pd.DataFrame(rows).set_index("")
                st.table(compare_df)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {result['concept_a']}")
                st.write(result.get("concept_a_summary", ""))
            with col2:
                st.markdown(f"### {result['concept_b']}")
                st.write(result.get("concept_b_summary", ""))

            st.markdown("### Key Difference")
            st.write(result.get("key_difference", ""))

            st.markdown("### How They Relate")
            st.write(result.get("how_they_relate", ""))

            if result.get("vet_score") is not None:
                score = result["vet_score"]
                st.markdown("### VET SCORE")
                st.progress(score / 100)
                st.markdown(f"**{score} / 100 - {result['rating_label']}**")