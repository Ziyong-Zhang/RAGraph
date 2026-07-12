# RAGraph — Current Progress

## Current Status

Phase 3 ongoing. LLM structured extraction and Graph Merging Logic implemented via instructor.

## Completed

- Added `openai` and `instructor` dependencies.
- Created `backend/core/extractor.py` with async `extract_entities()` function:
  - Patches `AsyncOpenAI` with instructor targeting DeepSeek base URL (`api.deepseek.com/v1`).
  - Uses `instructor.Mode.JSON` for strictly typed JSON outputs via `response_model=GraphState`.
  - Includes a highly specific system prompt directing the model to merge entities from `current_state` rather than creating duplicates.
  - API key is received as a parameter (no hardcoded keys).
- Applied TDD: created `tests/test_extractor.py` with `test_extract_entities_mock` patching instructor's client to return a hardcoded `GraphState`.
- All 6 tests pass across all phases.

## Next Action

Implement NetworkX graph construction and timeline logic.
