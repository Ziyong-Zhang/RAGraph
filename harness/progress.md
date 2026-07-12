# RAGraph — Current Progress

## Current Status

Phase 3 partial completion. Milestone architectural sync completed.

## Completed

- Added `openai` and `instructor` dependencies.
- Created `backend/core/extractor.py` with async `extract_entities()` function:
  - Patches `AsyncOpenAI` with instructor targeting DeepSeek base URL (`api.deepseek.com/v1`).
  - Uses `instructor.Mode.JSON` for strictly typed JSON outputs via `response_model=GraphState`.
  - Includes a highly specific system prompt directing the model to merge entities from `current_state` rather than creating duplicates.
  - API key is received as a parameter (no hardcoded keys).
- Applied TDD: created `tests/test_extractor.py` with `test_extract_entities_mock` patching instructor's client to return a hardcoded `GraphState`.
- Added `networkx` dependency.
- Created `backend/core/graph_builder.py` with:
  - `build_networkx_graph(state) -> nx.MultiDiGraph` — converts `GraphState` into a MultiDiGraph with node attributes (aliases as comma-separated string, description) and edge weight accumulation for duplicate (source, target, nature) tuples.
  - `save_graph(G, filepath)` — serializes to GraphML with directory creation.
  - `load_graph(filepath) -> nx.MultiDiGraph` — deserializes from GraphML.
- Applied TDD: created `tests/test_graph_builder.py` — validates weight accumulation on duplicate edges and GraphML round-trip persistence.
- All 8 tests pass across all phases.
- Updated `harness/project.md` with `## Architecture & Toolchain Map` section including toolchain role summary table and Mermaid data-flow diagram.
- Updated `harness/decision.md` with three new log entries: Graph Merging Logic (Rolling State), Instructor for Structured LLM Output, MultiDiGraph with Weight Accumulation.

## Next Action

Implement LangGraph state graph for orchestrating the chunk-by-chunk processing pipeline.
