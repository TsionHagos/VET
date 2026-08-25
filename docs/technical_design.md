# VET (Very Easy Tech) — Technical Design

## 1. Data Flow

### 1.1 Text Explanation Flow (Translator)
User enters term + selects difficulty/analogy style/audience
↓
render_settings_sidebar() reads widget state from st.session_state
↓
translator.py calls gemini_service.explain_concept(client, term, difficulty, analogy_style, audience)
↓
build_explanation_prompt() (src/prompts.py) interpolates inputs into a fixed-schema JSON instruction
↓
Gemini API call (gemini-2.5-flash) with SYSTEM_PROMPT + built prompt
↓
Response text is stripped of markdown fences, parsed via json.loads()
↓
Result dict returned to translator.py
↓
UI renders: audience_explanation → VET Score → expander (definition, analogy, why it matters, technical explanation, key takeaway, related concepts)
↓
Result appended to st.session_state.history; current_result updated; total_explanations incremented

### 1.2 Voice Flow (Voice VET)

Same as above, with one extra step at the front:
st.audio_input() captures audio bytes
↓
transcribe_and_explain() sends raw audio (inline_data) to Gemini with a
transcription-only instruction, extracts the transcribed text
↓
Delegates to explain_concept() using the transcribed text as term
↓
(rest of flow identical to 1.1)

Two Gemini calls occur per Voice VET interaction: one to transcribe,
one to explain.

### 1.3 Image Flow (Visual VET)
st.file_uploader() or st.camera_input() captures image bytes
↓
analyze_image() sends the image (inline_data) directly to Gemini
alongside a combined "identify + explain" instruction
↓
Single Gemini call returns both identified_subject and the full
explanation schema in one response
↓
(rest of flow identical to 1.1, with identified_subject shown first)

Unlike Voice VET, Visual VET uses a single Gemini call — identification
and explanation happen together since Gemini's vision capability can
reason about the image directly, without a separate transcription step.

### 1.4 Compare Flow
Two terms entered (Concept A, Concept B)
↓
compare_concepts() builds a single prompt covering both concepts
↓
Gemini returns: a row-by-row comparison table (purpose, analogy,
used_for, vet_version), two standalone concept summaries, a key
difference explanation, and a how-they-relate note
↓
UI renders: comparison table → side-by-side summaries → key
difference → how they relate → VET Score
↓
No dedicated history entry structure exists yet for compare
results (see Section 4, Known Gaps)

## 2. API Integration Strategy

### 2.1 Client Initialization

A single `genai.Client` is created once in `app.py` and stored in
`st.session_state.client`, guarded by an existence check so it
survives Streamlit reruns without re-authenticating on every
interaction:

```python
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=api_key)
```

The API key is read from `st.secrets["GEMINI_API_KEY"]`, sourced
from `.streamlit/secrets.toml`, which is gitignored.

### 2.2 Model Selection

All calls use `gemini-2.5-flash` — chosen for multimodal support
(text, audio, image in a single API surface) and lower latency
than larger model variants, at the cost of occasional JSON
formatting inconsistency (addressed in 2.3).

### 2.3 Structured Output via Prompt-Enforced JSON

Gemini's response is not requested via a strict schema/function-calling
API — instead, the prompt itself instructs the model to return JSON
only, with the exact key structure spelled out inline. This was a
deliberate simplicity trade-off:

**Pros:** works uniformly across text, image, and multi-input
prompts without needing per-call schema configuration.

**Cons:** occasional non-conforming output (extra prose, markdown
fences) requires defensive parsing.

Mitigations:
- Strip leading/trailing triple-backtick fences before parsing
- Wrap `json.loads()` in try/except, falling back to a schema-shaped
  dict with `"N/A"` placeholders and the raw text preserved in the
  explanation field, so downstream code never encounters a missing key

### 2.4 Error Handling Strategy

Two failure classes are handled explicitly at the API-call layer,
inside every function in `gemini_service.py`:

| Error Type | Cause | Handling |
|---|---|---|
| `genai_errors.ClientError` (HTTP 429) | Rate limit / daily quota exceeded | Return fallback dict with a quota-specific user-facing message |
| `genai_errors.ServerError` (HTTP 503) | Gemini temporarily overloaded | Return fallback dict with a temporary-unavailability message |
| `json.JSONDecodeError` | Malformed JSON in an otherwise successful response | Return fallback dict with raw text preserved |

In all three cases, the function returns rather than raises — the
caller (a `components/*.py` page) never needs its own try/except,
since it always receives a dict shaped like a successful response.

### 2.5 Audience/Parent Mode Injection

`audience` is not a raw passthrough of the user's dropdown
selection. `render_settings_sidebar()` computes a `final_audience`
value that overrides the dropdown with an expanded description when
Parent Mode is toggled on:

```python
final_audience = (
    "A non-technical parent who may have little or no understanding of computers."
    if parent_mode
    else audience
)
```

This value is what actually reaches every Gemini call — ensuring
consistent audience framing regardless of which page or input mode
is used.

## 3. Logic Modules

| Module | Responsibility |
|---|---|
| `app.py` | App entry point: page config, session state init, client init, navigation registration |
| `src/state.py` | Defines and initializes all `st.session_state` keys used across the app |
| `src/prompts.py` | Owns `SYSTEM_PROMPT` (VET's persona/rules) and `build_explanation_prompt()` (text-mode prompt construction) |
| `src/gemini_service.py` | All Gemini API calls, response parsing, and error handling. Four public functions: `explain_concept`, `transcribe_and_explain`, `analyze_image`, `compare_concepts` |
| `components/ui.py` | Single shared sidebar control for difficulty, analogy style, audience, and Parent Mode — used by every input-mode page so settings stay consistent and state persists across navigation |
| `components/translator.py` | Text input page: renders form, calls `explain_concept`, renders result |
| `components/voice_vet.py` | Audio input page: renders recorder, calls `transcribe_and_explain`, renders result |
| `components/visual_vet.py` | Image input page: renders uploader/camera input, calls `analyze_image`, renders result |
| `components/compare.py` | Two-concept comparison page: renders dual inputs, calls `compare_concepts`, renders table + summaries |
| `components/dashboard.py` | Aggregates `st.session_state.history` into a Pandas DataFrame; renders metric cards and a bar chart |
| `components/history.py` | Renders the full history log as an editable table |
| `components/about.py` | Static informational content; no API calls |

### Design Principle: Shared Settings, Independent Pages

Each input-mode page (`translator.py`, `voice_vet.py`,
`visual_vet.py`, `compare.py`) is self-contained — it can be
tested and reasoned about independently — but all four read
identical settings from `render_settings_sidebar()`. This avoids
duplicating widget definitions across pages while still letting
each page own its specific input-handling and result-rendering
logic.

### Design Principle: Uniform Response Shape

Regardless of input mode or failure mode, every Gemini-calling
function returns a dict containing the same core keys
(`audience_explanation`, `vet_score`, `rating_label`, etc., with
`identified_subject` added for images and a different shape for
comparisons). This lets every page's rendering code assume the
keys exist, rather than checking for `None` or missing keys at
every UI call site.

## 4. Known Gaps / Future Work

- **Compare Mode history entries** are not yet structured
  consistently with the other three modes — `compare.py` does not
  currently append to `st.session_state.history` in the same
  shape as Translator/Voice/Visual, so comparisons may not appear
  correctly in Dashboard/History views.
- **`src/analytics.py`** is currently an empty placeholder;
  dashboard aggregation logic currently lives directly in
  `components/dashboard.py` rather than being separated into its
  own analytics module.
- **No automatic retry** on transient 503 errors — the fallback
  message asks the user to retry manually rather than the app
  retrying automatically after a short delay.
- **No persistent storage** — see `architecture.md` Known
  Limitations; all state is in-memory only.