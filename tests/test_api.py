from unittest.mock import patch

from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "ragraph"}


def test_graphs_list_empty():
    """When output_dir doesn't exist or is empty, /api/v1/graphs returns []."""
    with patch("backend.main.get_pipeline_config") as mock_get:
        mock_cfg = type("MockConfig", (), {"output_dir": "/tmp/nonexistent_dir_xyz"})()
        mock_get.return_value = mock_cfg
        response = client.get("/api/v1/graphs")
        assert response.status_code == 200
        assert response.json() == []


def test_graph_endpoint_not_found():
    response = client.get("/api/v1/graph/nonexistent_book")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
