import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph

from backend.core.chunker import chunk_text
from backend.core.extractor import extract_entities
from backend.core.graph_builder import build_networkx_graph, save_graph
from backend.core.models import GraphState
from backend.core.parsers import EpubParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class PipelineState(TypedDict):
    filepath: str
    text_chunks: list[str]
    current_chunk_index: int
    graph_memory: GraphState
    output_graph_path: str
    api_key: str
    max_chunks: int | None


def initialize_document(state: PipelineState) -> dict:
    """Parse the EPUB, chunk the text, and initialize the rolling memory."""
    logger.info("Initializing document: %s", state["filepath"])
    parser = EpubParser()
    raw_text = parser.extract_text(state["filepath"])
    chunks = chunk_text(raw_text)
    logger.info("Extracted %d text chunks from document", len(chunks))

    return {
        "text_chunks": chunks,
        "graph_memory": GraphState(),
        "current_chunk_index": 0,
    }


async def process_single_chunk(state: PipelineState) -> dict:
    """Process one chunk, merge into graph memory, and advance the index."""
    idx = state["current_chunk_index"]
    total = len(state["text_chunks"])
    logger.info("Processing chunk %d / %d", idx + 1, total)

    chunk = state["text_chunks"][idx]
    new_state = await extract_entities(
        text_chunk=chunk,
        current_state=state["graph_memory"],
        api_key=state["api_key"],
    )
    logger.info(
        "Chunk %d complete: %d characters, %d relationships found so far",
        idx + 1,
        len(chunk),
        len(new_state.known_relationships),
    )

    return {
        "graph_memory": new_state,
        "current_chunk_index": idx + 1,
    }


def finalize_graph(state: PipelineState) -> dict:
    """Build the NetworkX graph from the accumulated memory and save it."""
    logger.info("Finalizing graph -> %s", state["output_graph_path"])
    G = build_networkx_graph(state["graph_memory"])
    save_graph(G, state["output_graph_path"])
    logger.info("Graph saved successfully (%d nodes)", G.number_of_nodes())
    return {}


def check_next_chunk(state: PipelineState) -> str:
    """Route to the next chunk processor, or finalize if all chunks done or limit reached."""
    # Circuit breaker: respect max_chunks_limit if set
    limit = state.get("max_chunks")
    if limit is not None and state["current_chunk_index"] >= limit:
        logger.info("Circuit breaker hit: max_chunks=%d reached", limit)
        return "finalize_graph"

    if state["current_chunk_index"] < len(state["text_chunks"]):
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