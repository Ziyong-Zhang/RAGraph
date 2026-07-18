import uuid

import networkx as nx


def export_to_cytoscape_json(G: nx.MultiDiGraph) -> dict:
    """Convert a NetworkX MultiDiGraph into a Cytoscape.js compatible JSON dict.

    Each node and edge is wrapped in a ``{"data": {...}}`` structure.
    Node attributes (aliases, description) are flattened into the data dict.
    Edge attributes (nature, weight) are flattened into the data dict.
    Every edge receives a globally unique UUID4 id to guarantee no Cytoscape.js
    crashes from duplicate IDs.
    """
    elements: dict[str, list[dict]] = {"nodes": [], "edges": []}

    for node_id, node_data in G.nodes(data=True):
        elements["nodes"].append({
            "data": {
                "id": node_id,
                "label": node_id,
                **node_data,
            }
        })

    for u, v, key, edge_data in G.edges(data=True, keys=True):
        elements["edges"].append({
            "data": {
                "id": str(uuid.uuid4()),
                "source": u,
                "target": v,
                **edge_data,
            }
        })

    return elements
