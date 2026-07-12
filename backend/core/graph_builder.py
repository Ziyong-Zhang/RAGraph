import os

import networkx as nx

from backend.core.models import GraphState


def build_networkx_graph(state: GraphState) -> nx.MultiDiGraph:
    """Build a MultiDiGraph from a GraphState.

    Node attributes store 'aliases' (comma-separated string) and 'description'.
    Multi-edges between the same (source, target) with the same 'nature' are
    collapsed and their weight is accumulated.
    """
    G = nx.MultiDiGraph()

    for character in state.known_characters:
        G.add_node(
            character.name,
            aliases=", ".join(character.aliases),
            description=character.description,
        )

    for rel in state.known_relationships:
        edge_found = False
        for key, edge_data in G.get_edge_data(rel.source, rel.target, default={}).items():
            if edge_data.get("nature") == rel.nature:
                G.add_edge(rel.source, rel.target, key=key, nature=rel.nature, weight=edge_data.get("weight", 1) + 1)
                edge_found = True
                break
        if not edge_found:
            G.add_edge(rel.source, rel.target, nature=rel.nature, weight=1)

    return G


def save_graph(G: nx.MultiDiGraph, filepath: str) -> None:
    """Serialize the graph to GraphML format at the given filepath."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    nx.write_graphml(G, filepath)


def load_graph(filepath: str) -> nx.MultiDiGraph:
    """Load a graph from a GraphML file."""
    return nx.MultiDiGraph(nx.read_graphml(filepath))
