# Software Intelligence Platform

Adaptive RAG-powered software expertise, delivered as a desktop application.

## Architecture

See `docs/` for the full Phase 1–10 architecture specifications.

## Development Setup

```bash
# Install uv (https://docs.astral.sh/uv/)
# Then install the project with dev dependencies:
uv sync --extra dev

# Run tests
uv run pytest

# Lint + format
uv run ruff check src tests
uv run ruff format src tests

# Type check
uv run mypy src
```

## Project Structure

```
src/sip/
├── core/           # Foundation: errors, logging, config
├── rag/            # Adaptive RAG engine (Phase 3)
├── knowledge/      # Storage contracts + repositories (Phase 4)
├── ingestion/      # Knowledge crawling + ingestion (Phase 5)
├── experts/        # Expert system + lifecycle (Phase 6)
├── llm/            # LLM Gateway + provider adapters (Phase 7)
├── agents/         # Agent Runtime (Phase 7)
├── tools/          # Tool Registry + execution (Phase 7)
├── api/            # FastAPI application (Phase 8)
├── evaluation/     # Benchmarking + metrics (Phase 9)
├── observability/  # Tracing + OpenTelemetry (Phase 9)
└── security/       # Auth, authorization, secrets (Phase 10)
```
