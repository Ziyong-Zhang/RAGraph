> Context: We deployed a new book ("Murder on the Orient Express") with spaces in the title. Chapters 1-4 rendered fine (only isolated nodes), but Chapter 5 resulted in a complete white screen on the Streamlit frontend. 
> Diagnosis: The white screen is caused by Cytoscape.js crashing due to duplicate edge `id`s generated during the `MultiDiGraph` JSON export. Early chapters didn't crash because they had 0 edges. Also, URL endpoints might fail if the book title contains spaces.

> STRICT RULES:
> 1. ALL code, comments, docstrings, and commit messages MUST be strictly in English.

Please execute the following robust fixes sequentially:

### Task 1: Guaranteed Unique Edge IDs (exporter.py)
- In `backend/core/exporter.py` (or wherever NetworkX graph is converted to Cytoscape JSON), replace the current edge ID generation logic (e.g., `f"{u}_{v}_{k}"`).
- Import the `uuid` module.
- For every edge appended to the cytoscape `edges` list, assign a globally unique identifier: `str(uuid.uuid4())`. This absolutely prevents Cytoscape.js from crashing due to ID collisions.

### Task 2: URL Encoding (app.py)
- In `frontend/app.py`, import `urllib.parse`.
- Whenever making a `requests.get` or `requests.post` call to the backend that includes `book_stem` in the URL path, encode it safely.
- Example: `safe_stem = urllib.parse.quote(selected_book)` -> `requests.get(f"http://localhost:8000/api/v1/graph/{safe_stem}/metadata")`.

### Task 3: Robust Frontend Error Handling (app.py)
- In `frontend/app.py`, wrap the JSON loading from `requests.get` in a `try...except` block.
- If `response.status_code != 200` or JSON parsing fails, use `st.error()` to display a clear error message instead of failing silently and causing a blank screen.

### Task 4: Relax Relationship Extraction Prompt (extractor.py)
- In `backend/core/extractor.py`, update the System Prompt.
- Add an instruction indicating that "relationships" do not strictly need to be familial or professional. If characters converse, travel together, or have observed emotional interactions (e.g., "Conversing", "Observing", "Fellow passengers"), those should also be extracted as relationships. This prevents early chapters from feeling empty.

Run `uv run pytest tests/ -v` to ensure your changes didn't break any backend API logic.