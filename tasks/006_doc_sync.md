# Task 006: Milestone Sync and Architectural Documentation Update

## Objective
Pause feature development to document the system architecture, toolchain purpose, and major decisions up to the completion of the NetworkX integration.

## Steps to Execute
1. Update `harness/project.md`:
   - Add a new section titled `## Architecture & Toolchain Map`.
   - Write a clear summary explaining the role of each tool used so far (FastAPI, Pydantic Settings, ebooklib/BeautifulSoup, LangChain TextSplitters, Instructor, DeepSeek API, NetworkX).
   - Create a `mermaid` markdown block detailing the data flow: EPUB -> Text -> Chunks -> LLM (with Rolling State) -> JSON Schema -> NetworkX GraphML.
2. Update `harness/decision.md`:
   - Add a log entry for `Graph Merging Logic`: Explain why we use `GraphState` to maintain a rolling memory of characters to prevent duplicate nodes.
   - Add a log entry for `Instructor for LLM`: Explain why we use `instructor` to enforce JSON schema instead of raw LLM prompting.
   - Add a log entry for `MultiDiGraph`: Explain why we chose a multi-directional graph with weights over a simple undirected graph.
3. Update `harness/progress.md`:
   - Status: "Phase 3 partial completion. Milestone architectural sync completed."
   - Next Action: "Implement LangGraph state graph for orchestrating the chunk-by-chunk processing pipeline."

## Constraints
- ALL documentation updates MUST BE EXCLUSIVELY IN ENGLISH.
- Ensure the Mermaid diagram syntax is correct and renders properly in markdown.