# Task 002: Backend Foundation, Configuration, and Observability

## Objective
Execute Phase 2 by setting up a strictly typed configuration management system using `pydantic-settings`, initializing the FastAPI application skeleton, and integrating LangSmith observability stubs.

## Steps to Execute
1. Run `uv add pydantic-settings langsmith`.
2. Create `backend/core/config.py`:
   - Inherit from `pydantic_settings.BaseSettings`.
   - Define strictly typed properties: `DEEPSEEK_API_KEY` (str).
   - Define optional string properties for LangSmith with default `None`: `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`.
   - Add `model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")`.
   - Instantiate a global `settings = Settings()` at the bottom.
3. Create `backend/main.py`:
   - Initialize a FastAPI application instance named `app`.
   - Create a simple GET endpoint `/health` that returns `{"status": "healthy", "service": "ragraph"}`.
4. Apply TDD: Create `tests/test_api.py`.
   - Import `TestClient` from `fastapi.testclient` and the `app` from `backend.main`.
   - Write `test_health_check()` to assert the `/health` endpoint returns a HTTP 200 status and the exact JSON payload.
5. Create `tests/test_config.py`.
   - Write a simple test to ensure the `Settings` class can be instantiated (you can mock the environment variables to prevent failing if the local `.env` is incomplete).
6. Run the tests: `uv run pytest tests/ -v`.
7. If tests pass, update `harness/process.md` to check off ALL tasks under Phase 2.
8. Update `harness/progress.md`:
   - Status: "Phase 2 completed. FastAPI skeleton, health check, and Pydantic configuration initialized."
   - Next Action: "Phase 3 - Implement EPUB parsing and text chunking logic."

## Constraints
- ALL code, docstrings, inline comments, and commit messages MUST BE EXCLUSIVELY IN ENGLISH.
- NEVER use Chinese characters in any generated files or configurations.
- Ensure strict separation of concerns; backend code must not contain any frontend/Streamlit logic.s
- Do not expose any real API keys in the codebase.