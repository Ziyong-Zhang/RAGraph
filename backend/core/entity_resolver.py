"""Deterministic Entity Resolution (Entity Resolution) module.

Uses a Union-Find (Disjoint Set Union) structure to group duplicate characters
based on name and alias overlap, then merges them into canonical entities.
"""

import re
from collections import defaultdict

from backend.core.models import Character, GraphState


# Chinese separator dots commonly used in translated names
_CHINESE_DOTS = "．·•"


def normalize_name(text: str) -> str:
    """Normalize a name or alias for comparison.

    1. Strip leading/trailing whitespace and lowercase.
    2. Remove all spaces within the string.
    3. Remove Chinese separator dots (．, ·, •) frequently used in
       translated names (e.g., '卡蘿琳．奎雷' -> '卡蘿琳奎雷').
    4. Remove standard punctuation characters.
    """
    text = text.strip().lower()
    text = text.replace(" ", "")
    for dot in _CHINESE_DOTS:
        text = text.replace(dot, "")
    text = re.sub(r"[^\w\s]", "", text)
    return text


class _UnionFind:
    """Simple Union-Find (Disjoint Set Union) for grouping equivalent characters."""

    def __init__(self) -> None:
        self._parent: dict[int, int] = {}
        self._rank: dict[int, int] = {}

    def find(self, x: int) -> int:
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def union(self, x: int, y: int) -> None:
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return
        if self._rank[root_x] < self._rank[root_y]:
            self._parent[root_x] = root_y
        elif self._rank[root_x] > self._rank[root_y]:
            self._parent[root_y] = root_x
        else:
            self._parent[root_y] = root_x
            self._rank[root_x] += 1

    def add(self, x: int) -> None:
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0


def resolve_and_merge_entities(characters: list[Character]) -> list[Character]:
    """Merge duplicate characters using deterministic alias matching.

    Two characters are considered equivalent if any of these hold
    (after case-insensitive normalization):

    1. Their names match exactly.
    2. One character's name appears in the other's aliases.
    3. Their alias lists share at least one common alias.
    """
    if not characters:
        return []

    # Assign each character an index
    n = len(characters)
    uf = _UnionFind()
    for i in range(n):
        uf.add(i)

    # Precompute normalized names and alias sets
    norm_names: list[str] = []
    norm_alias_sets: list[set[str]] = []

    for ch in characters:
        norm_names.append(normalize_name(ch.name))
        aliases_set = {normalize_name(a) for a in ch.aliases}
        norm_alias_sets.append(aliases_set)

    # Compare all pairs for equivalence
    for i in range(n):
        for j in range(i + 1, n):
            # Rule 1: names match
            if norm_names[i] == norm_names[j]:
                uf.union(i, j)
                continue

            # Rule 2: name matches alias of the other
            if norm_names[i] in norm_alias_sets[j] or norm_names[j] in norm_alias_sets[i]:
                uf.union(i, j)
                continue

            # Rule 3: shared alias intersection
            if norm_alias_sets[i] & norm_alias_sets[j]:
                uf.union(i, j)

    # Group indices by root
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        root = uf.find(i)
        groups[root].append(i)

    # Merge each group into a single canonical character
    merged: list[Character] = []
    for group_indices in groups.values():
        group_chars = [characters[i] for i in group_indices]

        # Choose canonical name: longest name in the group
        canonical_name = max(
            (ch.name for ch in group_chars),
            key=lambda name: len(name.strip()),
        )

        # Consolidate all unique aliases (excluding canonical name)
        all_aliases: list[str] = []
        for ch in group_chars:
            for alias in ch.aliases:
                if normalize_name(alias) != normalize_name(canonical_name) and normalize_name(
                    alias
                ) not in {normalize_name(a) for a in all_aliases}:
                    all_aliases.append(alias)

        # Merge descriptions (deduplicated)
        seen_descs: set[str] = set()
        desc_parts: list[str] = []
        for ch in group_chars:
            desc = ch.description.strip()
            if desc and desc not in seen_descs:
                seen_descs.add(desc)
                desc_parts.append(desc)
        merged_description = " | ".join(desc_parts)

        merged.append(
            Character(
                name=canonical_name,
                aliases=all_aliases,
                description=merged_description,
            )
        )

    return merged


def resolve_graph_state(state: GraphState) -> GraphState:
    """Apply entity resolution to a GraphState, also redirecting relationships."""
    if not state.known_characters:
        return state

    merged_characters = resolve_and_merge_entities(state.known_characters)

    # Build name mapping: old name -> canonical name
    name_map: dict[str, str] = {}
    for ch in state.known_characters:
        norm_ch_name = normalize_name(ch.name)
        for merged_ch in merged_characters:
            if normalize_name(ch.name) == normalize_name(merged_ch.name):
                name_map[ch.name] = merged_ch.name
                break
            if normalize_name(ch.name) in {normalize_name(a) for a in merged_ch.aliases}:
                name_map[ch.name] = merged_ch.name
                break

    # Redirect relationships to canonical names
    resolved_relationships = []
    seen_edges: set[tuple[str, str, str]] = set()
    for rel in state.known_relationships:
        src = name_map.get(rel.source, rel.source)
        tgt = name_map.get(rel.target, rel.target)
        key = (src, tgt, rel.nature)
        if key not in seen_edges:
            seen_edges.add(key)
            resolved_relationships.append(
                type(rel)(source=src, target=tgt, nature=rel.nature)
            )

    return GraphState(
        known_characters=merged_characters,
        known_relationships=resolved_relationships,
    )