# Contributing

## Repository layout

| Package / file | Responsibility |
|----------------|------------------|
| `app.py` | Streamlit page config, session state, chat rendering, orchestration of sidebar + AI calls. |
| `config/` | `settings` singleton: environment variables, model name, tokens, logging level. |
| `core/ai_engine.py` | Gemini SDK usage only: configure client, `stream_response` / `get_response`, API error handling, optional timing. **Do not embed domain facts here.** |
| `core/prompt_builder.py` | Persona text, guard rails, and conversion of in-app chat history to Gemini `role` / `parts` format. Update scope rules here if the assistant’s *behaviour* changes. |
| `knowledge/` | **Authoritative place for domain content** users should see reflected in answers: policies, processes, disclaimers, FAQ-style strings. |
| `ui/` | Streamlit presentation: headers, sidebar, bubbles, feedback controls, CSS. |
| `utils/` | Cross-cutting helpers (e.g. Loguru setup). |

## Adding or changing DVLA (or other) knowledge **without** touching `ai_engine.py`

1. **Edit or extend** [`knowledge/dvla_knowledge.py`](knowledge/dvla_knowledge.py)  
   - Put long-form reference text in methods such as `get_system_context()`, `get_quick_topics()`, or `get_disclaimer()`.  
   - Add new helper methods (for example `get_fees_reference()`) if you need structured sections, and call them from `get_system_context()` so the model still receives one consolidated context string.

2. **Keep the model contract stable**  
   - `AIEngine` pulls `DVLAKnowledgeBase().get_system_context()` and passes it into `PromptBuilder.build_system_prompt(...)`.  
   - As long as `get_system_context()` (or whatever `AIEngine` is wired to) returns a string, you do **not** need to change `ai_engine.py`.

3. **Adjust persona / scope wording** in [`core/prompt_builder.py`](core/prompt_builder.py)  
   - Use this when you need stricter or looser *instructions* (tone, refusals, language policy), not for pasting large tables of fees (those belong in `knowledge/`).

4. **Surface new UI affordances** (optional) in [`ui/components.py`](ui/components.py) and call new knowledge helpers from [`app.py`](app.py) if you add buttons or sidebar sections that need fresh copy.

5. **Tests and docs**  
   - If you add a second domain (e.g. another authority), prefer a **new module** under `knowledge/` (e.g. `knowledge/other_agency.py`) and compose its text inside `PromptBuilder` or a thin factory—still avoid growing `ai_engine.py` with non-API logic.

## When you *do* need `core/ai_engine.py`

- Changing model id, generation parameters, streaming behaviour, or error mapping for the Gemini API.
- Adding non-domain middleware that must wrap every model call (for example a universal request logger).

## Style

- Match existing typing, imports, and Loguru usage.  
- Keep secrets and environment-specific values in `.env`, not in code.  
- Do not commit `.env`.
