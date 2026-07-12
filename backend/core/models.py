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
    known_characters: list[str] = []
    known_relationships: list[Relationship] = []