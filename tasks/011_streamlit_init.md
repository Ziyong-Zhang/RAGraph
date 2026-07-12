# Task 011: API Graph Endpoint and Streamlit Visualization

## Objective
Kick off Phase 4 by extending the existing FastAPI application to serve the exported Cytoscape JSON, and initialize the Streamlit frontend to consume and render this interactive graph.

## Steps to Execute
1. Update FastAPI Backend (`backend/api/main.py`):
   - Ensure `CORSMiddleware` is configured to allow all origins (frontend is on port 8501, backend on 8000).
   - Import `get_pipeline_config` and add a new endpoint: `GET /api/v1/graph/{book_stem}`.
   - Logic for endpoint: Construct the expected JSON path `{output_dir}/{book_stem}_graph.json`. Check if it exists. If not, raise `HTTPException(status_code=404, detail="Graph data not found")`. If it exists, read the JSON file and return it.
2. Initialize Streamlit Frontend (`frontend/app.py`):
   - Set page config: `st.set_page_config(layout="wide", page_title="RAGraph")`.
   - Add a sidebar text input or select box for `book_stem` (e.g., default to the stem of your test book).
   - Use the `requests` library to fetch data from `http://localhost:8000/api/v1/graph/{book_stem}`.
   - If the response is 404, display an `st.warning("Please process the EPUB file first.")`.
   - If successful, render the graph. Use `st.components.v1.html` to embed a basic Cytoscape.js template that consumes the fetched JSON data (ensure nodes display their labels). Set the iframe height to at least 700px.
3. Apply TDD (`tests/test_api.py`):
   - Add a test for the new `/api/v1/graph/{book_stem}` endpoint. Mock the file system to return a dummy JSON for a valid book stem, and test the 404 behavior for an invalid one.
4. Add Runner Documentation:
   - Create a brief `README_RUN.md` at the project root explaining that developers must run TWO terminals:
     - Terminal 1: `uv run uvicorn backend.api.main:app --reload`
     - Terminal 2: `uv run streamlit run frontend/app.py`
5. Update `harness/progress.md` & `harness/process.md`:
   - Check off "Implement character relationship graph visualization (NetworkX + Streamlit)" and "Connect Streamlit frontend to FastAPI backend via REST" in Phase 4.
   - Status: "Phase 4 ongoing. Graph API endpoint added and Streamlit visualization active."

## Constraints
- ALL code, docstrings, inline comments, and commit messages MUST BE EXCLUSIVELY IN ENGLISH.
- NEVER use Chinese characters in any generated files.
- For the Cytoscape JS rendering in Streamlit, use a CDN link (`https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js`) in the HTML template.