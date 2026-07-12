# RAGraph — Current Progress

## Current Status

Documentation fully synced with Phase 4 architecture. Ready to proceed with Anti-spoiler Chat.

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
- Enhanced Cytoscape layout with `cose` algorithm parameters: `idealEdgeLength: 100`, `nodeRepulsion: 400000`, `componentSpacing: 100`, `edgeElasticity: 100` for reduced node overlap.
- Added floating `#info-panel` with interactive event listeners: tap node shows aliases/description, tap edge shows source/target/nature/weight, tap background hides panel. Gracefully handles missing attributes with italic "(none)" placeholder.
- Created `README_RUN.md` with two-terminal run instructions.
- Updated `tests/test_api.py` with `test_graphs_list_empty` (mocked nonexistent output dir).
- All 12 tests pass across all phases.

## Next Action

Implement LLM Chat interaction UI and state management.
