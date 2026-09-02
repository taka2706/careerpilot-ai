# Dependency Decisions

## Runtime

- **FastAPI + Uvicorn** — typed HTTP API and server.
- **Pydantic + Pydantic Settings** — structured contracts and environment configuration.
- **SQLAlchemy** — persistence abstraction for SQLite now and PostgreSQL later.
- **Streamlit + HTTPX** — portfolio dashboard and timeout-aware backend calls.
- **python-multipart + pypdf** — validated form uploads and in-memory PDF text extraction.
- **FAISS CPU + NumPy** — modular local vector search without an embedding API.
- **LangGraph + LangChain Core** — explicit typed graph nodes and conditional routing.
- **OpenAI SDK** — optional Responses API structured output behind a local interface.
- **Tenacity** — bounded exponential retry for transient LLM failures.

## Development

- **pytest + pytest-asyncio + pytest-cov** — offline unit and integration testing.
- **Ruff** — formatting and linting.
- **mypy** — strict backend type checking.

## Intentionally deferred

- **Alembic and PostgreSQL driver** — useful when a deployed database and schema migrations
  are introduced.
- **Celery/Redis or another queue** — useful when workflows move from synchronous demo runs
  to production background jobs.
- **Hosted embedding libraries** — unnecessary for the deterministic offline portfolio demo.

The project requires Python 3.12+ because the current FAISS/NumPy type ecosystem and CI image
are aligned on Python 3.12.
