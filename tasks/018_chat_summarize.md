> Context: We have accomplished several major architectural milestones today. We need to consolidate these updates into our project documentation to maintain alignment before moving to the Human-In-The-Loop (HITL) and Deployment phases.

> STRICT RULES:
> 1. ALL documentation updates MUST be exclusively in English.
> 2. Do not modify any python source code during this task.

Please execute the following tasks:

### Task 1: Update `harness/project.md`
Open `harness/project.md`. Add a new section titled `## Core Architectural Patterns Introduced`. Briefly summarize the following patterns we implemented:
1. **Chapter-Level Incremental Snapshotting:** Using a "Continuous Overwrite" pattern to save Cytoscape JSONs per chapter, achieving O(1) time-travel for the timeline UI without database bloat.
2. **Deterministic Entity Resolution (ER):** A Python-based fallback defense mechanism that normalizes strings and strictly merges characters based on overlapping aliases, preventing duplicate nodes despite LLM hallucinations.
3. **State-Aware Graph RAG & Context Isolation:** The backend chat endpoint is strictly stateless. The frontend strictly manages `st.session_state` chat history and deliberately wipes it when the user alters the `chapter_index` timeline, ensuring the LLM is perfectly grounded in the anti-spoiler snapshot context.
4. **Defensive UI Rendering:** Utilizing UUIDs for edge IDs, JS Object literal injection (to bypass escaping errors), and bounded physics parameters (`nodeRepulsion`) to prevent WebGL silent crashes in Cytoscape.js.

### Task 2: Update `README_RUN.md`
Open `README_RUN.md`. Under the frontend usage section:
- Mention the newly added "Chapter Timeline Slider" in the sidebar.
- Mention the "Anti-Spoiler Detective Assistant" chat interface at the bottom of the app. Explain that it automatically synchronizes its knowledge context based on the timeline slider.
- Add a small note suggesting users manually clear `data/raw/output/` if they encounter corrupted legacy JSON formats from previous extractions.

### Task 3: Update `harness/process.md`
Open `harness/process.md`.
Update "Phase 4: Frontend and Visualization":
- Mark `[x] Implement "anti-spoiler" chat state management.`
- Fix the wording: Change `[x] Build "anti-spoiler" chat interface with correction UI.` to `[x] Build "anti-spoiler" chat interface.` (We haven't built the correction UI yet).
- Update the remaining unchecked item to: `[ ] Build Human-in-the-Loop (HITL) interactive correction UI inside the graph info panel.`

Create a new Phase or update the remaining items:
**Phase 5: Human-In-The-Loop (HITL) Correction**
- [ ] Implement backend REST endpoints for node merging and edge deletion.
- [ ] Implement graph state reloading and JSON overwrite logic upon manual correction.
- [ ] Connect Streamlit UI buttons to correction endpoints.

**Phase 6: GCP Infrastructure and Deployment**
- [ ] Write Dockerfile for multi-stage container build.
- [ ] Write Terraform configuration for GCP Cloud Run deployment.
- [ ] Configure GitHub Actions workflow for CI/CD.
- [ ] Set up GCP service accounts and secrets management.

Ensure the documents look clean, professional, and well-formatted.