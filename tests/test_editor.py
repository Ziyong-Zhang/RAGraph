"""Tests for the HITL graph editor (merge nodes + delete edge)."""

import json

from backend.core.editor import merge_nodes_in_json, delete_edge_in_json
from backend.core.models import EdgeDeleteRequest, NodeMergeRequest


def _make_dummy_graph() -> dict:
    return {
        "nodes": [
            {
                "data": {
                    "id": "A",
                    "label": "A",
                    "aliases": "Alpha",
                    "description": "First character",
                }
            },
            {
                "data": {
                    "id": "B",
                    "label": "B",
                    "aliases": "Beta",
                    "description": "Second character",
                }
            },
        ],
        "edges": [
            {
                "data": {
                    "id": "edge-uuid-1",
                    "source": "A",
                    "target": "B",
                    "nature": "friend",
                    "weight": 2,
                }
            },
            {
                "data": {
                    "id": "edge-uuid-2",
                    "source": "B",
                    "target": "A",
                    "nature": "colleague",
                    "weight": 1,
                }
            },
        ],
    }


def test_merge_nodes_updates_aliases():
    data = _make_dummy_graph()
    # We'll test via the editor's internal logic by patching file I/O
    # Instead, test the core merge logic by asserting what the functions do

    # Create a tmp graph file
    import tempfile
    from pathlib import Path
    from unittest.mock import patch

    tmp_dir = Path(tempfile.mkdtemp())
    book_stem = "test_book"
    json_path = tmp_dir / f"{book_stem}_final.json"
    with open(json_path, "w") as f:
        json.dump(data, f)

    with patch("backend.core.editor.get_pipeline_config") as mock_cfg:
        mock_cfg.return_value = type(
            "MockCfg", (), {"output_dir": str(tmp_dir)}
        )()
        req = NodeMergeRequest(
            book_stem=book_stem,
            chapter_index=None,
            source_id="A",
            target_id="B",
        )
        result = merge_nodes_in_json(req)

    assert result["status"] == "success"

    # Read back and verify
    with open(json_path, "r") as f:
        updated = json.load(f)

    # Node A should be removed
    node_ids = [n["data"]["id"] for n in updated["nodes"]]
    assert "A" not in node_ids
    assert "B" in node_ids

    # Find node B
    node_b = next(n for n in updated["nodes"] if n["data"]["id"] == "B")
    assert "Alpha" in node_b["data"]["aliases"] or "Beta" in node_b["data"]["aliases"]
    assert "A" in node_b["data"]["aliases"]

    # All edges should point to B
    for edge in updated["edges"]:
        assert edge["data"]["source"] == "B" or edge["data"]["target"] == "B"


def test_delete_edge():
    data = _make_dummy_graph()

    import tempfile
    from pathlib import Path
    from unittest.mock import patch

    tmp_dir = Path(tempfile.mkdtemp())
    book_stem = "test_book"
    json_path = tmp_dir / f"{book_stem}_final.json"
    with open(json_path, "w") as f:
        json.dump(data, f)

    with patch("backend.core.editor.get_pipeline_config") as mock_cfg:
        mock_cfg.return_value = type(
            "MockCfg", (), {"output_dir": str(tmp_dir)}
        )()
        req = EdgeDeleteRequest(
            book_stem=book_stem,
            chapter_index=None,
            edge_id="edge-uuid-1",
        )
        result = delete_edge_in_json(req)

    assert result["status"] == "success"

    with open(json_path, "r") as f:
        updated = json.load(f)

    assert len(updated["edges"]) == 1
    assert updated["edges"][0]["data"]["id"] == "edge-uuid-2"


def test_merge_nonexistent_source():
    import tempfile
    from pathlib import Path
    from unittest.mock import patch

    tmp_dir = Path(tempfile.mkdtemp())
    book_stem = "test_book"
    json_path = tmp_dir / f"{book_stem}_final.json"
    with open(json_path, "w") as f:
        json.dump(_make_dummy_graph(), f)

    with patch("backend.core.editor.get_pipeline_config") as mock_cfg:
        mock_cfg.return_value = type(
            "MockCfg", (), {"output_dir": str(tmp_dir)}
        )()
        req = NodeMergeRequest(
            book_stem=book_stem,
            chapter_index=None,
            source_id="NONEXISTENT",
            target_id="B",
        )
        result = merge_nodes_in_json(req)

    assert result["status"] == "error"