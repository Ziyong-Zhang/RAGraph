# Task 010: Refactor Integration Flow and Observability

## Objective
Enhance the integration test pipeline for production robustness: implement dynamic output naming, centralize configurations in YAML, and fully activate LangSmith observability.

## Steps to Execute
1. Update `config.yaml`:
   - Add `books_dir: "data/raw/books"`
   - Add `output_dir: "data/raw/output"`
2. Update `backend/core/extractor.py`:
   - Import `traceable` from `langsmith`.
   - Add `@traceable(run_type="llm", name="DeepSeek_Entity_Extraction")` to the `extract_entities` function.
3. Update `scripts/run_integration.py`:
   - Refactor to read `books_dir` and `output_dir` from `get_pipeline_config()`.
   - Implement dynamic output naming:
     - Use `Path(epub_path).stem` to get the filename without extension.
     - Set `output_path` to `{output_dir}/{filename}_graph.graphml`.
   - Remove all hardcoded paths from the main logic flow.
4. Verify LangSmith Setup:
   - Ensure the `.env` uses the standard keys: `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_ENDPOINT`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`.
5. Run the integration test:
   - Create the directory structure `data/raw/books/` and move your test EPUBs there.
   - Run `uv run python scripts/run_integration.py --epub-path data/raw/books/test_book.epub`.
6. Update `harness/progress.md`:
   - Status: "Phase 3 fully complete. Observability and dynamic pipeline orchestration ready."

## Constraints
- ALL code, docstrings, inline comments, and commit messages MUST BE EXCLUSIVELY IN ENGLISH.
- NEVER use Chinese characters in any generated files.
- The logic must ensure that `data/raw/output` directory is created if it doesn't exist.