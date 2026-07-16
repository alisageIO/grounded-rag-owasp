from functools import lru_cache

from openai import AsyncOpenAI

from app.config import get_settings

EMBEDDING_MODEL = "text-embedding-3-small"


@lru_cache
def _client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=get_settings().openai_api_key)


async def embed(texts: list[str]) -> list[list[float]]:
    response = await _client().embeddings.create(input=texts, model=EMBEDDING_MODEL)
    return [item.embedding for item in sorted(response.data, key=lambda item: item.index)]
