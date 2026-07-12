import networkx as nx

from backend.core.exporter import export_to_cytoscape_json


def test_export_to_cytoscape_json():
    G = nx.MultiDiGraph()
    G.add_node("Poirot", aliases="Hercule Poirot", description="Belgian detective")
    G.add_node("Hastings", aliases="Captain Hastings", description="Poirot's friend")
    G.add_edge("Poirot", "Hastings", nature="friend", weight=2)

    result = export_to_cytoscape_json(G)

    assert "nodes" in result
    assert "edges" in result
    assert len(result["nodes"]) == 2
    assert len(result["edges"]) == 1

    # Check node structure
    node_poirot = result["nodes"][0]
    assert node_poirot["data"]["id"] == "Poirot"
    assert node_poirot["data"]["label"] == "Poirot"
    assert node_poirot["data"]["aliases"] == "Hercule Poirot"
    assert node_poirot["data"]["description"] == "Belgian detective"

    # Check edge structure
    edge = result["edges"][0]
    assert edge["data"]["source"] == "Poirot"
    assert edge["data"]["target"] == "Hastings"
    assert edge["data"]["nature"] == "friend"
    assert edge["data"]["weight"] == 2
    # Verify the nested "data" key pattern is strict
    assert set(edge.keys()) == {"data"}
    assert set(node_poirot.keys()) == {"data"}

    # Check unique edge ID format
    assert edge["data"]["id"] == "Poirot_Hastings_0"