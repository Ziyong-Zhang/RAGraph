# Task Specification: Chapter-Level Timeline & Dynamic Graph Snapshotting

## 1. Objective
Implement an interactive, chapter-level story timeline (time-travel) feature. The application will allow users to drag a slider on the Streamlit frontend to view the character relationship graph exactly as it was at the end of any selected chapter. This will be achieved using **Continuous Chapter Overwrite** snapshotting on the backend to avoid database overhead or storage bloat, establishing a solid data boundary for the upcoming "anti-spoiler" chat.

---

## 2. Steps to Execute

### Phase 1: Backend Data Model & Chunker Update
- [ ] **1.1 Update Chunk Models:** Ensure the Text Chunk or Graph State model contains metadata tracking the source chapter:
  - Add `chapter_index: int` (1-based index) to the text chunk processing pipeline.
  - Ensure the parser (`parsers.py` or `chunker.py`) correctly extracts and attaches the current chapter index to each generated text chunk.

### Phase 2: LangGraph Workflow Snapshot Logic
- [ ] **2.1 Implement Continuous Chapter Overwrite:** Update the node execution logic in `backend/core/workflow.py` (or the runner script):
  - In each iteration processing a chunk $C$ with `chapter_index = N`, update the global `GraphState`.
  - Immediately construct the updated NetworkX `MultiDiGraph` from the current `GraphState`.
  - Call the exporter to save/overwrite the current graph directly as `data/raw/output/{book_stem}_chapter_{N}.json`.
  - *Note:* Do not write complex "on-chapter-change" triggers. Simply overwrite the current chapter's JSON file. Once the pipeline moves to chapter $N+1$, the file for chapter $N$ naturally remains frozen in its complete, final state.
- [ ] **2.2 Export Final Baseline:** Ensure `{book_stem}_final.json` is still successfully written at the very end of the workflow execution.

### Phase 3: FastAPI REST API Enhancements
- [ ] **3.1 Create Metadata Endpoint:** Add `GET /api/v1/graph/{book_stem}/metadata` in `backend/main.py`:
  - It should scan `data/raw/output/` for files matching `{book_stem}_chapter_*.json`.
  - Extract the unique chapter numbers, sort them, and return a payload structure:
    ```json
    {
      "book_stem": "string",
      "available_chapters": [1, 2, 3, 4],
      "max_chapter": 4
    }
    ```
- [ ] **3.2 Enhance Graph Snapshot Endpoint:** Update `GET /api/v1/graph/{book_stem}` in `backend/main.py`:
  - Add an optional query parameter `chapter_index: int = None`.
  - If `chapter_index` is provided, load and return `{book_stem}_chapter_{chapter_index}.json`.
  - If `chapter_index` is `None` (or out of bounds), fall back to loading the final graph `{book_stem}_final.json`.
  - Return HTTP 404 with a clean message if the specified chapter file does not exist.
- [ ] **3.3 Update Collection Endpoint:** Ensure `GET /api/v1/graphs` only returns base `book_stem`s, filtering out any `_chapter_X` suffix files to keep the main selection dropdown clean.

### Phase 4: Streamlit Frontend Timeline Integration
- [ ] **4.1 Fetch Book Metadata:** In `frontend/app.py`, when a book is selected, fetch its chapter metadata from `GET /api/v1/graph/{book_stem}/metadata`.
- [ ] **4.2 Render Interactive Select-Slider:** - If chapters exist, render an `st.select_slider` (or `st.slider`) in the sidebar with the options mapped to `available_chapters`.
  - Set the default slider value to the maximum available chapter (the latest processed chapter).
- [ ] **4.3 Update REST Graph Call:** - Append the selected slider value as a query parameter (e.g., `?chapter_index={selected_chapter}`) when calling the graph fetching endpoint.
  - Trigger a seamless Cytoscape.js visual redraw when the user drags the slider.

### Phase 5: Automated Test Coverage (TDD)
- [ ] **5.1 Write API Unit Tests:** Create or update `tests/test_api.py` (or add `tests/test_timeline.py`):
  - Mock the output folder's file listing to simulate files like `mock_book_chapter_1.json` and `mock_book_chapter_2.json`.
  - Test `/api/v1/graph/mock_book/metadata` returns correct chapter indices.
  - Test `/api/v1/graph/mock_book?chapter_index=1` returns the expected chapter-1 data structure.
  - Test `/api/v1/graph/mock_book?chapter_index=99` returns a proper HTTP 404 error.
- [ ] **5.2 Verify Pipeline Output:** Run `uv run python scripts/run_integration.py` with mock data and verify chapter files populate successfully.

---

## 3. Constraints

1. **Strict Decoupling:** Under no circumstances should the backend import Streamlit modules or run visualization libraries. Frontend-backend communication must remain purely RESTful.
2. **Exclusively English Codebase:** All code comments, logging statements, docstrings, and Git commit messages generated during this implementation must be strictly in English. No Chinese characters in code.
3. **Continuous Chapter Overwrite Pattern Only:** Do not implement complex in-memory chapter boundary detection or caching state machine. Rely entirely on file overwrites mapped to the current chunk's metadata chapter index.
4. **Graceful Failures:** If a requested chapter file is missing, return a clean JSON error representation with an appropriate HTTP status code (e.g. 404), rather than throwing an unhandled exception in FastAPI.
5. **UI Responsiveness:** Ensure that Streamlit does not unnecessarily double-fetch data or trigger infinite loops when the slider values change. Utilize `st.cache_data` where appropriate.
