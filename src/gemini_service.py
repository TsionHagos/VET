from google import genai
from google.genai import errors as genai_errors
from src.prompts import (
    SYSTEM_PROMPT,
    build_explanation_prompt
)
import json

def create_client(api_key):
    return genai.Client(api_key = api_key)

def _unavailable_message():
    return "VET couldn't reach Gemini right now - the service is experiencing high demand. Please try again in a moment."

def _quota_message():
    return "VET has hit its daily usage limit for now. Please try again later, or check the API plan's rate limits."

def explain_concept(
        client,
        term,
        difficulty,
        analogy_style,
        audience
):
    prompt = build_explanation_prompt(
        term = term,
        difficulty = difficulty,
        analogy_style = analogy_style,
        audience = audience
    )

    try:
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = [
                SYSTEM_PROMPT,
                prompt
            ]
        )
    except genai_errors.ClientError as e:
        message = _quota_message() if e.code == 429 else _unavailable_message()
        return {
            "simple_definition": "N/A",
            "everyday_analogy": "N/A",
            "audience_explanation": message,
            "why_it_matters": "N/A",
            "technical_explanation": "N/A",
            "key_takeaway": "N/A",
            "related_concepts": [],
            "vet_score": None,
            "rating_label": "N/A",
            "factors": {}
        }
    except genai_errors.ServerError:
        return {
            "simple_definition": "N/A",
            "everyday_analogy": "N/A",
            "audience_explanation": _unavailable_message(),
            "why_it_matters": "N/A",
            "technical_explanation": "N/A",
            "key_takeaway": "N/A",
            "related_concepts": [],
            "vet_score": None,
            "rating_label": "N/A",
            "factors": {}
        }

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()
    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {
            "simple_definition": "N/A",
            "everyday_analogy": "N/A",
            "audience_explanation": raw_text,
            "why_it_matters": "N/A",
            "technical_explanation": "N/A",
            "key_takeaway": "N/A",
            "related_concepts": [],
            "vet_score": None,
            "rating_label": "N/A",
            "factors": {}
        }
    return result

def transcribe_and_explain(client, audio_bytes, mime_type, difficulty, analogy_style, audience):
    try:
        transcription_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                "Transcribe the question asked in this audio clip. "
                "Respond with ONLY the transcribed question text, nothing else.",
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": audio_bytes
                    }
                }
            ]
        )
    except genai_errors.ServerError:
        return "N/A", {
            "simple_definition": "N/A",
            "everyday_analogy": "N/A",
            "audience_explanation": _unavailable_message(),
            "why_it_matters": "N/A",
            "technical_explanation": "N/A",
            "key_takeaway": "N/A",
            "related_concepts": [],
            "vet_score": None,
            "rating_label": "N/A",
            "factors": {}
        }

    term = transcription_response.text.strip()

    result = explain_concept(
        client=client,
        term=term,
        difficulty=difficulty,
        analogy_style=analogy_style,
        audience=audience
    )

    return term, result

def analyze_image(client, image_bytes, mime_type, difficulty, analogy_style, audience):
    prompt = f"""
You are VET - Very Easy Tech.
Look at the attached image. It may be a technical diagram, a lecture slide, a networking diagram, or a code screenshot.
Identify what the image shows, then explain it as VET would.
DIFFICULTY LEVEL:
{difficulty}
ANALOGY STYLE:
{analogy_style}
TARGET AUDIENCE:
{audience}
Generate a JSON object with exactly this structure:
{{
"identified_subject": "a short label for what the image shows, e.g. 'Network topology diagram'",
"simple_definition": "...",
"everyday_analogy": "...",
"audience_explanation": "...",
"why_it_matters": "...",
"technical_explanation": "...",
"key_takeaway": "...",
"related_concepts": ["...", "..."],
"vet_score": 92,
"rating_label": "VERY EASY",
"factors": {{
"jargon_density": 90,
"sentence_complexity": 88,
"explanation_length": 95,
"analogy_quality": 93,
"audience_readability": 94
}}
}}
Requirements:
- Base everything strictly on what is visible in the image. Do not invent details you cannot see.
- If the image is unclear or not a technical image, say so in "identified_subject" and explain as best you can.
- "audience_explanation" must be fully self-contained: introduce and explain the analogy within this field itself, as if the reader has not seen "everyday_analogy" separately.
- Respond ONLY with valid JSON, no markdown formatting, no backticks.
"""
    try:
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = [
                prompt,
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_bytes
                    }
                }
            ]
        )
    except genai_errors.ClientError as e:
        message = _quota_message() if e.code == 429 else _unavailable_message()
        return {
            "simple_definition": "N/A",
            "everyday_analogy": "N/A",
            "audience_explanation": message,
            "why_it_matters": "N/A",
            "technical_explanation": "N/A",
            "key_takeaway": "N/A",
            "related_concepts": [],
            "vet_score": None,
            "rating_label": "N/A",
            "factors": {}
        }
    except genai_errors.ServerError:
        return {
            "identified_subject": "Unavailable",
            "simple_definition": "N/A",
            "everyday_analogy": "N/A",
            "audience_explanation": _unavailable_message(),
            "why_it_matters": "N/A",
            "technical_explanation": "N/A",
            "key_takeaway": "N/A",
            "related_concepts": [],
            "vet_score": None,
            "rating_label": "N/A",
            "factors": {}
        }

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()
    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {
            "identified_subject": "Unknown",
            "simple_definition": "N/A",
            "everyday_analogy": "N/A",
            "audience_explanation": raw_text,
            "why_it_matters": "N/A",
            "technical_explanation": "N/A",
            "key_takeaway": "N/A",
            "related_concepts": [],
            "vet_score": None,
            "rating_label": "N/A",
            "factors": {}
        }
    return result

def compare_concepts(client, term_a, term_b, difficulty, analogy_style, audience):
    prompt = f"""
You are VET - Very Easy Tech.
Compare these two computer science / IT concepts for a non-technical audience:
CONCEPT A: {term_a}
CONCEPT B: {term_b}
DIFFICULTY LEVEL:
{difficulty}
ANALOGY STYLE:
{analogy_style}
TARGET AUDIENCE: 
{audience}
Generate a JSON object with exactly this structure:
{{
"concept_a": "{term_a}",
"concept_b": "{term_b}",
"comparison": {{
"purpose": {{"a": "...", "b": "..."}},
"analogy": {{"a": "...", "b": "..."}},
"used_for": {{"a": "...", "b": "..."}},
"vet_version": {{"a": "...", "b": "..."}}
}},
"concept_a_summary": "2-3 sentence explanation of {term_a} written for the TARGET AUDIENCE, using the ANALOGY STYLE",
"concept_b_summary": "2-3 sentence explanation of {term_b} written for the TARGET AUDIENCE, using the ANALOGY STYLE",
"key_difference": "2-3 sentences explaining the core difference between them and why that difference matters in practice, not just a one-line label",
"how_they_relate": "1-2 sentences on how these two concepts often work together or interact in real systems, if applicable - otherwise state they are generally used independently",
"vet_score": 92,
"rating_label": "VERY EASY",
"factors": {{
"jargon_density": 90,
"sentence_complexity": 88,
"explanation_length": 95,
"analogy_quality": 93,
"audience_readability": 94
}}
}}
Requirements:
- Table rows (purpose, analogy, used_for, vet_version) should stay short phrases (2-5 words) for quick scanning.
- "concept_a_summary" and "concept_b_summary" must be fully self-contained explanations a reader could understand without seeing the table.
- The analogies for A and B should come from the same {analogy_style} style so they feel like a matched pair.
- "vet_version" should be a simple, everyday nickname for each concept's role (e.g. "Messenger", "Storage room").
- "key_difference" should go beyond a single label - explain the practical implication of the difference.
- Respond ONLY with valid JSON, no markdown formatting, no backticks.
"""
    try:
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = [prompt]
        )
    except genai_errors.ClientError as e:
        message = _quota_message() if e.code == 429 else _unavailable_message()
        return {
            "simple_definition": "N/A",
            "everyday_analogy": "N/A",
            "audience_explanation": message,
            "why_it_matters": "N/A",
            "technical_explanation": "N/A",
            "key_takeaway": "N/A",
            "related_concepts": [],
            "vet_score": None,
            "rating_label": "N/A",
            "factors": {}
        }
    except genai_errors.ServerError:
        return {
            "concept_a": term_a,
            "concept_b": term_b,
            "comparison": {},
            "concept_a_summary": "N/A",
            "concept_b_summary": "N/A",
            "key_difference": _unavailable_message(),
            "how_they_relate": "N/A",
            "vet_score": None,
            "rating_label": "N/A",
            "factors": {}
        }

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()
    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {
            "concept_a": term_a,
            "concept_b": term_b,
            "comparison": {},
            "concept_a_summary": "N/A",
            "concept_b_summary": "N/A",
            "key_difference": raw_text,
            "how_they_relate": "N/A",
            "vet_score": None,
            "rating_label": "N/A",
            "factors": {}
        }
    return result