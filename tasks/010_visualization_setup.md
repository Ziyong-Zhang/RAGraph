# Task 010: Observability Debugging and Cytoscape JSON Export

## Objective
Ensure LangSmith tracing is correctly capturing LLM calls, and implement a JSON exporter that transforms the NetworkX `MultiDiGraph` into a strict Cytoscape.js compatible schema for frontend rendering.

## Steps to Execute
1. Fix Observability Initialization:
   - In `scripts/run_integration.py`, ensure that `from backend.core.config import get_settings` and `settings = get_settings()` are explicitly called BEFORE importing any LangGraph or LLM modules. This guarantees `.env` is loaded into `os.environ` early.
   - Verify `@traceable` is imported from `langsmith` and applied to `extract_entities` in `backend/core/extractor.py`.
2. Implement Cytoscape JSON Exporter:
   - Create `backend/core/exporter.py`.
   - Implement `export_to_cytoscape_json(G: nx.MultiDiGraph) -> dict`:
     - Initialize `elements = {"nodes": [], "edges": []}`.
     - Iterate through `G.nodes(data=True)`:
       - Append `{"data": {"id": node_id, "label": node_id, **node_data}}` to `elements["nodes"]`.
     - Iterate through `G.edges(data=True, keys=True)` (since it's a MultiDiGraph):
       - Append `{"data": {"source": u, "target": v, "id": f"{u}_{v}_{key}", **edge_data}}` to `elements["edges"]`.
     - Return `elements`.
   - Update `scripts/run_integration.py` to also call `export_to_cytoscape_json(result["graph_memory"])` and write the output to `{output_dir}/{filename_stem}_graph.json` using `json.dump`.
3. Harden GraphML Export (Fallback):
   - In `backend/core/graph_builder.py`, ensure `nx.write_graphml(G, filepath)` is the only logic used in `save_graph`. 
   - Double-check that no Python lists or dicts are stored as node/edge attributes (aliases should already be a joined string).
4. Apply TDD:
   - Create `tests/test_exporter.py`.
   - Build a dummy `MultiDiGraph` with 2 nodes and 1 edge (including weights and nature).
   - Assert that `export_to_cytoscape_json` returns a dictionary with keys "nodes" and "edges", and that the "data" dictionary inside nodes/edges correctly contains the provided attributes.
5. Update `harness/progress.md`:
   - Status: "Observability hardened. Cytoscape JSON export logic implemented."
   - Next Action: "Phase 4 - FastAPI Routing for Frontend."

## Constraints
- ALL code, docstrings, inline comments, and commit messages MUST BE EXCLUSIVELY IN ENGLISH.
- NEVER use Chinese characters in any generated files.
- The Cytoscape JSON MUST strictly wrap node and edge attributes inside a nested `"data"` key.