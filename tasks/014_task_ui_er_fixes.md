> Context: We successfully ran Task 013. However, user testing revealed two major issues:
> 1. Frontend UI Latency: The user has to click "Load Graph" to update the graph after dragging the slider. We want it to update automatically on slider drag.
> 2. Entity Resolution Failures: Duplicate character nodes (e.g., "奎雷夫人", "卡蘿琳．奎雷", and "卡拉．洛曼荃") exist in the graph because their names differ, despite their aliases overlapping. We need a deterministic Python-based Entity Resolution (ER) merge step.

> STRICT RULES:
> 1. ALL code, comments, docstrings, and commit messages MUST be strictly in English. No Chinese characters in the code.
> 2. Follow strict separation of concerns.

Please execute the following tasks:

### Task 1: Streamlit Timeline Auto-Update (app.py)
- In `frontend/app.py`, refactor the graph rendering logic.
- REMOVE the `st.button("Load Graph")` block or any forms wrapping the graph visualization.
- Wrap the FastAPI API call fetching the graph in a cached function using `@st.cache_data`. This ensures dragging the slider back and forth is instantaneous and doesn't spam the backend with duplicate requests.
- When `selected_chapter` from `st.select_slider` changes, immediately trigger the cached fetch function and re-render the Cytoscape component.

### Task 2: Backend Deterministic Entity Resolution (graph_builder.py & workflow.py)
- Create a utility function `resolve_and_merge_entities(characters: list[Character]) -> list[Character]` in a new or existing module (e.g., `backend/core/entity_resolver.py` or inside `graph_builder.py`).
- **Entity Resolution Logic:**
  - Build an equivalence graph or use a Union-Find (Disjoint Set Union) structure to group characters.
  - Two characters `C1` and `C2` belong to the same group if:
    - `C1.name.lower() == C2.name.lower()` (after stripping whitespaces/punctuation).
    - `C1.name` matches any alias in `C2.aliases` (case-insensitive, normalized).
    - `C2.name` matches any alias in `C1.aliases` (case-insensitive, normalized).
    - `C1.aliases` and `C2.aliases` share at least one common alias (intersection is not empty).
  - For each merged group:
    - Choose the **longest/most descriptive name** as the canonical `name`.
    - Consolidate all unique aliases into the new canonical character's `aliases` list (excluding the canonical name itself).
    - Merge descriptions by concatenating them with a divider (e.g., `" | "`) and removing duplicates.
- Apply this `resolve_and_merge_entities` function:
  1. In `backend/core/workflow.py` during the `GraphState` rolling memory update loop (so the LLM receives a clean, merged history in the next chunk).
  2. In `backend/core/graph_builder.py` right before constructing the NetworkX `MultiDiGraph` to guarantee final graph integrity.
- **Edge Redirection:** Ensure that when building the `MultiDiGraph`, any relationships referencing old, merged-away character names are dynamically mapped to point to the new canonical character name.

### Task 3: LLM Prompt Hardening (extractor.py)
- In `backend/core/extractor.py`, update the system prompt instructing the LLM:
  - Specifically warn about characters in Agatha Christie novels sharing identical or inherited names (e.g., mothers and daughters with the same name, like Caroline Crale and Carla Lemarchant).
  - Instruct the LLM: "Do NOT list a younger generation's name as an alias for an older generation character unless they are verified to be the exact same physical person in the story. Keep distinct generations as separate entities with precise description differences."

### Task 4: Automated Testing & Validation
- Update `tests/test_timeline.py` or create `tests/test_er.py` to test the deterministic merger:
  - Mock a list of characters with overlapping aliases (e.g., C1: name='A', aliases=['B']; C2: name='B', aliases=['C']).
  - Assert that `resolve_and_merge_entities` collapses them into 1 single character node with aliases `['A', 'B', 'C']` (excluding canonical).
- Run `uv run pytest tests/ -v` to ensure all tests pass.