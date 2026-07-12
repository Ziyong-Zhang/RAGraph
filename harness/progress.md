# RAGraph — Current Progress

## Current Status

Phase 3 fully complete. Observability and dynamic pipeline orchestration ready.

## Completed

- Added `openai` and `instructor` dependencies.
- Created `backend/core/extractor.py` with async `extract_entities()` function.
- Added `networkx` dependency.
- Created `backend/core/graph_builder.py` with MultiDiGraph construction, weight accumulation, GraphML persistence.
- Added `langgraph` dependency.
- Created `backend/core/workflow.py` with sequential StateGraph pipeline.
- Updated `harness/project.md` with Architecture & Toolchain Map section.
- Updated `harness/decision.md` with three new log entries.
- Added `pyyaml` dependency and created `config.yaml` at project root with `pipeline.chunk_size`, `pipeline.chunk_overlap`, `pipeline.max_chunks_limit`.
- Updated `backend/core/config.py` with `PipelineConfig` Pydantic model and `get_pipeline_config()` function reading from `config.yaml`.
- Updated `backend/core/chunker.py` to dynamically read chunk_size and chunk_overlap from config.yaml at runtime.
- Updated `backend/core/workflow.py`:
  - Added Python logging (basicConfig at INFO level) with progress statements in each node.
  - Added `max_chunks: int | None` to `PipelineState` TypedDict.
  - Circuit breaker: `check_next_chunk` respects `max_chunks` limit via `state.get("max_chunks")` safe access.
- Created `scripts/run_integration.py` — validates API key, selects EPUB from `src/agatha_novels/`, reads circuit breaker from config, invokes pipeline, logs results.
- Refactored `config.yaml` to add `books_dir` and `output_dir` paths.
- Updated `backend/core/config.py` PipelineConfigModel with `books_dir` and `output_dir` fields.
- Added `@traceable(run_type="llm", name="DeepSeek_Entity_Extraction")` decorator to `extract_entities` for LangSmith observability.
- Refactored `scripts/run_integration.py`:
  - Reads `books_dir` and `output_dir` from `get_pipeline_config()` — no hardcoded paths.
  - Dynamic output naming: `{output_dir}/{input_stem}_graph.graphml`.
  - Falls back to `books_dir` when `--epub-path` is not provided.
- Updated `.env.example` with standard LangSmith keys: `LANGCHAIN_TRACING_V2`, `LANGCHAIN_ENDPOINT`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`.
- Created `backend/core/exporter.py` with `export_to_cytoscape_json(G: nx.MultiDiGraph) -> dict` — converts any MultiDiGraph into a strict Cytoscape.js compatible schema with nested `{"data": {...}}` key structure for nodes and edges.
- Updated `scripts/run_integration.py`:
  - Early settings initialization: `get_settings()` called at module level BEFORE any LangGraph/LLM imports, guaranteeing `.env` is loaded before LangSmith/LangGraph.
  - Added JSON export step: after the pipeline completes, builds the NetworkX graph from `result["graph_memory"]`, exports via `export_to_cytoscape_json`, and writes `{output_dir}/{filename_stem}_graph.json`.
- Verified `backend/core/graph_builder.py` only stores string attributes (no lists/dicts) — GraphML-safe.
- Applied TDD: created `tests/test_exporter.py` — validates nested `"data"` key pattern, node/edge attributes, and edge ID format.
- All 10 tests pass across all phases.

## Next Action

Phase 4 - FastAPI Routing for Frontend.
