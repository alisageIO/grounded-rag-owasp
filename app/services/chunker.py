def chunk(content: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    words = content.split()
    if not words:
        return []
    pieces: list[str] = []
    step = chunk_size - overlap
    start = 0
    while start < len(words):
        pieces.append(" ".join(words[start : start + chunk_size]))
        if start + chunk_size >= len(words):
            break
        start += step
    return pieces
