from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.core.models import GraphState, Relationship
from backend.core.workflow import PipelineState, ragraph_app


@pytest.mark.asyncio
async def test_workflow_loops_and_finalizes():
    """Mock the core nodes to verify the pipeline state machine loops correctly."""
    dummy_state = GraphState(
        known_characters=[],
        known_relationships=[
            Relationship(source="A", target="B", nature="friend"),
        ],
    )

    # Build 2 chunks both from chapter 1
    chapter_chunks = [("chunk_a", 1), ("chunk_b", 1)]

    initial: PipelineState = {
        "filepath": "/fake/book.epub",
        "chapter_chunks": [],
        "current_chunk_index": 0,
        "graph_memory": GraphState(),
        "output_base_path": "/fake/output/test_book",
        "api_key": "sk-test",
        "max_chunks": None,
    }

    with (
        patch(
            "backend.core.workflow.EpubParser.extract_chapter_texts",
            return_value=["chap1 content"],
        ),
        patch(
            "backend.core.workflow.chunk_chapter_texts",
            return_value=chapter_chunks,
        ),
        patch(
            "backend.core.workflow.extract_entities",
            new_callable=AsyncMock,
            return_value=dummy_state,
        ),
        patch("backend.core.workflow.build_networkx_graph"),
        patch("backend.core.workflow.save_graph"),
        patch("backend.core.workflow.export_to_cytoscape_json", return_value={"nodes": [], "edges": []}),
        patch("builtins.open", new_callable=MagicMock),
    ):
        result = await ragraph_app.ainvoke(initial)

    # After the pipeline runs, graph_memory should hold the merged state
    assert len(result["graph_memory"].known_relationships) == 1
    assert result["graph_memory"].known_relationships[0].source == "A"
    assert result["graph_memory"].known_relationships[0].target == "B"
    assert result["current_chunk_index"] == 2  # both chunks processed