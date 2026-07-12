# Task 007: LangGraph Orchestration and Pipeline Assembly

## Objective
Conclude Phase 3 by orchestrating the entire RAGraph extraction pipeline using `langgraph`. We will assemble the EPUB parser, the chunker, the LLM extractor (with rolling state), and the NetworkX graph builder into a fault-tolerant, sequential state machine graph.

## Steps to Execute
1. Run `uv add langgraph`.
2. Create `backend/core/workflow.py`:
   - Import necessary components: `EpubParser`, `chunk_text`, `extract_entities`, `build_networkx_graph`, `save_graph` and our models.
   - Import `StateGraph`, `END` from `langgraph.graph`.
   - Define a TypedDict state: `class PipelineState(TypedDict):`
     - `filepath: str`
     - `text_chunks: list[str]`
     - `current_chunk_index: int`
     - `graph_memory: GraphState`
     - `output_graph_path: str`
     - `api_key: str`
   - Define Node 1: `initialize_document(state: PipelineState)`. Uses parser and chunker. Populates `text_chunks`, initializes empty `graph_memory`, sets `current_chunk_index = 0`.
   - Define Node 2: `process_single_chunk(state: PipelineState)`. Async node. Takes the chunk at `current_chunk_index`, calls `extract_entities(chunk, graph_memory, api_key)`. Updates `graph_memory` and increments `current_chunk_index`.
   - Define Node 3: `finalize_graph(state: PipelineState)`. Calls `build_networkx_graph`, saves to `output_graph_path`.
   - Define Edge Logic: `def check_next_chunk(state: PipelineState) -> str:`. Returns `"process_single_chunk"` if `current_chunk_index < len(text_chunks)`, else returns `"finalize_graph"`.
   - Compile the graph: Build the `StateGraph(PipelineState)`, add nodes, add edges, set entry point to `initialize_document`, compile into `ragraph_app`.
3. Apply TDD: Create `tests/test_workflow.py`.
   - Since testing the full pipeline involves multiple heavy mocks, write a simplified test.
   - Mock `initialize_document` to return 2 dummy chunks. Mock `extract_entities` to return a dummy state.
   - Pass an initial state to the compiled graph and assert that it correctly loops twice and then reaches `finalize_graph`.
4. Run the tests: `uv run pytest tests/test_workflow.py -v`.
5. If the tests pass, update `harness/process.md` to check off "Define LangGraph state graph for character extraction workflow" and the "Timeline logic" item (mark it as deferred/handled implicitly by graph state for now).
6. Update `harness/progress.md`:
   - Status: "Phase 3 almost complete. LangGraph sequential orchestration pipeline assembled."
   - Next Action: "Finalize Phase 3 with a full integration manual test before moving to Streamlit Frontend."

## Constraints
- ALL code, docstrings, inline comments, and commit messages MUST BE EXCLUSIVELY IN ENGLISH.
- NEVER use Chinese characters in any generated files.
- The pipeline MUST be purely sequential to ensure the Rolling State (Graph Merging) remains perfectly consistent.