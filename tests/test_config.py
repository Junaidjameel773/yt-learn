from pathlib import Path

import pytest
from pydantic import ValidationError

from yt_learn.config import Settings

ENV_VARS = [
    "LLM_PROVIDER",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "LLM_MODEL",
    "DATA_DIR",
    "API_URL",
    "TRANSCRIPT_LANGUAGES",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)  # no stray .env from the repo


def test_defaults() -> None:
    s = Settings()
    assert s.llm_provider == "gemini"
    assert s.gemini_api_key == ""
    assert s.openai_api_key == ""
    assert s.llm_model is None
    assert s.data_dir == Path("./data")
    assert s.api_url == "http://localhost:8000"
    assert s.transcript_languages == ["en"]


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("DATA_DIR", "/tmp/yt")
    monkeypatch.setenv("API_URL", "http://api:8000")
    s = Settings()
    assert s.llm_provider == "openai"
    assert s.openai_api_key == "sk-test"
    assert s.llm_model == "gpt-4o-mini"
    assert s.data_dir == Path("/tmp/yt")
    assert s.api_url == "http://api:8000"


def test_dotenv_file(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("GEMINI_API_KEY=abc\nLLM_MODEL=\n")
    s = Settings()
    assert s.gemini_api_key == "abc"
    assert s.llm_model is None


def test_invalid_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "claude")
    with pytest.raises(ValidationError):
        Settings()
