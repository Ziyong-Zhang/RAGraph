"""
Integration test script for the RAGraph pipeline.

Run with: uv run python scripts/run_integration.py [--epub-path PATH] [--max-chunks N]

Requires a valid DEEPSEEK_API_KEY in .env.
All directory paths are read from config.yaml (books_dir, output_dir).
Output filenames are dynamically derived from the input EPUB filename.
"""

import argparse
import asyncio
import json
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


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RAGraph extraction pipeline")
    parser.add_argument(
        "--epub-path",
        type=str,
        default=None,
        help="Path to an EPUB file to process",
    )
    parser.add_argument(
        "--max-chunks",
        type=int,
        default=None,
        help="Override the max_chunks_limit circuit breaker",
    )
    args = parser.parse_args()

    # 1. Load pipeline config
    pipeline_cfg = get_pipeline_config()

    project_root = Path(__file__).resolve().parent.parent

    # 2. Resolve EPUB path
    epub_path = args.epub_path
    if epub_path is None:
        books_dir = project_root / pipeline_cfg.books_dir
        if not books_dir.is_dir():
            logger.warning("books_dir '%s' not found. Creating it.", books_dir)
            books_dir.mkdir(parents=True, exist_ok=True)

        epubs = list(books_dir.glob("*.epub"))
        if not epubs:
            logger.error(
                "No EPUB files found in %s. Place a book there or use --epub-path.",
                books_dir,
            )
            sys.exit(1)
        epub_path = str(epubs[0])
        logger.info("Selected EPUB: %s", epub_path)
    else:
        epub_path = str(Path(epub_path).resolve())

    epub_path_obj = Path(epub_path)
    if not epub_path_obj.is_file():
        logger.error("File not found: %s", epub_path)
        sys.exit(1)

    # 3. Read circuit breaker limit
    max_chunks = (
        args.max_chunks if args.max_chunks is not None else pipeline_cfg.max_chunks_limit
    )
    logger.info("Circuit breaker: max_chunks=%s", max_chunks)

    # 4. Build dynamic output base path from input filename
    output_dir = project_root / pipeline_cfg.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    filename_stem = epub_path_obj.stem
    output_base_path = str(output_dir / filename_stem)
    logger.info("Output base path: %s", output_base_path)

    # 5. Initialize pipeline state
    initial_state: PipelineState = {
        "filepath": epub_path,
        "chapter_chunks": [],
        "current_chunk_index": 0,
        "graph_memory": GraphState(),
        "output_base_path": output_base_path,
        "api_key": api_key,
        "max_chunks": max_chunks,
    }

    # 6. Invoke the pipeline
    logger.info("Starting RAGraph pipeline: %s", epub_path)
    result = await ragraph_app.ainvoke(initial_state)
    logger.info(
        "Pipeline complete. Processed %d chunks.",
        result["current_chunk_index"],
    )
    logger.info(
        "Characters: %d, Relationships: %d",
        len(result["graph_memory"].known_characters),
        len(result["graph_memory"].known_relationships),
    )
    logger.info("Output files in: %s", output_dir)


if __name__ == "__main__":
    asyncio.run(main())