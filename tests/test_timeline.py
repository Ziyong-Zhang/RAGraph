import json
import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _create_mock_output_dir(tmp_path, book_stem, chapter_indices):
    """Helper to create a mock output dir with chapter JSON files."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx in chapter_indices:
        data = {
            "nodes": [{"data": {"id": f"char_{idx}", "label": f"Character {idx}"}}],
            "edges": [],
        }
        filepath = output_dir / f"{book_stem}_chapter_{idx}.json"
        with open(filepath, "w") as f:
            json.dump(data, f)

    # Also create a final file
    final_data = {
        "nodes": [{"data": {"id": "final_char", "label": "Final Character"}}],
        "edges": [],
    }
    with open(output_dir / f"{book_stem}_final.json", "w") as f:
        json.dump(final_data, f)

    return output_dir


class MockPipelineConfig:
    """Mock config pointing to a temp directory."""

    def __init__(self, output_dir):
        self.output_dir = output_dir


def test_graph_metadata_endpoint(tmp_path):
    """Test /api/v1/graph/{book_stem}/metadata returns correct chapter indices."""
    output_dir = _create_mock_output_dir(tmp_path, "test_book", [1, 2, 3])
    mock_cfg = MockPipelineConfig(str(output_dir))

    with patch("backend.main.get_pipeline_config", return_value=mock_cfg):
        resp = client.get("/api/v1/graph/test_book/metadata")
        assert resp.status_code == 200
        data = resp.json()
        assert data["book_stem"] == "test_book"
        assert data["available_chapters"] == [1, 2, 3]
        assert data["max_chapter"] == 3


def test_graph_metadata_endpoint_no_chapters(tmp_path):
    """Test metadata endpoint returns empty list when no chapter files exist."""
    output_dir = _create_mock_output_dir(tmp_path, "test_book", [])
    mock_cfg = MockPipelineConfig(str(output_dir))

    with patch("backend.main.get_pipeline_config", return_value=mock_cfg):
        resp = client.get("/api/v1/graph/test_book/metadata")
        assert resp.status_code == 200
        data = resp.json()
        assert data["available_chapters"] == []
        assert data["max_chapter"] is None


def test_graph_endpoint_with_chapter(tmp_path):
    """Test GET /api/v1/graph/{book_stem}?chapter_index=N."""
    output_dir = _create_mock_output_dir(tmp_path, "test_book", [1, 2])
    mock_cfg = MockPipelineConfig(str(output_dir))

    with patch("backend.main.get_pipeline_config", return_value=mock_cfg):
        resp = client.get("/api/v1/graph/test_book?chapter_index=1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["data"]["id"] == "char_1"


def test_graph_endpoint_with_invalid_chapter(tmp_path):
    """Test chapter endpoint returns 404 for nonexistent chapters."""
    output_dir = _create_mock_output_dir(tmp_path, "test_book", [1])
    mock_cfg = MockPipelineConfig(str(output_dir))

    with patch("backend.main.get_pipeline_config", return_value=mock_cfg):
        resp = client.get("/api/v1/graph/test_book?chapter_index=99")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()


def test_graphs_list_excludes_chapter_suffixes(tmp_path):
    """Test /api/v1/graphs returns clean stems without _chapter_X noise."""
    output_dir = _create_mock_output_dir(tmp_path, "mybook", [1, 2, 3])
    mock_cfg = MockPipelineConfig(str(output_dir))

    with patch("backend.main.get_pipeline_config", return_value=mock_cfg):
        resp = client.get("/api/v1/graphs")
        assert resp.status_code == 200
        stems = resp.json()
        assert "mybook" in stems
        # No chapter-X files should appear as stems
        assert not any("chapter" in s for s in stems)