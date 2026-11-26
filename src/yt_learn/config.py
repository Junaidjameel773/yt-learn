"""Application settings read from environment variables and `.env`."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Empty values (e.g. `LLM_MODEL=` in .env) fall back to the defaults below.
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    llm_provider: Literal["gemini", "openai"] = "gemini"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    llm_model: str | None = None
    data_dir: Path = Path("./data")
    api_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings (loaded once)."""
    return Settings()
