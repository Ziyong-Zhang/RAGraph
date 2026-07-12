from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str

    LANGCHAIN_TRACING_V2: str | None = None
    LANGCHAIN_API_KEY: str | None = None
    LANGCHAIN_PROJECT: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


class PipelineConfigModel(BaseModel):
    chunk_size: int = 2000
    chunk_overlap: int = 200
    max_chunks_limit: int | None = None
    books_dir: str = "data/raw/books"
    output_dir: str = "data/raw/output"


class PipelineConfig(BaseModel):
    pipeline: PipelineConfigModel


@lru_cache
def get_pipeline_config() -> PipelineConfigModel:
    config_path = Path(__file__).resolve().parent.parent.parent / "config.yaml"
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    parsed = PipelineConfig(**data)
    return parsed.pipeline