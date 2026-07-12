# Task 012: UI/UX Refinement for Graph Visualization

## Objective
Enhance the user experience of the Phase 4 Streamlit app by implementing a dynamic book selection dropdown, tuning the force-directed graph layout to prevent node overlap, and building an interactive floating detail panel for node/edge attributes.

## Steps to Execute
1. Update FastAPI Backend (`backend/api/main.py`):
   - Add a new endpoint: `GET /api/v1/graphs`.
   - Logic: Read `output_dir` from pipeline config. Use `pathlib` to glob all `*_graph.json` files in the directory. Extract and return the stems (e.g., `["test_book", "agatha_book"]`). Return `[]` if the directory doesn't exist or is empty.
2. Update Streamlit Frontend (`frontend/app.py`):
   - Fetch the list of available graphs from `http://localhost:8000/api/v1/graphs`.
   - If the list is empty, display an `st.warning` prompting the user to process an EPUB first.
   - If populated, use `st.selectbox` in the sidebar to let the user select a `book_stem` instead of `st.text_input`.
3. Refactor Cytoscape HTML Template (in `frontend/app.py`):
   - **Styling:** Update the Cytoscape stylesheet. Set node `label` to `data(label)`. Set edge `label` to `data(nature)` ONLY. Add basic styling to make nodes and edges look modern (e.g., node background color, edge arrow styles).
   - **Layout:** Configure the layout to use the `cose` algorithm. Add parameters to spread nodes: `{ name: 'cose', idealEdgeLength: 100, nodeOverlap: 20, refresh: 20, fit: true, padding: 30, randomize: false, componentSpacing: 100, nodeRepulsion: 400000, edgeElasticity: 100 }`.
   - **Interactive Panel:** Inside the HTML string, add a floating `div` (e.g., `<div id="info-panel" style="position: absolute; top: 10px; right: 10px; background: rgba(255,255,255,0.9); padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 300px; display: none; font-family: sans-serif; z-index: 10;"></div>`).
   - **Event Listeners:** - Add `cy.on('tap', 'node', function(evt){ ... })`: Extract `data.label`, `data.aliases`, and `data.description`. Populate the `#info-panel` innerHTML with these details and set `display: block`.
     - Add `cy.on('tap', 'edge', function(evt){ ... })`: Extract `data.source`, `data.target`, `data.nature`, and `data.weight`. Populate the `#info-panel` and show it.
     - Add `cy.on('tap', function(evt){ if(evt.target === cy){ ... } })`: Hide the `#info-panel` when the background is clicked.
4. Update `harness/progress.md`:
   - Status: "Phase 4 UI/UX refinements complete. Dynamic selection and interactive graph layout implemented."
   - Next Action: "Implement LLM Chat interaction UI and state management."

## Constraints
- ALL code, docstrings, inline comments, and commit messages MUST BE EXCLUSIVELY IN ENGLISH.
- NEVER use Chinese characters in any generated files.
- Ensure the CSS for the floating panel uses a high `z-index` so it appears above the Cytoscape canvas.
- Ensure the `info-panel` gracefully handles missing attributes (e.g., if aliases are empty).