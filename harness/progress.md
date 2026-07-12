# RAGraph — Current Progress

## Current Status

Phase 3 initiated. Extensible parsers (Strategy Pattern), chunking logic, and GraphState models implemented.

## Completed

- Added `ebooklib`, `beautifulsoup4`, and `langchain-text-splitters` dependencies.
- Defined Pydantic models (`Character`, `Relationship`, `GraphState`) in `backend/core/models.py` for entity resolution merging mechanism.
- Implemented `BaseParser` ABC and `EpubParser` in `backend/core/parsers.py` using the Strategy Pattern (extensible for PDF/TXT).
- Implemented `chunk_text()` in `backend/core/chunker.py` using LangChain's `RecursiveCharacterTextSplitter`.
- Applied TDD: created `tests/test_parsers.py` with `test_chunk_text` (overlap behavior) and `test_epub_parser_extract_text` (mocked EPUB extraction).
- All 5 tests pass across all phases.

## Next Action

Implement structured entity extraction via DeepSeek API using instructor and Graph Merging Logic.
