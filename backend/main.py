import json
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Initialize observability (LangSmith) BEFORE any LangChain/LLM imports.
from backend.core.config import get_settings
get_settings()

from backend.core.chat import generate_chat_response
from backend.core.config import get_pipeline_config
from backend.core.models import ChatRequest, ChatResponse

app = FastAPI(title="RAGraph")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ragraph"}


@app.get("/api/v1/graphs")
def list_graphs():
    """Return a list of available book stems with processed graph files.

    Only returns base book stems, filtering out any _chapter_X or _final
    suffixed files to keep the selection dropdown clean.
    """
    pipeline_cfg = get_pipeline_config()
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / pipeline_cfg.output_dir

    if not output_dir.is_dir():
        return []

    stems: set[str] = set()
    for f in output_dir.glob("*_graph.json"):
        parts = f.name.replace("_graph.json", "").rsplit("_", 1)
        stem = parts[0]
        stems.add(stem)
    # Also catch files named with _final or _chapter suffix
    for f in output_dir.glob("*_final.json"):
        stem = f.name.replace("_final.json", "")
        stems.add(stem)
    for f in output_dir.glob("*_chapter_*.json"):
        stem = f.name.rsplit("_chapter_", 1)[0]
        stems.add(stem)

    return sorted(stems)


@app.get("/api/v1/graph/{book_stem}/metadata")
def get_graph_metadata(book_stem: str):
    """Return chapter metadata for a processed book."""
    pipeline_cfg = get_pipeline_config()
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / pipeline_cfg.output_dir

    chapter_indices: list[int] = []
    pattern = f"{book_stem}_chapter_*.json"
    for f in output_dir.glob(pattern):
        try:
            idx = int(f.name.rsplit("_chapter_", 1)[1].replace(".json", ""))
            chapter_indices.append(idx)
        except (ValueError, IndexError):
            continue

    chapter_indices = sorted(chapter_indices)
    max_chapter = max(chapter_indices) if chapter_indices else None

    return {
        "book_stem": book_stem,
        "available_chapters": chapter_indices,
        "max_chapter": max_chapter,
    }


@app.get("/api/v1/graph/{book_stem}")
def get_graph(
    book_stem: str,
    chapter_index: Optional[int] = Query(None, alias="chapter_index"),
):
    """Return graph data for a book, optionally for a specific chapter."""
    pipeline_cfg = get_pipeline_config()
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / pipeline_cfg.output_dir

    if chapter_index is not None:
        # Load chapter-specific snapshot
        json_path = output_dir / f"{book_stem}_chapter_{chapter_index}.json"
        if not json_path.is_file():
            raise HTTPException(
                status_code=404,
                detail=f"Chapter {chapter_index} graph data not found.",
            )
    else:
        # Load final graph
        json_path = output_dir / f"{book_stem}_final.json"
        if not json_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Graph data not found. Please process the EPUB file first.",
            )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Anti-spoiler chat: answers based only on the current chapter's graph."""
    settings = get_settings()
    answer = await generate_chat_response(request, settings.DEEPSEEK_API_KEY)
    return ChatResponse(answer=answer)
