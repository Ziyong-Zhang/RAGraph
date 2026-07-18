import os
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


def init_observability(settings: Settings) -> None:
    """Synchronize LangSmith environment variables from Settings to os.environ.

    LangChain and LangSmith SDKs read configuration directly from os.environ
    at import time. pydantic-settings loads values into memory, but they are
    not propagated to os.environ. This function bridges that gap.
    Call early before any LangChain imports.
    """
    if settings.LANGCHAIN_TRACING_V2:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    if settings.LANGCHAIN_PROJECT:
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    init_observability(settings)
    return settings


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