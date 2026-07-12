from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.core.config import get_pipeline_config


def chunk_text(text: str, chunk_size: int | None = None, chunk_overlap: int | None = None) -> list[str]:
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