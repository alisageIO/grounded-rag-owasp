import os

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("DATABASE_URL", "postgresql://rag:rag@localhost:5432/rag")
os.environ.setdefault("OPENAI_API_KEY", "sk-test")

from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
async def truncate_tables():
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    try:
        await conn.execute("TRUNCATE documents, chunks RESTART IDENTITY CASCADE")
    finally:
        await conn.close()
    yield


@pytest.fixture(autouse=True)
def stub_embedder(monkeypatch):
    async def _fake_embed(texts: list[str]) -> list[list[float]]:
        return [[0.0] * 1536 for _ in texts]

    monkeypatch.setattr("app.services.embedder.embed", _fake_embed)


@pytest.fixture
async def client():
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
