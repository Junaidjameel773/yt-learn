# CLAUDE.md

Guidance for AI coding assistants working in this repository.

## Project

yt-learn: YouTube learning assistant. Python 3.11+, uv, FastAPI backend (`src/yt_learn/`),
Streamlit UI, Gemini/OpenAI for generation. Tests in `tests/`.

## Commands

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## Rules

1. Only work on public repositories owned by `Junaidjameel773`. Never read, modify, push to, or
   otherwise touch any private repository.
2. One issue per PR. The PR description must contain `Closes #N` for that issue.
3. Tests and lint must pass before opening or merging a PR (`ruff check`, `ruff format --check`,
   `pytest`).
4. When a feature ships, update the README Features table status and the API table.
5. No AI attribution anywhere: no `Co-Authored-By` trailers, no "Generated with" lines, no mention
   of AI tools as author or contributor in commits, PRs, issues, or code.
6. Keep code simple. Prefer the standard library and existing dependencies; no speculative
   abstractions.
