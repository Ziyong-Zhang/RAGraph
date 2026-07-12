import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_pipeline_config

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
    """Return a list of available book stems with processed graph files."""
    pipeline_cfg = get_pipeline_config()
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / pipeline_cfg.output_dir

    if not output_dir.is_dir():
        return []

    stems = sorted(
        f.name.replace("_graph.json", "")
        for f in output_dir.glob("*_graph.json")
    )
    return stems


@app.get("/api/v1/graph/{book_stem}")
def get_graph(book_stem: str):
    pipeline_cfg = get_pipeline_config()
    project_root = Path(__file__).resolve().parent.parent
    json_path = project_root / pipeline_cfg.output_dir / f"{book_stem}_graph.json"

    if not json_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Graph data not found. Please process the EPUB file first.",
        )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data
