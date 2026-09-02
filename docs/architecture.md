# Architecture

CareerPilot AI separates HTTP concerns, business logic, persistence, AI orchestration,
retrieval, and presentation. Each layer communicates through typed schemas.

```mermaid
flowchart LR
    UI[Streamlit UI] --> API[FastAPI]
    API --> Services[Application services]
    Services --> DB[(SQLite / PostgreSQL)]
    Services --> Graph[LangGraph workflow - Phase 4]
    Graph --> Tools[Job and profile tools]
    Tools --> RAG[Profile RAG - Phase 2]
```

The `agents`, `rag`, `tools`, and `evaluation` packages are intentional extension points.
They remain small until their implementation phases so the project stays runnable.

