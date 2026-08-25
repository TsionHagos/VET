import streamlit as st
from src.gemini_service import analyze_image
from components.ui import render_settings_sidebar

def render():
    st.title("Visual VET")
    st.write("Upload or take a picture of a technical diagram, lecture slide, networking diagram, or code screenshot.")

    difficulty, analogy_style, final_audience, parent_mode = render_settings_sidebar()

    image_source = st.radio(
        "Image source",
        ["Upload a file", "Take a picture"],
        horizontal=True
    )

    if image_source == "Upload a file":
        image_value = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp"]
        )
    else:
        image_value = st.camera_input("Take a picture")

    if image_value is not None:
        st.image(image_value, caption="Image to analyze", width=400)

        if st.button("Analyze with VET"):
            with st.spinner("VET is looking at the image..."):
                image_bytes = image_value.getvalue()
                result = analyze_image(
                    client=st.session_state.client,
                    image_bytes=image_bytes,
                    mime_type=image_value.type,
                    difficulty=difficulty,
                    analogy_style=analogy_style,
                    audience=final_audience
                )

            st.session_state.current_result = result
            st.markdown(f"**VET sees:** {result.get('identified_subject', 'N/A')}")

            st.markdown("### VET Explanation")
            st.write(result["audience_explanation"])

            st.session_state.history.append({
                "term": result.get("identified_subject", "Image"),
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