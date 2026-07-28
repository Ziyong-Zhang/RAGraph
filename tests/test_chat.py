"""Tests for the Anti-Spoiler Chat endpoint."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_chat_endpoint_missing_graph(tmp_path):
    """When no graph file exists, chat returns a default message."""
    with patch("backend.core.chat.get_pipeline_config") as mock_cfg:
        mock_cfg.return_value = type(
            "MockCfg", (), {"output_dir": str(tmp_path / "nonexistent")}
        )()
        payload = {
            "book_stem": "nonexistent_book",
            "chapter_index": 1,
            "messages": [{"role": "user", "content": "Who is the murderer?"}],
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["answer"] == "Graph data not found."


def test_chat_endpoint_anti_spoiler(tmp_path):
    """Test the chat endpoint respects anti-spoiler constraints."""
    # Create a dummy graph JSON file
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    graph_file = output_dir / "test_book_chapter_1.json"
    graph_file.write_text(
        '{"nodes": [{"data": {"id": "Victim", "label": "Victim"}}], "edges": []}',
        encoding="utf-8",
    )

    # Mock config to point to tmp_path output
    with (
        patch("backend.core.chat.get_pipeline_config") as mock_cfg,
        patch("backend.core.chat.AsyncOpenAI") as mock_openai,
    ):
        mock_cfg.return_value = type(
            "MockCfg", (), {"output_dir": str(output_dir)}
        )()
        # Mock the DeepSeek API call
        mock_instance = MagicMock()
        mock_create = AsyncMock()
        mock_create.return_value.choices = [
            MagicMock(message=MagicMock(content="Based on current clues, this is a mystery."))
        ]
        mock_instance.chat.completions.create = mock_create
        mock_openai.return_value = mock_instance

        payload = {
            "book_stem": "test_book",
            "chapter_index": 1,
            "messages": [{"role": "user", "content": "Who is the murderer?"}],
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["answer"] == "Based on current clues, this is a mystery."