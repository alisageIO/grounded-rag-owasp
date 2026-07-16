import asyncpg.pool
import pytest

from app.main import app
from app.services import change_detector


async def _seed_document(source_path: str, content: str, latest_version: int = 1) -> None:
    await app.state.db.execute(
        "INSERT INTO documents (source_path, content_hash, latest_version, ingested_at, status) "
        "VALUES ($1, $2, $3, now(), 'active')",
        source_path,
        change_detector.hash_content(content),
        latest_version,
    )


async def test_idempotent_reingest_is_a_noop_on_second_run(client):
    batch = [
        {"source_path": "a.md", "content": "content a"},
        {"source_path": "b.md", "content": "content b"},
    ]

    first = await client.post("/api/ingest", json=batch)
    assert first.status_code == 200
    assert first.json() == {"new": 2, "changed": 0, "unchanged": 0, "removed": 0}

    second = await client.post("/api/ingest", json=batch)
    assert second.status_code == 200
    assert second.json() == {"new": 0, "changed": 0, "unchanged": 2, "removed": 0}

    chunk_count = await app.state.db.fetchval("SELECT count(*) FROM chunks")
    assert chunk_count == 0


async def test_ingest_never_calls_embedder(client, monkeypatch):
    async def _fail_embed(texts):
        raise AssertionError("embedder must not be called by /api/ingest")

    monkeypatch.setattr("app.services.embedder.embed", _fail_embed)

    response = await client.post("/api/ingest", json=[{"source_path": "a.md", "content": "content a"}])

    assert response.status_code == 200


async def test_response_counts_match_batch_composition(client):
    await _seed_document("existing.md", "old content")

    batch = [
        {"source_path": "existing.md", "content": "new content"},
        {"source_path": "new.md", "content": "brand new"},
    ]

    response = await client.post("/api/ingest", json=batch)

    assert response.json() == {"new": 1, "changed": 1, "unchanged": 0, "removed": 0}


async def test_mixed_new_and_unchanged_batch_leaves_unchanged_row_untouched(client):
    await _seed_document("known.md", "known content")

    before = await app.state.db.fetchrow(
        "SELECT content_hash, ingested_at FROM documents WHERE source_path = $1", "known.md"
    )

    batch = [
        {"source_path": "known.md", "content": "known content"},
        {"source_path": "fresh.md", "content": "fresh content"},
    ]
    response = await client.post("/api/ingest", json=batch)

    assert response.json() == {"new": 1, "changed": 0, "unchanged": 1, "removed": 0}

    after = await app.state.db.fetchrow(
        "SELECT content_hash, ingested_at FROM documents WHERE source_path = $1", "known.md"
    )
    assert after["content_hash"] == before["content_hash"]
    assert after["ingested_at"] == before["ingested_at"]


async def test_interrupted_batch_commits_completed_items_only(client, monkeypatch):
    await _seed_document("existing.md", "existing content")

    batch = {
        "one.md": "content one",
        "existing.md": "changed content",
        "three.md": "content three",
    }

    original_execute = asyncpg.pool.Pool.execute
    calls: list[str] = []

    async def _flaky_execute(self, query, *args, **kwargs):
        calls.append(query)
        if len(calls) == 2:
            raise RuntimeError("simulated crash mid-batch")
        return await original_execute(self, query, *args, **kwargs)

    monkeypatch.setattr(asyncpg.pool.Pool, "execute", _flaky_execute)

    with pytest.raises(RuntimeError):
        await change_detector.apply_ingest(app.state.db, batch)

    monkeypatch.setattr(asyncpg.pool.Pool, "execute", original_execute)

    rows = {row["source_path"] for row in await app.state.db.fetch("SELECT source_path FROM documents")}
    assert "one.md" in rows
    assert "three.md" not in rows


async def test_changed_item_bumps_version(client):
    await _seed_document("existing.md", "old content", latest_version=3)

    response = await client.post("/api/ingest", json=[{"source_path": "existing.md", "content": "new content"}])

    assert response.json()["changed"] == 1

    row = await app.state.db.fetchrow(
        "SELECT latest_version, content_hash FROM documents WHERE source_path = $1", "existing.md"
    )
    assert row["latest_version"] == 4
    assert row["content_hash"] == change_detector.hash_content("new content")


async def test_removed_item_reported_but_row_untouched(client):
    await _seed_document("gone.md", "content that disappears")

    response = await client.post("/api/ingest", json=[])

    assert response.json() == {"new": 0, "changed": 0, "unchanged": 0, "removed": 1}

    row = await app.state.db.fetchrow("SELECT status FROM documents WHERE source_path = $1", "gone.md")
    assert row["status"] == "active"
