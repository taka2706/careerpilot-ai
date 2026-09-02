# Dependency plan

## Phase 1 runtime

- **FastAPI + Uvicorn** — typed HTTP API and development server.
- **Pydantic + Pydantic Settings** — request validation and environment configuration.
- **SQLAlchemy** — database abstraction compatible with SQLite now and PostgreSQL later.
- **Streamlit** — lightweight portfolio dashboard.
- **HTTPX** — timeout-aware communication from the dashboard to the API.
- **pytest, Ruff, mypy** — tests, linting, formatting checks, and static type checking.

## Deferred until the feature needs them

- **LangGraph and an OpenAI-compatible client** — agent workflow and LLM calls (Phase 4).
- **pypdf** — PDF text extraction (Phase 2).
- **ChromaDB or FAISS plus an embedding client** — profile retrieval (Phase 2, after a
  small interface is defined).
- **Alembic and a PostgreSQL driver** — migrations and production database support
  (deployment preparation).

Deferring unused libraries keeps installation fast and makes each phase easier to debug.

