import asyncpg.pool
import pytest

from app.main import app
from app.services import change_detector, chunker


def _install_embed_spy(monkeypatch):
    calls: list[list[str]] = []

    async def _spy_embed(texts: list[str]) -> list[list[float]]:
        calls.append(list(texts))
        return [[0.0] * 1536 for _ in texts]

    monkeypatch.setattr("app.services.embedder.embed", _spy_embed)
    return calls


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

    chunk_count_after_first = await app.state.db.fetchval("SELECT count(*) FROM chunks")
    assert chunk_count_after_first > 0

    second = await client.post("/api/ingest", json=batch)
    assert second.status_code == 200
    assert second.json() == {"new": 0, "changed": 0, "unchanged": 2, "removed": 0}

    chunk_count_after_second = await app.state.db.fetchval("SELECT count(*) FROM chunks")
    assert chunk_count_after_second == chunk_count_after_first


async def test_unchanged_and_removed_items_never_call_embedder(client, monkeypatch):
    await _seed_document("known.md", "known content")

    async def _fail_embed(texts):
        raise AssertionError("embedder must not be called for unchanged/removed items")

    monkeypatch.setattr("app.services.embedder.embed", _fail_embed)

    unchanged_response = await client.post(
        "/api/ingest", json=[{"source_path": "known.md", "content": "known content"}]
    )
    assert unchanged_response.status_code == 200
    assert unchanged_response.json()["unchanged"] == 1

    removed_response = await client.post("/api/ingest", json=[])
    assert removed_response.status_code == 200
    assert removed_response.json()["removed"] == 1


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

    original_fetchrow = asyncpg.pool.Pool.fetchrow
    calls: list[str] = []

    async def _flaky_fetchrow(self, query, *args, **kwargs):
        calls.append(query)
        if len(calls) == 2:
            raise RuntimeError("simulated crash mid-batch")
        return await original_fetchrow(self, query, *args, **kwargs)

    monkeypatch.setattr(asyncpg.pool.Pool, "fetchrow", _flaky_fetchrow)

    with pytest.raises(RuntimeError):
        await change_detector.apply_ingest(app.state.db, batch)

    monkeypatch.setattr(asyncpg.pool.Pool, "fetchrow", original_fetchrow)

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


async def test_changing_one_document_embeds_only_that_document(client, monkeypatch):
    await _seed_document("a.md", "content a")
    await _seed_document("b.md", "content b")
    await _seed_document("c.md", "content c")

    calls = _install_embed_spy(monkeypatch)

    batch = [
        {"source_path": "a.md", "content": "content a"},
        {"source_path": "b.md", "content": "content b CHANGED"},
        {"source_path": "c.md", "content": "content c"},
    ]
    response = await client.post("/api/ingest", json=batch)

    assert response.json()["changed"] == 1
    assert len(calls) == 1
    assert calls[0] == ["content b CHANGED"]


async def _run_single_change_and_assert_one_call(client, monkeypatch, corpus_size: int) -> None:
    for i in range(corpus_size):
        await _seed_document(f"doc{i}.md", f"content {i}")

    calls = _install_embed_spy(monkeypatch)

    batch = [{"source_path": f"doc{i}.md", "content": f"content {i}"} for i in range(corpus_size)]
    batch[0]["content"] = "content 0 CHANGED"

    response = await client.post("/api/ingest", json=batch)

    assert response.json()["changed"] == 1
    assert len(calls) == 1


async def test_embedding_call_count_is_one_with_small_corpus(client, monkeypatch):
    await _run_single_change_and_assert_one_call(client, monkeypatch, corpus_size=5)


async def test_embedding_call_count_is_one_with_larger_corpus(client, monkeypatch):
    await _run_single_change_and_assert_one_call(client, monkeypatch, corpus_size=20)


async def test_new_documents_embedded_alongside_changed_document(client, monkeypatch):
    await _seed_document("existing.md", "existing content")
    await _seed_document("stable.md", "stable content")

    calls = _install_embed_spy(monkeypatch)

    batch = [
        {"source_path": "existing.md", "content": "existing content CHANGED"},
        {"source_path": "stable.md", "content": "stable content"},
        {"source_path": "brand-new.md", "content": "brand new content"},
    ]
    response = await client.post("/api/ingest", json=batch)

    assert response.json() == {"new": 1, "changed": 1, "unchanged": 1, "removed": 0}
    assert len(calls) == 2


async def test_all_documents_changed_simultaneously_all_reembedded(client, monkeypatch):
    for i in range(4):
        await _seed_document(f"doc{i}.md", f"content {i}")

    calls = _install_embed_spy(monkeypatch)

    batch = [{"source_path": f"doc{i}.md", "content": f"content {i} CHANGED"} for i in range(4)]
    response = await client.post("/api/ingest", json=batch)

    assert response.json()["changed"] == 4
    assert len(calls) == 4


async def test_larger_changed_document_only_changes_its_own_chunk_count(client):
    initial_batch = [
        {"source_path": "a.md", "content": "short content a"},
        {"source_path": "b.md", "content": "short content b"},
    ]
    await client.post("/api/ingest", json=initial_batch)

    doc_a_id = await app.state.db.fetchval("SELECT id FROM documents WHERE source_path = 'a.md'")
    doc_b_id = await app.state.db.fetchval("SELECT id FROM documents WHERE source_path = 'b.md'")

    a_chunk_count_before = await app.state.db.fetchval(
        "SELECT count(*) FROM chunks WHERE document_id = $1", doc_a_id
    )
    b_chunk_ids_before = {
        row["id"] for row in await app.state.db.fetch("SELECT id FROM chunks WHERE document_id = $1", doc_b_id)
    }
    assert a_chunk_count_before == 1

    larger_content_a = " ".join(f"word{i}" for i in range(500))
    update_batch = [
        {"source_path": "a.md", "content": larger_content_a},
        {"source_path": "b.md", "content": "short content b"},
    ]
    response = await client.post("/api/ingest", json=update_batch)
    assert response.json()["changed"] == 1

    # Tombstoning superseded chunks is US-004's job — the version-1 chunk row from the
    # initial ingest is still present, so total count is old + newly inserted version-2 chunks.
    a_chunk_count_after = await app.state.db.fetchval(
        "SELECT count(*) FROM chunks WHERE document_id = $1", doc_a_id
    )
    assert a_chunk_count_after == a_chunk_count_before + len(chunker.chunk(larger_content_a))

    a_new_version_chunk_count = await app.state.db.fetchval(
        "SELECT count(*) FROM chunks WHERE document_id = $1 AND version = 2", doc_a_id
    )
    assert a_new_version_chunk_count == len(chunker.chunk(larger_content_a))

    b_chunk_ids_after = {
        row["id"] for row in await app.state.db.fetch("SELECT id FROM chunks WHERE document_id = $1", doc_b_id)
    }
    assert b_chunk_ids_after == b_chunk_ids_before
