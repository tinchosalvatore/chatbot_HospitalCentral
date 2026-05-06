# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run app
streamlit run app.py

# Test API + PDF connectivity (no browser)
python test_backend.py
```

## Architecture

Single-file Streamlit app (`app.py`). No routing, no modules — everything in one script.

**Data flow:**
1. At startup, `manual_medico.pdf` is uploaded to the Gemini Files API via `upload_and_cache_pdf()`, which is decorated with `@st.cache_resource` — upload only happens once per server process, not on every Streamlit rerender.
2. A `GenerativeModel` is created with a hardcoded system prompt (Spanish, persona "Lupe", Hospital Central Mendoza — lupus specialist).
3. A `chat_session` is initialized in `st.session_state` with the PDF file injected as the first two history entries (user sends PDF + "Estudia este documento.", model replies "Entendido.").
4. The UI renders `history[2:]` — skipping those two bootstrap messages so users only see actual conversation.

**Key constraints:**
- Model: `models/gemini-flash-latest`, `temperature=0.2` (low for medical accuracy), `max_output_tokens=8192`.
- Emergency detection is handled in the system prompt, not in Python code.
- The assistant must never reference "the document" or "the PDF" — it presents knowledge as its own.
- "Nueva Consulta" button deletes `chat_session` from session state and reruns, which triggers a new chat session (but reuses the cached PDF upload).

## Required files at runtime

| File | Purpose |
|------|---------|
| `.env` | `GEMINI_API_KEY=...` |
| `manual_medico.pdf` | Knowledge base uploaded to Gemini |
| `logo_HC.png` | Sidebar logo |

## Security note

`.env` must never be committed. It is listed in `.gitignore` but verify it is not tracked: `git ls-files .env`. The API key in `.env` grants Gemini API access and should be rotated if ever exposed.
