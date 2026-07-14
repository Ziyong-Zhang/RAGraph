from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.core.config import get_pipeline_config


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[str]:
    """Split text into overlapping chunks.

    If chunk_size or chunk_overlap are not provided, they are read from
    the project's config.yaml file at runtime.
    """
    cfg = get_pipeline_config()
    size = chunk_size if chunk_size is not None else cfg.chunk_size
    overlap = chunk_overlap if chunk_overlap is not None else cfg.chunk_overlap

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
    )
    return splitter.split_text(text)


def chunk_chapter_texts(
    chapter_texts: list[str],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[tuple[str, int]]:
    """Split chapter-separated texts into overlapping chunks.

    Each chunk is tagged with its source chapter index (1-based).
    Returns a list of (text, chapter_index) tuples.
    """
    cfg = get_pipeline_config()
    size = chunk_size if chunk_size is not None else cfg.chunk_size
    overlap = chunk_overlap if chunk_overlap is not None else cfg.chunk_overlap

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
    )

    result: list[tuple[str, int]] = []
    for chapter_idx, chapter_text in enumerate(chapter_texts, start=1):
        chunks = splitter.split_text(chapter_text)
        for chunk in chunks:
            result.append((chunk, chapter_idx))

    return result