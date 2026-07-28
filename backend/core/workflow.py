import json
import logging
import os
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, StateGraph

from backend.core.chunker import chunk_chapter_texts
from backend.core.entity_resolver import resolve_graph_state
from backend.core.exporter import export_to_cytoscape_json
from backend.core.extractor import extract_entities
from backend.core.graph_builder import build_networkx_graph, save_graph
from backend.core.models import GraphState
from backend.core.parsers import EpubParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class PipelineState(TypedDict):
    filepath: str
    chapter_chunks: list[tuple[str, int]]  # (text, chapter_index)
    current_chunk_index: int
    graph_memory: GraphState
    output_base_path: str  # directory for output files (no extension)
    api_key: str
    max_chunks: int | None


def initialize_document(state: PipelineState) -> dict:
    """Parse the EPUB by chapter, chunk each chapter, and initialize rolling memory."""
    logger.info("Initializing document: %s", state["filepath"])
    parser = EpubParser()
    chapter_texts = parser.extract_chapter_texts(state["filepath"])
    logger.info("Extracted %d chapters from document", len(chapter_texts))

    chunks = chunk_chapter_texts(chapter_texts)
    logger.info("Generated %d total chunks across all chapters", len(chunks))

    return {
        "chapter_chunks": chunks,
        "graph_memory": GraphState(),
        "current_chunk_index": 0,
    }


async def process_single_chunk(state: PipelineState) -> dict:
    """Process one chunk, merge into graph memory, snapshot chapter graph."""
    idx = state["current_chunk_index"]
    total = len(state["chapter_chunks"])
    chunk_text, chapter_idx = state["chapter_chunks"][idx]
    logger.info("Processing chunk %d / %d (chapter %d)", idx + 1, total, chapter_idx)

    new_state = await extract_entities(
        text_chunk=chunk_text,
        current_state=state["graph_memory"],
        api_key=state["api_key"],
    )

    # Apply deterministic entity resolution to merge duplicates before storing
    resolved = resolve_graph_state(new_state)
    logger.info(
        "Chunk %d complete: chapter %d, %d characters, %d relationships found so far "
        "(ER merged %d -> %d characters)",
        idx + 1,
        chapter_idx,
        len(chunk_text),
        len(resolved.known_relationships),
        len(new_state.known_characters),
        len(resolved.known_characters),
    )

    # Continuous Chapter Overwrite: build and save the snapshot for this chapter
    base_path = state["output_base_path"]
    G = build_networkx_graph(resolved)
    cytoscape_data = export_to_cytoscape_json(G)

    chapter_path = f"{base_path}_chapter_{chapter_idx}.json"
    with open(chapter_path, "w", encoding="utf-8") as f:
        json.dump(cytoscape_data, f, ensure_ascii=False, indent=2)
    logger.info("Chapter %d graph snapshot saved to %s", chapter_idx, chapter_path)

    return {
        "graph_memory": resolved,
        "current_chunk_index": idx + 1,
    }


def finalize_graph(state: PipelineState) -> dict:
    """Build the final NetworkX graph and save both GraphML and final JSON."""
    logger.info("Finalizing graph -> %s", state["output_base_path"])
    base_path = state["output_base_path"]

    # Apply entity resolution for final graph integrity
    resolved = resolve_graph_state(state["graph_memory"])
    G = build_networkx_graph(resolved)

    # Save GraphML
    graphml_path = base_path + "_graph.graphml"
    save_graph(G, graphml_path)
    logger.info("GraphML saved to %s (%d nodes)", graphml_path, G.number_of_nodes())

    # Save final Cytoscape JSON
    cytoscape_data = export_to_cytoscape_json(G)
    final_json_path = base_path + "_final.json"
    with open(final_json_path, "w", encoding="utf-8") as f:
        json.dump(cytoscape_data, f, ensure_ascii=False, indent=2)
    logger.info("Final JSON saved to %s", final_json_path)

    return {}


def check_next_chunk(state: PipelineState) -> str:
    """Route to the next chunk processor, or finalize if all chunks done or limit reached."""
    limit = state.get("max_chunks")
    if limit is not None and state["current_chunk_index"] >= limit:
        logger.info("Circuit breaker hit: max_chunks=%d reached", limit)
        return "finalize_graph"

    if state["current_chunk_index"] < len(state["chapter_chunks"]):
        return "process_single_chunk"

    logger.info("All chunks processed")
    return "finalize_graph"


# Build the LangGraph state machine
workflow = StateGraph(PipelineState)

workflow.add_node("initialize_document", initialize_document)
workflow.add_node("process_single_chunk", process_single_chunk)
workflow.add_node("finalize_graph", finalize_graph)

workflow.set_entry_point("initialize_document")

workflow.add_edge("initialize_document", "process_single_chunk")

workflow.add_conditional_edges(
    "process_single_chunk",
    check_next_chunk,
    {
        "process_single_chunk": "process_single_chunk",
        "finalize_graph": "finalize_graph",
    },
)

workflow.add_edge("finalize_graph", END)

ragraph_app = workflow.compile()