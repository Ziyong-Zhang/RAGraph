from pydantic import BaseModel


class Character(BaseModel):
    name: str
    aliases: list[str] = []
    description: str = ""


class Relationship(BaseModel):
    source: str
    target: str
    nature: str = ""


class GraphState(BaseModel):
    known_characters: list[Character] = []
    known_relationships: list[Relationship] = []


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    book_stem: str
    chapter_index: int
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    answer: str


class NodeMergeRequest(BaseModel):
    book_stem: str
    chapter_index: int | None = None
    source_id: str
    target_id: str


class EdgeDeleteRequest(BaseModel):
    book_stem: str
    chapter_index: int | None = None
    edge_id: str
