import os

import networkx as nx

from backend.core.models import Character, GraphState, Relationship
from backend.core.graph_builder import build_networkx_graph, save_graph, load_graph


def test_build_networkx_graph_weight_accumulation():
    """Duplicate edges with same nature should accumulate weight."""
    state = GraphState(
        known_characters=[
            Character(name="Hercule Poirot", aliases=["Poirot"], description="Belgian detective"),
            Character(name="Captain Hastings", aliases=["Hastings"], description="Poirot's friend"),
        ],
        known_relationships=[
            Relationship(source="Hercule Poirot", target="Captain Hastings", nature="friend"),
            Relationship(source="Hercule Poirot", target="Captain Hastings", nature="friend"),
            Relationship(source="Hercule Poirot", target="Captain Hastings", nature="colleague"),
        ],
    )

    G = build_networkx_graph(state)

    assert isinstance(G, nx.MultiDiGraph)
    assert G.number_of_nodes() == 2
    assert G.has_node("Hercule Poirot")
    assert G.has_node("Captain Hastings")
    assert G.nodes["Hercule Poirot"]["aliases"] == "Poirot"
    assert G.nodes["Hercule Poirot"]["description"] == "Belgian detective"

    # 3 edges added: 2 "friend" which collapse into weight=2, 1 "colleague" weight=1
    edge_data_friend = G.get_edge_data("Hercule Poirot", "Captain Hastings")
    assert edge_data_friend is not None
    weights = [v.get("weight", 0) for v in edge_data_friend.values()]
    assert 2 in weights, "Duplicate 'friend' edges should be collapsed with weight=2"
    assert 1 in weights, "'colleague' edge should exist with weight=1"

    # Total of 2 edge keys
    assert len(edge_data_friend) == 2


def test_save_and_load_graph(tmp_path):
    """Graph serialized to GraphML should survive a round-trip."""
    state = GraphState(
        known_characters=[
            Character(name="Miss Marple", aliases=["Marple"], description="Amateur sleuth"),
        ],
        known_relationships=[
            Relationship(source="Miss Marple", target="Inspector Craddock", nature="ally"),
        ],
    )

    G = build_networkx_graph(state)
    filepath = os.path.join(str(tmp_path), "graphs", "test.graphml")

    save_graph(G, filepath)
    assert os.path.isfile(filepath)

    loaded = load_graph(filepath)
    assert isinstance(loaded, nx.MultiDiGraph)
    assert loaded.number_of_nodes() == 2
    assert loaded.number_of_edges() == 1
    assert loaded.has_node("Miss Marple")
    assert loaded.nodes["Miss Marple"]["aliases"] == "Marple"
    assert loaded.nodes["Miss Marple"]["description"] == "Amateur sleuth"