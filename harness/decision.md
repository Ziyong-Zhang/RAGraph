> POLICY: This file is an append-only log reserved STRICTLY for MAJOR architectural decisions (e.g., tech stack changes, database schema design, LLM chunking strategies, system boundaries). Minor implementation details, bug fixes, and routine refactoring belong in Git commits.

## Decision Log

### 1. Adopt Harness Engineering Pattern

- **Date:** 2026-03-07
- **Context:** Need a reliable way to manage Agent context and maintain architectural boundaries across all future coding sessions.
- **Decision:** Adopt Harness Engineering pattern (`project.md`, `process.md`, `progress.md`, `decision.md`). Enforce strict Streamlit/FastAPI decoupling with REST-only communication between frontend and backend.