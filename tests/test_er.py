"""Tests for deterministic entity resolution (entity_resolver.py)."""

from backend.core.models import Character, GraphState, Relationship
from backend.core.entity_resolver import resolve_and_merge_entities, resolve_graph_state


def test_no_merge_when_no_overlap():
    """Characters with no shared names or aliases should remain separate."""
    chars = [
        Character(name="Hercule Poirot", aliases=["Poirot"], description="Belgian detective"),
        Character(name="Miss Marple", aliases=["Marple"], description="Amateur sleuth"),
    ]
    merged = resolve_and_merge_entities(chars)
    assert len(merged) == 2


def test_merge_by_name_match():
    """Characters with identical names (case-insensitive) should merge."""
    chars = [
        Character(name="John Smith", aliases=[], description="First mention"),
        Character(name="john smith", aliases=[], description="Second mention"),
    ]
    merged = resolve_and_merge_entities(chars)
    assert len(merged) == 1
    assert merged[0].name == "John Smith"  # longest name wins (both same length)
    assert "First mention" in merged[0].description
    assert "Second mention" in merged[0].description


def test_merge_by_name_in_alias():
    """Character C2's name is an alias of C1, so they should merge."""
    chars = [
        Character(name="Caroline Crale", aliases=["Carrie"], description="Mother"),
        Character(name="Carrie", aliases=["Caroline"], description="Daughter"),
    ]
    merged = resolve_and_merge_entities(chars)
    assert len(merged) == 1
    # Canonical name should be the longest
    assert merged[0].name == "Caroline Crale"


def test_merge_by_shared_alias():
    """Two characters sharing a common alias should be merged."""
    chars = [
        Character(name="Alpha", aliases=["X", "Y"], description="First"),
        Character(name="Beta", aliases=["Y", "Z"], description="Second"),
    ]
    merged = resolve_and_merge_entities(chars)
    assert len(merged) == 1
    assert merged[0].name == "Alpha"  # or "Beta", both same length; Alpha first in list
    # Aliases should include all unique aliases except the canonical name
    all_aliases = [a.lower() for a in merged[0].aliases]
    assert "x" in all_aliases
    assert "y" in all_aliases
    assert "z" in all_aliases


def test_merge_chained_overlap():
    """Chain: C1 name is C2 alias, C2 name is C3 alias -> all three merge."""
    chars = [
        Character(name="A", aliases=["B"], description="Char A"),
        Character(name="B", aliases=["C"], description="Char B"),
        Character(name="C", aliases=["D"], description="Char C"),
    ]
    merged = resolve_and_merge_entities(chars)
    assert len(merged) == 1
    # All three collapsed into one


def test_resolve_graph_state_redirects_relationships():
    """Relationships pointing to merged-away names should be redirected."""
    state = GraphState(
        known_characters=[
            Character(name="Poirot", aliases=["Hercule Poirot"], description="Detective"),
            Character(name="Hercule Poirot", aliases=["Poirot"], description="Belgian detective"),
        ],
        known_relationships=[
            Relationship(source="Poirot", target="Hastings", nature="friend"),
            Relationship(source="Hastings", target="Poirot", nature="friend"),
        ],
    )
    resolved = resolve_graph_state(state)
    assert len(resolved.known_characters) == 1
    assert resolved.known_characters[0].name == "Hercule Poirot"
    # Both relationships should point to "Hercule Poirot" now
    for rel in resolved.known_relationships:
        assert rel.source == "Hercule Poirot" or rel.target == "Hercule Poirot"


def test_chinese_dot_normalization():
    """Characters with Chinese separator dots should merge correctly.

    '卡蘿琳．奎雷' (full-width dot) and '卡蘿琳·奎雷' (middle dot) should
    both normalize to '卡蘿琳奎雷'. A character whose name is another's
    alias (e.g., '奎雷夫人' matched via alias list) should also merge.
    """
    chars = [
        Character(name="卡蘿琳．奎雷", aliases=["奎雷夫人"], description="Full-width dot version"),
        Character(name="奎雷夫人", aliases=[], description="Title+Surname form"),
        Character(name="卡蘿琳·奎雷", aliases=[], description="Middle dot version"),
    ]
    merged = resolve_and_merge_entities(chars)
    assert len(merged) == 1, f"Expected 1 merged character, got {len(merged)}"
    # Canonical name should be the longest (by char count)
    assert merged[0].name == "卡蘿琳．奎雷"


def test_normalize_name_removes_chinese_dots():
    """Verify normalize_name handles various dot characters."""
    from backend.core.entity_resolver import normalize_name

    assert normalize_name("卡蘿琳．奎雷") == normalize_name("卡蘿琳·奎雷")
    assert normalize_name("卡蘿琳．奎雷") == normalize_name("卡蘿琳奎雷")
    assert normalize_name("甲．乙·丙•丁") == "甲乙丙丁"


def test_empty_characters():
    """Empty list should return empty list."""
    assert resolve_and_merge_entities([]) == []
