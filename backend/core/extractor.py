from openai import AsyncOpenAI
import instructor
from langsmith import traceable

from backend.core.models import GraphState

EXTRACTOR_SYSTEM_PROMPT = (
    "You are an expert literary analyst extracting structured knowledge from text.\n"
    "Your goal is to identify Characters and their Relationships from the provided text.\n\n"
    "CRITICAL RULES FOR GRAPH MERGING:\n"
    "1. Look at the `current_state` provided by the user.\n"
    "2. If a character in the text already exists in `current_state.known_characters` "
    "(even by a different alias or pronoun), DO NOT create a new character. Instead, "
    "update the existing character's `aliases` and `description`.\n"
    "3. If a character is entirely new, add them to the list.\n"
    "4. Extract relationships between characters (e.g., 'friend', 'enemy', 'employer').\n\n"
    "STRICT ALIAS RULES:\n"
    "- An alias MUST ONLY be a proper noun, an alternative formal name, a nickname, "
    "or a Title + Surname combination (e.g., 'Mrs. Crale', 'Poirot', 'Captain Hastings').\n"
    "- NEVER extract relational roles, pronouns, or generic identifiers as aliases. "
    "Words like 'mother', 'wife', 'brother', 'that man' are strictly FORBIDDEN "
    "in the aliases list. Put relationship information in the `description`.\n"
    "- If a female character is referred to by her husband's surname with a title "
    "(e.g., 'Mrs. Crale'), you MUST explicitly include that title+surname form "
    "in her aliases list.\n\n"
    "WARNING — Name Inheritance in Agatha Christie Novels:\n"
    "In Agatha Christie stories, characters from different generations often share the "
    "same or very similar names (e.g., a mother and daughter both named Caroline, "
    "or a character inheriting a parent's married name after marriage).\n"
    "- Do NOT list a younger generation's name as an alias for an older generation "
    "character unless they are verified to be the exact same physical person.\n"
    "- Keep distinct generations as separate entities with precise description "
    "differences (e.g., 'Caroline Crale (mother)' vs 'Carla Lemarchant (daughter)').\n\n"
    "Return the COMPLETE, updated GraphState containing both the old (merged) and new entities."
)

@traceable(run_type="llm", name="DeepSeek_Entity_Extraction")
async def extract_entities(
    text_chunk: str,
    current_state: GraphState,
    api_key: str,
) -> GraphState:
    client = instructor.from_openai(
        AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1"),
        mode=instructor.Mode.JSON,
    )

    result = await client.chat.completions.create(
        model="deepseek-chat",
        response_model=GraphState,
        messages=[
            {"role": "system", "content": EXTRACTOR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Text chunk:\n{text_chunk}\n\n"
                    f"Current state:\n{current_state.model_dump_json(indent=2)}"
                ),
            },
        ],
    )

    return result