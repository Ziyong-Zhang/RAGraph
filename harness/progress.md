# RAGraph — Current Progress

## Current Status

Chapter-level timeline and dynamic graph snapshotting implemented. Ready for Anti-spoiler Chat UI.

## Completed

- Added `openai` and `instructor` dependencies.
- Created `backend/core/extractor.py` with async `extract_entities()` function.
- Added `networkx` dependency.
- Created `backend/core/graph_builder.py` with MultiDiGraph construction, weight accumulation, GraphML persistence.
- Added `langgraph` dependency.
- Created `backend/core/workflow.py` with sequential StateGraph pipeline.
- Updated `harness/project.md` with Architecture & Toolchain Map section.
- Updated `harness/decision.md` with three new log entries.
- Added `pyyaml` dependency and created `config.yaml` at project root with pipeline hyperparameters.
- Updated `backend/core/config.py` with `PipelineConfig` and `get_pipeline_config()`.
- Updated `backend/core/chunker.py` to read chunk_size/chunk_overlap from config.
- Added logging, `max_chunks` circuit breaker to `backend/core/workflow.py`.
- Created `scripts/run_integration.py` with early settings init, dynamic output naming, Cytoscape JSON export.
- Created `backend/core/exporter.py` with `export_to_cytoscape_json()`.
- Updated `.env.example` with LangSmith standard keys.
- Added CORS middleware and `GET /api/v1/graph/{book_stem}` endpoint to `backend/main.py`.
- Added `GET /api/v1/graphs` endpoint listing available book stems from processed JSON files.
- Created `frontend/app.py` — Streamlit UI with sidebar book stem input, Cytoscape.js rendering via `st.components.v1.html`.
- Refactored `frontend/app.py`: dynamic `st.selectbox` populated from `/api/v1/graphs` endpoint (falls back to text_input if empty).
- Enhanced Cytoscape layout with `cose` algorithm parameters.
- Added floating `#info-panel` with interactive event listeners.
- Created `README_RUN.md` with two-terminal run instructions.
- Updated `tests/test_api.py` with `test_graphs_list_empty`.
- **Chapter-Level Timeline Implementation:**
  - Updated `backend/core/parsers.py`: Added `extract_chapter_texts()` method returning plain text per EPUB document item (chapter).
  - Updated `backend/core/chunker.py`: Added `chunk_chapter_texts()` returning `list[tuple[str, int]]` — each chunk tagged with its source chapter index (1-based).
  - Updated `backend/core/workflow.py`: Changed `PipelineState` to use `chapter_chunks` (list of text+chapter tuples) and `output_base_path`. Implemented Continuous Chapter Overwrite — each chunk snapshot saves `{base}_chapter_{N}.json`. Finalize saves both GraphML and `{base}_final.json`.
  - Updated `scripts/run_integration.py`: Uses new `PipelineState` fields (`chapter_chunks`, `output_base_path`).
  - Added `GET /api/v1/graph/{book_stem}/metadata` endpoint — scans output dir for `{book_stem}_chapter_*.json` files, returns `{book_stem, available_chapters, max_chapter}`.
  - Updated `GET /api/v1/graph/{book_stem}` with optional `?chapter_index=N` query param — loads chapter-specific snapshot or falls back to `_final.json`.
  - Updated `GET /api/v1/graphs` to filter out `_chapter_X` and `_final` suffixed files from the selection dropdown.
  - Updated `frontend/app.py`: Fetches chapter metadata on book selection. Renders `st.select_slider` in the sidebar for chapter timeline. Appends `?chapter_index=N` to graph fetch URL.
- Applied TDD: created `tests/test_timeline.py` with 5 tests: metadata endpoint (with and without chapters), chapter-indexed graph fetch, invalid chapter 404, graphs list exclusion of chapter suffixes.
- All 17 tests pass across all phases.

- **Anti-Spoiler Chat Frontend:**
  - Initialized `st.session_state.messages`, `current_book`, and `current_chapter` tracking variables.
  - Context switching logic: when book or chapter changes, chat history is cleared and tracking variables updated — prevents leaking future context during time-travel.
  - Rendered `st.divider()` + `st.subheader("Detective Assistant")` below the graph visualization.
  - Iterates over `st.session_state.messages` with `st.chat_message()` bubbles.
  - `st.chat_input("Ask a question about the current case...")` captures user prompts.
  - On submission: appends user message, shows loading spinner, sends `POST /api/v1/chat` with `{book_stem, chapter_index, messages}` payload, appends and renders assistant response.
  - Error handling: `try...except requests.exceptions.RequestException` catches connection failures and displays `st.error()` — app remains responsive.
  - No LLM logic in frontend; purely a view layer delegating to FastAPI.

- **LLM Prompt Hardening (Relationship Ontology):** Updated `backend/core/extractor.py` system prompt with 4 strict relationship extraction rules to reduce edge clutter:
  - Rule 1 (State over Action): `nature` MUST describe structural/social/emotional status, NOT ephemeral events.
  - Rule 2 (Forbidden Verbs): Strictly forbids "-ing" verb forms (e.g., "conversing", "observing") in the `nature` field.
  - Rule 3 (Inference): LLM must use interactions as evidence to deduce the true relationship (e.g., "intimate conversation" → "Secret Lovers").
  - Rule 4 (Conciseness): `nature` limited to 2-4 words; detailed context moved to character `description`.

## Next Action

Docker containerization and GCP Cloud Run deployment.
