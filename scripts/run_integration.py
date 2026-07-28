"""
Integration test script for the RAGraph pipeline.

Run with: uv run python scripts/run_integration.py [--epub-path PATH] [--max-chunks N]

If --epub-path is provided, only that single book is processed.
Otherwise, ALL EPUB files found in books_dir (from config.yaml) are processed.

Requires a valid DEEPSEEK_API_KEY in .env.
All directory paths are read from config.yaml (books_dir, output_dir).
Output filenames are dynamically derived from each input EPUB filename.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Ensure the project root is on sys.path for direct execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load .env into os.environ EARLY, before any LangGraph/LLM imports.
from backend.core.config import get_settings

settings = get_settings()
api_key = settings.DEEPSEEK_API_KEY

from backend.core.config import get_pipeline_config
from backend.core.models import GraphState
from backend.core.workflow import PipelineState, ragraph_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def process_single_book(
    epub_path: str,
    output_dir: Path,
    max_chunks: int | None,
) -> None:
    """Run the RAGraph pipeline on a single EPUB file."""
    epub_path_obj = Path(epub_path)
    filename_stem = epub_path_obj.stem
    output_base_path = str(output_dir / filename_stem)

    # Initialize pipeline state
    initial_state: PipelineState = {
        "filepath": epub_path,
        "chapter_chunks": [],
        "current_chunk_index": 0,
        "graph_memory": GraphState(),
        "output_base_path": output_base_path,
        "api_key": api_key,
        "max_chunks": max_chunks,
    }

    # Invoke the pipeline
    logger.info("Starting RAGraph pipeline: %s", epub_path)
    result = await ragraph_app.ainvoke(initial_state)
    logger.info(
        "Pipeline complete for '%s'. Processed %d chunks. "
        "Characters: %d, Relationships: %d. Output in: %s",
        filename_stem,
        result["current_chunk_index"],
        len(result["graph_memory"].known_characters),
        len(result["graph_memory"].known_relationships),
        output_dir,
    )


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the RAGraph extraction pipeline on one or all books"
    )
    parser.add_argument(
        "--epub-path",
        type=str,
        default=None,
        help="Path to a single EPUB file to process (if omitted, all books are processed)",
    )
    parser.add_argument(
        "--max-chunks",
        type=int,
        default=None,
        help="Override the max_chunks_limit circuit breaker",
    )
    args = parser.parse_args()

    # Load pipeline config
    pipeline_cfg = get_pipeline_config()
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / pipeline_cfg.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve circuit breaker limit
    max_chunks = (
        args.max_chunks if args.max_chunks is not None else pipeline_cfg.max_chunks_limit
    )
    logger.info("Circuit breaker: max_chunks=%s", max_chunks)

    if args.epub_path is not None:
        # Single-book mode
        epub_path = str(Path(args.epub_path).resolve())
        if not Path(epub_path).is_file():
            logger.error("File not found: %s", epub_path)
            sys.exit(1)
        await process_single_book(epub_path, output_dir, max_chunks)
        return

    # Batch mode: process all EPUBs in books_dir
    books_dir = project_root / pipeline_cfg.books_dir
    if not books_dir.is_dir():
        logger.warning("books_dir '%s' not found. Creating it.", books_dir)
        books_dir.mkdir(parents=True, exist_ok=True)
        logger.info("No books to process. Place .epub files in %s and re-run.", books_dir)
        return

    epubs = sorted(books_dir.glob("*.epub"))
    if not epubs:
        logger.info("No .epub files found in %s. Nothing to process.", books_dir)
        return

    logger.info("Found %d EPUB(s) in %s. Starting batch processing...", len(epubs), books_dir)
    for epub_file in epubs:
        await process_single_book(str(epub_file), output_dir, max_chunks)

    logger.info("Batch processing complete. All output files are in: %s", output_dir)


if __name__ == "__main__":
    asyncio.run(main())