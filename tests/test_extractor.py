from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.core.models import Character, GraphState, Relationship
from backend.core.extractor import extract_entities


@pytest.mark.asyncio
async def test_extract_entities_mock():
    initial_state = GraphState(
        known_characters=[
            Character(name="Hercule Poirot", aliases=["Poirot"], description="Belgian detective"),
        ],
        known_relationships=[
            Relationship(source="Hercule Poirot", target="Captain Hastings", nature="friend"),
        ],
    )

    expected_state = GraphState(
        known_characters=[
            Character(name="Hercule Poirot", aliases=["Poirot"], description="Belgian detective"),
            Character(name="Captain Hastings", aliases=["Hastings"], description="Poirot's friend"),
            Character(name="Inspector Japp", aliases=["Japp"], description="Scotland Yard inspector"),
        ],
        known_relationships=[
            Relationship(source="Hercule Poirot", target="Captain Hastings", nature="friend"),
            Relationship(source="Hercule Poirot", target="Inspector Japp", nature="colleague"),
        ],
    )

    mock_client = MagicMock()
    mock_create = AsyncMock(return_value=expected_state)
    mock_client.chat.completions.create = mock_create

    with patch("backend.core.extractor.instructor.from_openai", return_value=mock_client):
        result = await extract_entities(
            text_chunk="Poirot and Japp worked together on the case.",
            current_state=initial_state,
            api_key="sk-test-fake-key",
        )

    assert isinstance(result, GraphState)
    assert len(result.known_characters) == 3
    assert len(result.known_relationships) == 2
    assert result.known_characters[0].name == "Hercule Poirot"
    assert result.known_characters[1].name == "Captain Hastings"
    assert result.known_characters[2].name == "Inspector Japp"
    mock_create.assert_awaited_once()
