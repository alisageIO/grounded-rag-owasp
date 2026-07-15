# Stage 7 — Retrieval-Grounded Answering with Citations

RAG service over the OWASP Cheat Sheet Series with idempotent freshness-aware ingestion and structural abstention. Full spec: [docs/TRD.md](docs/TRD.md).

## Local development

```bash
uv sync
cp .env.example .env   # fill in OPENAI_API_KEY

docker compose up -d postgres
uv run uvicorn app.main:app --reload
```

`GET /api/documents` is live. `POST /api/ingest` and `GET /api/ask` return `501` coming soon.

## Tests

```bash
uv run pytest
```

Requires the compose Postgres running (`docker compose up -d postgres`).
