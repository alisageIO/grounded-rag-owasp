import hashlib
from collections import Counter

import asyncpg


def hash_content(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def classify(batch: dict[str, str], known_hashes: dict[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for source_path, content in batch.items():
        content_hash = hash_content(content)
        if source_path not in known_hashes:
            result[source_path] = "new"
        elif known_hashes[source_path] != content_hash:
            result[source_path] = "changed"
        else:
            result[source_path] = "unchanged"
    for source_path in known_hashes:
        if source_path not in batch:
            result[source_path] = "removed"
    return result


async def apply_ingest(pool: asyncpg.Pool, batch: dict[str, str]) -> dict[str, int]:
    rows = await pool.fetch("SELECT source_path, content_hash FROM documents")
    known_hashes = {row["source_path"]: row["content_hash"] for row in rows}
    classification = classify(batch, known_hashes)

    for source_path, label in classification.items():
        if label == "new":
            await pool.execute(
                "INSERT INTO documents (source_path, content_hash, latest_version, ingested_at, status) "
                "VALUES ($1, $2, 1, now(), 'active')",
                source_path,
                hash_content(batch[source_path]),
            )
        elif label == "changed":
            await pool.execute(
                "UPDATE documents SET content_hash = $1, latest_version = latest_version + 1, ingested_at = now() "
                "WHERE source_path = $2",
                hash_content(batch[source_path]),
                source_path,
            )
        # unchanged / removed: no write here — US-003/US-004 own those paths

    counts = {"new": 0, "changed": 0, "unchanged": 0, "removed": 0}
    counts.update(Counter(classification.values()))
    return counts
