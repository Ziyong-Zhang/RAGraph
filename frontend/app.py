import json
import urllib.parse

import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="RAGraph")

st.title("RAGraph - Character Relationship Visualizer")

# ---- Sidebar ----
st.sidebar.header("Book Selection")

# Fetch available graphs from backend
try:
    resp_graphs = requests.get("http://localhost:8000/api/v1/graphs", timeout=5)
    available_stems = resp_graphs.json() if resp_graphs.status_code == 200 else []
except requests.exceptions.ConnectionError:
    available_stems = []

if not available_stems:
    st.sidebar.warning("No processed graphs found. Run `uv run python scripts/run_integration.py` first.")
    selected_stem = st.sidebar.text_input(
        "Book stem (filename without extension)",
        value="",
        help="Enter the stem of the EPUB file manually.",
    )
else:
    selected_stem = st.sidebar.selectbox(
        "Select a processed book",
        options=available_stems,
        index=0 if available_stems else None,
    )

st.session_state["selected_stem"] = selected_stem

# ---- Chapter Timeline (only when a book is selected) ----
chapter_indices = []
if selected_stem:
    safe_stem = urllib.parse.quote(selected_stem)
    try:
        resp_meta = requests.get(
            f"http://localhost:8000/api/v1/graph/{safe_stem}/metadata",
            timeout=5,
        )
        if resp_meta.status_code == 200:
            meta = resp_meta.json()
            chapter_indices = meta.get("available_chapters", [])
    except requests.exceptions.ConnectionError:
        pass

if chapter_indices:
    default_chapter = chapter_indices[-1]
    selected_chapter = st.sidebar.select_slider(
        "Chapter Timeline",
        options=chapter_indices,
        value=default_chapter,
        help="Drag to view the character relationship graph at the end of a specific chapter.",
    )
    st.session_state["selected_chapter"] = selected_chapter
else:
    st.session_state["selected_chapter"] = None


# ---- Cached Graph Fetcher ----
@st.cache_data
def fetch_graph(book_stem: str, chapter_index: int | None) -> dict | None:
    """Fetch graph data from backend. Cached to avoid duplicate requests."""
    safe_stem = urllib.parse.quote(book_stem)
    base_url = f"http://localhost:8000/api/v1/graph/{safe_stem}"
    try:
        if chapter_index is not None:
            resp = requests.get(base_url, params={"chapter_index": chapter_index}, timeout=10)
        else:
            resp = requests.get(base_url, timeout=10)
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Is the FastAPI server running on port 8000?")
        return None

    if resp.status_code == 404:
        st.warning(
            "Graph data not found. Please process the EPUB file first by running:\n\n"
            "`uv run python scripts/run_integration.py`\n\n"
            "Then reload this page."
        )
        return None

    if resp.status_code != 200:
        st.error(f"Backend returned status {resp.status_code}: {resp.text}")
        return None

    try:
        data = resp.json()
        return data
    except requests.exceptions.JSONDecodeError as e:
        st.error(f"Failed to parse JSON response: {e}")
        return None


# ---- Auto-update graph on slider change (no button needed) ----
book_stem = st.session_state.get("selected_stem")
chapter = st.session_state.get("selected_chapter")

if book_stem and chapter is not None:
    data = fetch_graph(book_stem, chapter)
    if data:
        st.session_state["graph_data"] = data
        st.sidebar.success(f"Loaded: {len(data.get('nodes', []))} nodes, {len(data.get('edges', []))} edges")
elif book_stem and not chapter_indices:
    # No chapters — load final graph
    data = fetch_graph(book_stem, None)
    if data:
        st.session_state["graph_data"] = data
elif not book_stem:
    if "graph_data" in st.session_state:
        del st.session_state["graph_data"]

# ---- Render Graph ----
if "graph_data" in st.session_state and st.session_state["graph_data"]:
    # Use json.dumps for safe JavaScript object literal injection
    # This guarantees any apostrophe or special char is safely escaped
    safe_json = json.dumps(st.session_state["graph_data"])

    cytoscape_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
        <style>
            body {{ margin: 0; padding: 0; font-family: sans-serif; }}
            #cy {{
                width: 100%;
                height: 700px;
                background-color: #f5f7fa;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            #info-panel {{
                position: absolute;
                top: 15px;
                right: 15px;
                background: rgba(255, 255, 255, 0.95);
                padding: 16px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                width: 320px;
                display: none;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                line-height: 1.5;
                z-index: 1000;
                pointer-events: auto;
            }}
            #info-panel h3 {{
                margin: 0 0 8px 0;
                color: #2c5f8a;
                border-bottom: 2px solid #4a90d9;
                padding-bottom: 6px;
            }}
            #info-panel .label {{
                font-weight: 600;
                color: #555;
            }}
            #info-panel .value {{
                color: #333;
                margin-bottom: 8px;
            }}
            #info-panel .missing {{
                color: #999;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div id="info-panel"></div>
        <div id="cy"></div>
        <script>
            var graphData = {safe_json};
            var cy = cytoscape({{
                container: document.getElementById('cy'),
                elements: graphData,
                style: [
                    {{
                        selector: 'node',
                        style: {{
                            'label': 'data(label)',
                            'background-color': '#4a90d9',
                            'color': '#222',
                            'font-size': '13px',
                            'font-weight': 'bold',
                            'text-valign': 'bottom',
                            'text-halign': 'center',
                            'text-margin-y': 4,
                            'width': 45,
                            'height': 45,
                            'border-width': 2,
                            'border-color': '#2c5f8a'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 'mapData(weight, 1, 10, 1, 6)',
                            'line-color': '#999',
                            'target-arrow-color': '#999',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'label': 'data(nature)',
                            'font-size': '10px',
                            'text-rotation': 'autorotate',
                            'color': '#666',
                            'edge-text-rotation': 'autorotate'
                        }}
                    }}
                ],
                layout: {{
                    name: 'cose',
                    idealEdgeLength: 100,
                    nodeOverlap: 20,
                    refresh: 20,
                    fit: true,
                    padding: 30,
                    randomize: false,
                    componentSpacing: 100,
                    nodeRepulsion: 400000,
                    edgeElasticity: 100
                }}
            }});

            var infoPanel = document.getElementById('info-panel');

            function showPanel(html) {{
                infoPanel.innerHTML = html;
                infoPanel.style.display = 'block';
            }}

            cy.on('tap', 'node', function(evt) {{
                var node = evt.target;
                var name = node.data('label') || node.data('id');
                var aliases = node.data('aliases');
                var description = node.data('description');

                var aliasesHtml = aliases && aliases.trim()
                    ? '<div class="value">' + aliases + '</div>'
                    : '<div class="value missing">(none)</div>';
                var descHtml = description && description.trim()
                    ? '<div class="value">' + description + '</div>'
                    : '<div class="value missing">(none)</div>';

                showPanel(
                    '<h3><span class="label">Character</span>: ' + name + '</h3>' +
                    '<div><span class="label">Aliases:</span></div>' + aliasesHtml +
                    '<div><span class="label">Description:</span></div>' + descHtml
                );
            }});

            cy.on('tap', 'edge', function(evt) {{
                var edge = evt.target;
                var source = edge.data('source');
                var target = edge.data('target');
                var nature = edge.data('nature') || '(unspecified)';
                var weight = edge.data('weight') || 1;

                showPanel(
                    '<h3>Relationship</h3>' +
                    '<div><span class="label">Source:</span> ' + source + '</div>' +
                    '<div><span class="label">Target:</span> ' + target + '</div>' +
                    '<div><span class="label">Nature:</span> ' + nature + '</div>' +
                    '<div><span class="label">Weight (occurrences):</span> ' + weight + '</div>'
                );
            }});

            cy.on('tap', function(evt) {{
                if (evt.target === cy) {{
                    infoPanel.style.display = 'none';
                }}
            }});
        </script>
    </body>
    </html>
    """

    st.components.v1.html(cytoscape_html, height=720)

    with st.expander("Show raw JSON data"):
        st.json(st.session_state["graph_data"])
else:
    st.info("Select a book stem in the sidebar and drag the chapter slider to visualize character relationships.")