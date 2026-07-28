"""HITL Graph Editor — modifies Cytoscape JSON files on disk.

These functions are called by the FastAPI endpoints and directly mutate
the JSON snapshot files (chapter or final). No Pydantic models are used
here; the JSON is read, manipulated as plain dicts, and written back.
"""

import json
from copy import deepcopy
from pathlib import Path

from backend.core.config import get_pipeline_config
from backend.core.models import EdgeDeleteRequest, NodeMergeRequest


def _resolve_json_path(book_stem: str, chapter_index: int | None) -> Path | None:
    """Return the path to the target JSON file.

    Tries chapter-specific file first, then falls back to _final.json.
    Returns None if neither exists.
    """
    pipeline_cfg = get_pipeline_config()
    project_root = Path(__file__).resolve().parent.parent.parent
    output_dir = project_root / pipeline_cfg.output_dir

    if chapter_index is not None:
        chapter_path = output_dir / f"{book_stem}_chapter_{chapter_index}.json"
        if chapter_path.is_file():
            return chapter_path

    final_path = output_dir / f"{book_stem}_final.json"
    return final_path if final_path.is_file() else None


def merge_nodes_in_json(req: NodeMergeRequest) -> dict:
    """Merge source_id into target_id within the target JSON file.

    1. Appends source's name and aliases to target's aliases.
    2. Combines descriptions.
    3. Redirects all edges pointing to source_id to target_id.
    4. Removes the source_id node.
    """
    filepath = _resolve_json_path(req.book_stem, req.chapter_index)
    if filepath is None:
        return {"status": "error", "detail": "Graph file not found."}

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    # Find source and target nodes
    source_node = None
    target_node = None
    for node in nodes:
        nd = node.get("data", {})
        if nd.get("id") == req.source_id:
            source_node = node
        if nd.get("id") == req.target_id:
            target_node = node

    if source_node is None:
        return {"status": "error", "detail": f"Source node '{req.source_id}' not found."}
    if target_node is None:
        return {"status": "error", "detail": f"Target node '{req.target_id}' not found."}

    src_data = source_node["data"]
    tgt_data = target_node["data"]

    # Merge aliases: append source name if not already present, plus all source aliases
    existing_aliases_lower = {a.lower().strip() for a in tgt_data.get("aliases", "").split(", ") if a.strip()}

    new_aliases: list[str] = []

    # If source name is from the selected dropdown (not already an alias), add it
    src_name_lower = src_data.get("label", src_data.get("id", "")).lower().strip()
    if src_name_lower and src_name_lower not in existing_aliases_lower:
        new_aliases.append(src_data.get("label", src_data.get("id", "")))
        existing_aliases_lower.add(src_name_lower)

    # Add source's existing aliases
    for alias in src_data.get("aliases", "").split(", "):
        alias_clean = alias.strip()
        if alias_clean and alias_clean.lower() not in existing_aliases_lower:
            new_aliases.append(alias_clean)
            existing_aliases_lower.add(alias_clean.lower())

    if new_aliases:
        old_alias_str = tgt_data.get("aliases", "")
        tgt_data["aliases"] = (old_alias_str + ", " + ", ".join(new_aliases)).strip(", ")

    # Merge descriptions
    src_desc = src_data.get("description", "").strip()
    tgt_desc = tgt_data.get("description", "").strip()
    if src_desc and src_desc.lower() not in tgt_desc.lower():
        tgt_data["description"] = (tgt_desc + " | " + src_desc).strip(" | ")

    # Redirect edges: change any source/target that matches source_id to target_id
    for edge in edges:
        ed = edge.get("data", {})
        if ed.get("source") == req.source_id:
            ed["source"] = req.target_id
        if ed.get("target") == req.source_id:
            ed["target"] = req.target_id

    # Remove source node
    data["nodes"] = [n for n in nodes if n.get("data", {}).get("id") != req.source_id]

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {"status": "success"}


def delete_edge_in_json(req: EdgeDeleteRequest) -> dict:
    """Delete an edge by its ID from the target JSON file."""
    filepath = _resolve_json_path(req.book_stem, req.chapter_index)
    if filepath is None:
        return {"status": "error", "detail": "Graph file not found."}

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    edges = data.get("edges", [])
    original_count = len(edges)
    data["edges"] = [e for e in edges if e.get("data", {}).get("id") != req.edge_id]

    if len(data["edges"]) == original_count:
        return {"status": "error", "detail": f"Edge '{req.edge_id}' not found."}

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {"status": "success"}