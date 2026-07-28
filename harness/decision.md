> POLICY: This file is an append-only log reserved STRICTLY for MAJOR architectural decisions (e.g., tech stack changes, database schema design, LLM chunking strategies, system boundaries). Minor implementation details, bug fixes, and routine refactoring belong in Git commits.

## Decision Log

### 1. Adopt Harness Engineering Pattern

- **Date:** 2026-03-07
- **Context:** Need a reliable way to manage Agent context and maintain architectural boundaries across all future coding sessions.
- **Decision:** Adopt Harness Engineering pattern (`project.md`, `process.md`, `progress.md`, `decision.md`). Enforce strict Streamlit/FastAPI decoupling with REST-only communication between frontend and backend.

### 2. Graph Merging Logic (Rolling State)

- **Date:** 2026-07-12
- **Context:** When processing EPUB text in overlapping chunks, the LLM may re-discover characters already seen in previous chunks, leading to duplicate nodes in the final graph.
- **Decision:** Use a `GraphState` Pydantic model (`known_characters: list[Character]`, `known_relationships: list[Relationship]`) as a rolling memory basket. Each LLM call receives the current state and is instructed to merge aliases rather than creating duplicates. This prevents entity proliferation across chunks without requiring a separate database or vector index.

### 3. Instructor for Structured LLM Output

- **Date:** 2026-07-12
- **Context:** Raw LLM responses are unstructured and prone to missing fields or schema violations, making downstream processing (e.g., NetworkX graph construction) fragile.
- **Decision:** Use `instructor` patched on the DeepSeek `AsyncOpenAI` client with `mode=instructor.Mode.JSON`. This enforces strict Pydantic model validation on the LLM output, guaranteeing that every response conforms to the `GraphState` schema before any downstream logic executes.

### 4. MultiDiGraph with Weight Accumulation

- **Date:** 2026-07-12
- **Context:** Relationships between characters can be mentioned multiple times across different chapters with the same nature (e.g., "friend"). A simple undirected graph or DiGraph loses this frequency information.
- **Decision:** Use `networkx.MultiDiGraph` to allow multiple edges between the same two nodes. Edges sharing the same (source, target, nature) tuple are collapsed with an accumulated `weight` attribute. This preserves relationship multiplicity for downstream analytics (e.g., link strength in visualizations).

### 5. Dual-Configuration Pattern (YAML + .env)

- **Date:** 2026-07-12
- **Context:** Mixing runtime secrets (API keys) and pipeline hyperparameters (chunk size, limits) in a single `.env` file limits reproducibility and version control.
- **Decision:** Implement a dual-configuration architecture. Use `.env` exclusively for secrets (excluded from Git). Use a version-controlled `config.yaml` for pipeline hyperparameters, parsed via a Pydantic `PipelineConfig` model.

### 6. Frontend Graph Rendering via Cytoscape JSON

- **Date:** 2026-07-12
- **Context:** While GraphML is standard for offline analysis (e.g., Gephi), it is not natively suited for interactive web visualization in a Streamlit/FastAPI architecture.
- **Decision:** Decouple graph construction from visualization by implementing an exporter that converts the NetworkX `MultiDiGraph` into strict Cytoscape.js JSON format. FastAPI serves this JSON, and Streamlit renders it using `st.components.v1.html`, ensuring a lightweight, interactive frontend.

### 7. Explicit Environment Variable Sync for Observability

- **Date:** 2026-07-12
- **Context:** `pydantic-settings` loads configurations into memory, but LangChain/LangSmith SDKs strictly read from `os.environ` during initialization, causing tracing to silently fail.
- **Decision:** Explicitly synchronize LangSmith variables from the Pydantic settings object back into `os.environ` at the application entry points (`run_integration.py` and `main.py`) before importing any LangChain modules.

### 8. Anti-Spoiler Graph RAG Chat Engine

- **Date:** 2026-07-18
- **Context:** Users need a stateful chat interface that answers questions about the story based on knowledge extracted up to a specific chapter. Answers must not reveal future events or characters not yet discovered.
- **Decision:** Implement a stateless POST endpoint `/api/v1/chat`. The request includes `book_stem`, `chapter_index`, and `messages`. The backend reads the corresponding `{book_stem}_chapter_{chapter_index}.json`, stringifies it, and injects it into the system prompt. The LLM is rigidly instructed to reject answering any question whose premise cannot be found in the injected JSON snapshot, thus preventing spoilers.

### 9. Native Streamlit HITL Editor vs. Iframe JS

- **Date:** 2026-07-28
- **Context:** Phase 5 requires enabling users to manually merge duplicate character nodes and delete hallucinated edges. The Cytoscape graph renders inside an isolated `<iframe>` via `st.components.v1.html`, making it nearly impossible to embed interactive HTML edit buttons that reliably communicate back to the Streamlit Python runtime.
- **Decision:** Build the graph editor using native Streamlit widgets (expander, tabs, selectboxes, buttons) positioned below the graph visualization. This ensures reliable state synchronization via `st.rerun()`, strictly decouples the visualization container from mutation logic, and avoids complex cross-origin message passing. Backend endpoints directly modify the JSON files on disk, and the frontend re-fetches after each mutation.
