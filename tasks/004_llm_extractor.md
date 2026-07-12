# Task 004: Structured LLM Extraction and Graph Merging Logic

## Objective
Continue Phase 3 by implementing the core Agentic extractor. This module will use the `instructor` library to patch the OpenAI client (targeting DeepSeek), enforce strictly typed JSON outputs based on our Pydantic models, and implement the "Rolling State" graph merging logic to resolve entities across text chunks.

## Steps to Execute
1. Run `uv add openai instructor`.
2. Create `backend/core/extractor.py`:
   - Import `AsyncOpenAI` from `openai` and `instructor`.
   - Import `Character`, `Relationship`, and `GraphState` from `backend.core.models`.
   - Write an async function: `async def extract_entities(text_chunk: str, current_state: GraphState, api_key: str) -> GraphState`.
   - Inside the function, initialize the async client targeting DeepSeek's base URL (`https://api.deepseek.com/v1`). Patch it using `instructor.from_openai(client, mode=instructor.Mode.JSON)`.
   - Craft a highly specific System Prompt: Instruct the model to act as a literary analyst. It must read the `text_chunk`, extract characters and relationships, and CRITICALLY, it must review the `current_state`. If a character already exists in `current_state`, it should merge aliases rather than creating a duplicate entity.
   - Execute the LLM call using `response_model=GraphState`.
   - Return the newly generated `GraphState`.
3. Apply TDD: Create `tests/test_extractor.py`.
   - Use `@pytest.mark.asyncio`.
   - Write `test_extract_entities_mock()`. Since LLM calls are non-deterministic and cost money, use `unittest.mock.patch` to intercept the `client.chat.completions.create` call (or the instructor wrapper) and return a hardcoded, valid `GraphState` object.
   - Assert that the function returns a `GraphState` and correctly handles the inputs.
4. Run the tests: `uv run pytest tests/test_extractor.py -v`.
5. If the tests pass, update `harness/process.md` to check off "Integrate DeepSeek API for LLM-based character extraction".
6. Update `harness/progress.md`:
   - Status: "Phase 3 ongoing. LLM structured extraction and Graph Merging Logic implemented via instructor."
   - Next Action: "Implement NetworkX graph construction and timeline logic."

## Constraints
- ALL code, docstrings, inline comments, and commit messages MUST BE EXCLUSIVELY IN ENGLISH.
- NEVER use Chinese characters in any generated files.
- The function MUST NOT contain hardcoded API keys (it receives it as a parameter).
- Ensure network calls have basic error handling considerations (though standard instructor/openai retries are sufficient for now).