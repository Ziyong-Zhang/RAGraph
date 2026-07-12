# Task 005: Advanced NetworkX Graph Construction and Persistence

## Objective
Continue Phase 3 by transforming the structured Pydantic `GraphState` into a mathematical `networkx` graph. Implement high-level optimizations including multi-directional edges, edge weight accumulation, and graph serialization to local files for zero-cost reloading.

## Steps to Execute
1. Run `uv add networkx`.
2. Create `backend/core/graph_builder.py`:
   - Import `networkx as nx` and `os`.
   - Import `GraphState` from `backend.core.models`.
   - Implement `build_networkx_graph(state: GraphState) -> nx.MultiDiGraph:`
     - Initialize `G = nx.MultiDiGraph()`.
     - Add nodes: Iterate through `state.known_characters`, add them using `G.add_node`, storing `aliases` (join as string if needed by GraphML) and `description`.
     - Add edges with weighting: Iterate through `state.known_relationships`. Check if an edge between `source` and `target` with the exact `nature` already exists. If it does, increment its `weight` attribute by 1. If not, create it with `weight=1`.
     - Return `G`.
   - Implement `save_graph(G: nx.MultiDiGraph, filepath: str)`: Ensure the directory exists, then use `nx.write_graphml(G, filepath)`.
   - Implement `load_graph(filepath: str) -> nx.MultiDiGraph`: Use `nx.read_graphml(filepath)` and return the graph.
3. Apply TDD: Create `tests/test_graph_builder.py`.
   - Test `build_networkx_graph`: Mock a `GraphState` with duplicate relationships between the same source and target to assert that the edge `weight` becomes 2.
   - Test `save_graph` and `load_graph`: Build a simple graph, save it to a temporary directory (`tmp_path` fixture), load it back, and assert the nodes and edges match.
4. Run the tests: `uv run pytest tests/test_graph_builder.py -v`.
5. If tests pass, update `harness/process.md` to check off "Implement NetworkX graph construction...".
6. Update `harness/progress.md`:
   - Status: "Phase 3 ongoing. Advanced NetworkX MultiDiGraph logic and persistence implemented."
   - Next Action: "Perform Milestone Sync (Task 006) to update architectural documentation."

## Constraints
- ALL code, docstrings, inline comments, and commit messages MUST BE EXCLUSIVELY IN ENGLISH.
- NEVER use Chinese characters in any generated files.
- `GraphML` format may struggle with Python lists. Convert the `aliases` list to a comma-separated string before storing it as a node attribute.