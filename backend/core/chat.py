"""Anti-Spoiler Chat Engine.

Reads the graph snapshot JSON for a given book/chapter, injects it into a
rigid system prompt, and calls the DeepSeek API. The LLM is constrained to
only answer based on the injected graph data, preventing spoilers.
"""

import json
from pathlib import Path

from openai import AsyncOpenAI

from backend.core.config import get_pipeline_config
from backend.core.models import ChatRequest


CHAT_SYSTEM_PROMPT_TEMPLATE = (
    "You are an expert assistant strictly analyzing an Agatha Christie novel "
    "based ONLY on the provided JSON graph.\n\n"
    "CONSTRAINT 1 (Anti-Spoiler): The injected JSON represents the absolute "
    "limit of the reader's current knowledge. DO NOT spoil future events, "
    "identities, or twists.\n\n"
    "CONSTRAINT 2 (Handling Unknowns): If the user asks a question (e.g., "
    "'Who is the murderer?') and the answer cannot be explicitly deduced "
    "from the JSON nodes or edges, you MUST reply naturally that based on "
    "the current clues, this remains a mystery. Do not guess.\n\n"
    "Current Knowledge Graph:\n{graph_json}"
)


def _load_graph_json(book_stem: str, chapter_index: int) -> str | None:
    """Load the graph JSON file for the given book and chapter.

    Tries the chapter-specific file first, then falls back to _final.json.
    Returns the raw JSON string, or None if neither file exists.
    """
    pipeline_cfg = get_pipeline_config()
    project_root = Path(__file__).resolve().parent.parent.parent
    output_dir = project_root / pipeline_cfg.output_dir

    # Try chapter-specific file
    chapter_path = output_dir / f"{book_stem}_chapter_{chapter_index}.json"
    if chapter_path.is_file():
        return chapter_path.read_text(encoding="utf-8")

    # Fall back to final graph
    final_path = output_dir / f"{book_stem}_final.json"
    if final_path.is_file():
        return final_path.read_text(encoding="utf-8")

    return None


async def generate_chat_response(request: ChatRequest, api_key: str) -> str:
    """Generate an anti-spoiler-aware chat response based on graph snapshot."""
    graph_json = _load_graph_json(request.book_stem, request.chapter_index)
    if graph_json is None:
        return "Graph data not found."

    system_prompt = CHAT_SYSTEM_PROMPT_TEMPLATE.format(graph_json=graph_json)

    openai_messages = [{"role": "system", "content": system_prompt}]
    for msg in request.messages:
        openai_messages.append({"role": msg.role, "content": msg.content})

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
    )

    result = await client.chat.completions.create(
        model="deepseek-chat",
        messages=openai_messages,
    )

    return result.choices[0].message.content or ""