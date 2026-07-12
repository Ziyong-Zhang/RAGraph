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
