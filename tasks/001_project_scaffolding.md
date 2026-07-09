# Task 001: Project Scaffolding and Environment Initialization

## Objective
Complete Phase 1 by initializing the Python environment using `uv`, creating the decoupled directory structure, and establishing the testing baseline.

## Steps to Execute
1. Run `uv init` in the root directory to create `pyproject.toml` and `.python-version`. Delete the default `hello.py` if it is generated.
2. Run `uv add fastapi uvicorn pydantic python-dotenv streamlit`.
3. Run `uv add --dev pytest pytest-asyncio`.
4. Create the core directory structure:
   - `backend/`
   - `backend/core/`
   - `frontend/`
   - `tests/`
   - `data/raw/` (for storing EPUB files locally)
5. Create empty `__init__.py` files in `backend/`, `backend/core/`, and `tests/`.
6. Create or update `.gitignore`. It MUST explicitly ignore:
   - `.env`
   - `__pycache__/`
   - `.pytest_cache/`
   - `.venv/`
   - `.ruff_cache/`
   - `*.epub`
   - `data/`
7. Create `.env.example` with placeholders: `DEEPSEEK_API_KEY=your_key_here`.
8. Apply TDD: Create `tests/test_architecture.py`. Write a dummy test `test_directories_exist()` that asserts the existence of the `backend` and `frontend` directories using `pathlib.Path`.
9. Run `uv run pytest tests/test_architecture.py`.
10. If the test passes, update `harness/process.md` to check off the remaining tasks in Phase 1.
11. Update `harness/progress.md`:
    - Status: "Phase 1 completed. Task 001 executed successfully."
    - Next Action: "Phase 2 - Backend Foundation (FastAPI and LangSmith setup)."

## Constraints
- ALL code, docstrings, inline comments, and commit messages MUST BE EXCLUSIVELY IN ENGLISH.
- NEVER use Chinese characters in any generated files.
- Ensure strict separation of backend and frontend.