# RAGraph — Process Roadmap

## Phase 0: Repository Setup and IDE Agent Integration

- [x] Create GitHub repository with initial README.
- [x] Configure IDE (VS Code) with Agentic coding assistant.
- [x] Establish Git remote and initial commit.

## Phase 1: Establish Harness Engineering Context and Project Scaffolding

- [x] Create `harness/project.md`, `harness/process.md`, `harness/progress.md`, `harness/decision.md`.
- [x] Create `.clinerules` with strict operational mandates.
- [x] Initialize `uv` package manager and `pyproject.toml`.
- [x] Create `tests/` directory for TDD.
- [x] Set up project directory structure (`backend/`, `frontend/`, `backend/core/`, `data/raw/`).
- [x] Add production dependencies (fastapi, uvicorn, pydantic, python-dotenv, streamlit).
- [x] Add dev dependencies (pytest, pytest-asyncio).
- [x] Create `.gitignore` and `.env.example`.
- [x] Create `tests/test_architecture.py` (TDD) — passes.

## Phase 2: Backend Foundation

- [x] Implement FastAPI application skeleton with health check endpoint.
- [x] Write Pytest test suite for health check endpoint.
- [x] Integrate LangSmith for observability and tracing.
- [x] Configure environment variable management (`.env`, `settings.py`).

## Phase 3: Agentic Core

- [x] Implement EPUB parsing module (text extraction, chapter splitting).
- [x] Define LangGraph state graph for character extraction workflow.
- [x] Integrate DeepSeek API for LLM-based character extraction.
- [x] Implement NetworkX graph construction from extracted relationships.
- [x] Build timeline extraction and ordering logic (handled implicitly by graph state ordering across chunks).

## Phase 4: Frontend and Visualization

- [x] Build Streamlit app with EPUB upload and processing UI.
- [x] Implement character relationship graph visualization (NetworkX + Streamlit).
- [x] Implement timeline visualization.
- [x] Implement "anti-spoiler" chat state management.
- [x] Build "anti-spoiler" chat interface.
- [ ] Build Human-in-the-Loop (HITL) interactive correction UI inside the graph info panel.
- [x] Connect Streamlit frontend to FastAPI backend via REST.

## Phase 5: Human-In-The-Loop (HITL) Correction

- [ ] Implement backend REST endpoints for node merging and edge deletion.
- [ ] Implement graph state reloading and JSON overwrite logic upon manual correction.
- [ ] Connect Streamlit UI buttons to correction endpoints.

## Phase 6: GCP Infrastructure and Deployment

- [ ] Write Dockerfile for multi-stage container build.
- [ ] Write Terraform configuration for GCP Cloud Run deployment.
- [ ] Configure GitHub Actions workflow for CI/CD.
- [ ] Set up GCP service accounts and secrets management.
- [ ] Deploy production and staging environments.