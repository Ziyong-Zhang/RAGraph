> Context: We are now implementing the "Anti-Spoiler Chat Backend". The chat must be strictly constrained by the knowledge available in the specific chapter snapshot currently viewed by the user. If the answer is not in the JSON, the LLM must elegantly state it does not know.

> STRICT RULES:
> 1. ALL code, inline comments, docstrings, and commit messages MUST be exclusively in English.
> 2. Maintain strict decoupling: FastAPI handles logic; Streamlit handles UI (do not touch Streamlit yet).
> 3. Use Test-Driven Development (TDD).

Please execute the following tasks sequentially:

**Task 1: Generate an ADR**
Create an entry in `harness/decision.md` titled "9. Anti-Spoiler Graph RAG Chat Engine". Explain that we will implement a stateless POST endpoint `/api/v1/chat`. The request includes `book_stem`, `chapter_index`, and `messages`. The backend will read the corresponding `{book_stem}_chapter_{chapter_index}.json`, stringify it, and inject it into the System Prompt. The LLM will be rigidly instructed to reject answering any question whose premise cannot be found in the injected JSON snapshot, thus preventing spoilers.

**Task 2: Define Pydantic Models**
In `backend/core/models.py`, add:
- `ChatMessage`: requires `role` (str: "user" or "assistant") and `content` (str).
- `ChatRequest`: requires `book_stem` (str), `chapter_index` (int), and `messages` (list[ChatMessage]).
- `ChatResponse`: requires `answer` (str).

**Task 3: Implement Chat Business Logic**
Create `backend/core/chat.py`. 
- Implement an async function `generate_chat_response(request: ChatRequest) -> str`.
- Construct the file path: `data/raw/output/{book_stem}_chapter_{chapter_index}.json`. Read its contents. If the file is missing, fall back to `{book_stem}_final.json`. If still missing, return a default string: "Graph data not found."
- Initialize the `AsyncOpenAI` client for DeepSeek.
- **Construct the System Prompt (CRITICAL):**
  - "You are an expert assistant strictly analyzing an Agatha Christie novel based ONLY on the provided JSON graph."
  - "CONSTRAINT 1 (Anti-Spoiler): The injected JSON represents the absolute limit of the reader's current knowledge. DO NOT spoil future events, identities, or twists."
  - "CONSTRAINT 2 (Handling Unknowns): If the user asks a question (e.g., 'Who is the murderer?') and the answer cannot be explicitly deduced from the JSON nodes or edges, you MUST reply naturally that based on the current clues, this remains a mystery. Do not guess."
  - Append the raw JSON string to the system prompt.
- Format the `request.messages` into the OpenAI API format and call the DeepSeek chat completion endpoint. Return the resulting text.

**Task 4: Create FastAPI Endpoint**
In `backend/main.py`, add a `POST /api/v1/chat` endpoint. It accepts a `ChatRequest` and returns a `ChatResponse` utilizing the `generate_chat_response` function. 

**Task 5: Write Pytest**
In `tests/test_api.py` or a new `tests/test_chat.py`:
- Write an async test `test_chat_endpoint_anti_spoiler`.
- Mock the file reading utility to return a dummy JSON string `{"nodes": [{"id": "Victim"}], "edges": []}`.
- Mock the DeepSeek API call to return a static string: "Based on current clues, this is a mystery."
- Assert that `POST /api/v1/chat` returns HTTP 200 and the expected `ChatResponse`.

Run `uv run pytest tests/ -v` and confirm tests pass.