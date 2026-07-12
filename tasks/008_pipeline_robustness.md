# Task 008: YAML Configuration Decoupling, Pipeline Robustness, and Integration Test

## Objective
Refactor the architecture to use a dual-configuration pattern: secrets in `.env` and hyperparameters in a `config.yaml` file. Decouple hardcoded values (chunk size, overlap, circuit breakers), add standard Python logging to the LangGraph pipeline, and formalize an integration test script.

## Steps to Execute
1. Run `uv add pyyaml`.
2. Create `config.yaml` at the project root:
   - Define a `pipeline` section with the following keys:
     - `chunk_size: 2000`
     - `chunk_overlap: 200`
     - `max_chunks_limit: 4` (Comment this as: "Set to null for unlimited production runs")
3. Update `backend/core/config.py`:
   - Keep the existing `Settings` class (which reads `.env` for `DEEPSEEK_API_KEY`).
   - Import `yaml` and `BaseModel` from Pydantic.
   - Define a `PipelineConfig` Pydantic model matching the YAML structure.
   - Write a function `get_pipeline_config() -> PipelineConfig` that reads `config.yaml`, parses it, and returns the Pydantic object. Cache it using `@lru_cache` from `functools`.
4. Update `backend/core/chunker.py`:
   - Import `get_pipeline_config`.
   - Remove the hardcoded default values in `chunk_text` function signature. Instead, fetch `chunk_size` and `chunk_overlap` dynamically from the pipeline config inside the function.
5. Update `backend/core/workflow.py`:
   - Import Python's built-in `logging`. Configure a basic logger at the `INFO` level.
   - Update `PipelineState` TypedDict: Add `max_chunks: int | None`.
   - Add `logging.info` statements inside `initialize_document`, `process_single_chunk`, and `finalize_graph` to report progress.
   - Update `check_next_chunk` routing logic: 
     - If `state.get("max_chunks")` is not None AND `state["current_chunk_index"] >= state["max_chunks"]`, return `"finalize_graph"`.
     - Otherwise, if `state["current_chunk_index"] < len(state["text_chunks"])`, return `"process_single_chunk"`.
     - Else, return `"finalize_graph"`.
6. Create Integration Script `scripts/run_integration.py`:
   - Import `asyncio`, `os`, `logging`, `ragraph_app`.
   - Import `get_settings` and `get_pipeline_config`.
   - Write an async `main()` function:
     - Validate API key from settings.
     - Read the circuit breaker limit from `get_pipeline_config().max_chunks_limit`.
     - Read from a test EPUB path (`src/agatha_novels`) and select one novel, log a warning if missing.
     - Initialize `PipelineState` and invoke `ragraph_app`.
     - Log success and the GraphML output path.
7. Apply TDD: Update/fix `tests/test_workflow.py` and `tests/test_parsers.py` (chunker tests) to mock or handle the new config system properly.
8. Run the Pytest suite: `uv run pytest tests/ -v`.
9. Update `harness/progress.md`:
   - Status: "Phase 3 fully completed. Architecture upgraded with YAML hyperparameters, logging, circuit breakers, and integration testing."
   - Next Action: "Phase 4 - FastAPI Routing and Streamlit Frontend initialization."

## Constraints
- ALL code, docstrings, inline comments, and commit messages MUST BE EXCLUSIVELY IN ENGLISH.
- NEVER use Chinese characters in any generated files.
- Ensure the circuit breaker is evaluated safely using `state.get("max_chunks")` to avoid KeyError in existing tests.