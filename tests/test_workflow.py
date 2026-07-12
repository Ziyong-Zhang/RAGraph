from unittest.mock import AsyncMock, patch

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

    # Start with filepath + api_key; initialize_document will produce 2 chunks
    initial: PipelineState = {
        "filepath": "/fake/book.epub",
        "text_chunks": [],
        "current_chunk_index": 0,
        "graph_memory": GraphState(),
        "output_graph_path": "/fake/output.graphml",
        "api_key": "sk-test",
        "max_chunks": None,
    }

    with (
        patch("backend.core.workflow.EpubParser.extract_text", return_value="chap1 chap2"),
        patch("backend.core.workflow.chunk_text", return_value=["chunk_a", "chunk_b"]),
        patch("backend.core.workflow.extract_entities", new_callable=AsyncMock, return_value=dummy_state),
        patch("backend.core.workflow.build_networkx_graph"),
        patch("backend.core.workflow.save_graph"),
    ):
        result = await ragraph_app.ainvoke(initial)

    # After the pipeline runs, graph_memory should hold the merged state
    assert len(result["graph_memory"].known_relationships) == 1
    assert result["graph_memory"].known_relationships[0].source == "A"
    assert result["graph_memory"].known_relationships[0].target == "B"
    assert result["current_chunk_index"] == 2  # both chunks processed