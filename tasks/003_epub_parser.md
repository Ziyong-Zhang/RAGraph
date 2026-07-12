# Task 003: Extensible Document Parsing and Chunking Pipeline

## Objective
Initiate Phase 3 by implementing a robust, extensible document parsing pipeline using the Strategy Pattern (supporting EPUB now, ready for PDF/TXT later). Implement text chunking and define the Pydantic data structures required for the stateful "Graph Merging Logic" (Rolling State).

## Steps to Execute
1. Run `uv add ebooklib beautifulsoup4 langchain-text-splitters`.
2. Create or update `backend/core/models.py`:
   - Define Pydantic models: `Character` (name, aliases, description), `Relationship` (source, target, nature).
   - Define `GraphState`: A model containing `known_characters` (list[str]) and `known_relationships` (list[Relationship]) to serve as the "memory basket" for our entity resolution merging mechanism.
3. Create `backend/core/parsers.py`:
   - Import `ABC` and `abstractmethod` from `abc`.
   - Define an abstract base class `BaseParser` with an abstract method `extract_text(file_path: str) -> str`.
   - Implement `EpubParser(BaseParser)`. Use `ebooklib` to read the EPUB document, iterate through document items of type `ITEM_DOCUMENT`, use `BeautifulSoup` to strip HTML tags, and return clean plain text.
4. Create `backend/core/chunker.py`:
   - Implement `chunk_text(text: str, chunk_size: int = 2000, chunk_overlap: int = 200) -> list[str]`: Use LangChain's `RecursiveCharacterTextSplitter` to divide the extracted text into overlapping chunks.
5. Apply TDD: Create `tests/test_parsers.py`.
   - Write a test for `chunk_text` using a mock long string to assert the correct number of chunks and overlap behavior.
   - Write a test for `EpubParser.extract_text`. Use `unittest.mock.patch` to mock `ebooklib.epub.read_epub` and return a fake book object with dummy HTML content, asserting that `BeautifulSoup` successfully extracts the clean text.
6. Run the tests: `uv run pytest tests/test_parsers.py -v`.
7. If the tests pass, update `harness/process.md` to check off "Implement EPUB parsing module (text extraction, chapter splitting)".
8. Update `harness/progress.md`:
   - Status: "Phase 3 initiated. Extensible parsers (Strategy Pattern), chunking logic, and GraphState models implemented."
   - Next Action: "Implement structured entity extraction via DeepSeek API using instructor and Graph Merging Logic."

## Constraints
- ALL code, docstrings, inline comments, and commit messages MUST BE EXCLUSIVELY IN ENGLISH.
- NEVER use Chinese characters in any generated files.
- Ensure robust error handling (e.g., raising `FileNotFoundError` if the EPUB path is invalid).
- Do not expose or write code that tightly couples this module to the database or UI.