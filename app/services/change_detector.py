import hashlib


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
