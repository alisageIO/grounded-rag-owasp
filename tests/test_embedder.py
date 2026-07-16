from types import SimpleNamespace

from app.services import embedder

# Captured at collection time, before conftest's autouse `stub_embedder` fixture
# monkeypatches `embedder.embed` per-test — these tests exercise the real implementation.
_real_embed = embedder.embed


class _FakeEmbeddings:
    def __init__(self, response):
        self._response = response
        self.calls: list[dict] = []

    async def create(self, *, input, model):
        self.calls.append({"input": input, "model": model})
        return self._response


class _FakeClient:
    def __init__(self, response):
        self.embeddings = _FakeEmbeddings(response)


def _response(vectors_by_index: dict[int, list[float]]):
    data = [
        SimpleNamespace(embedding=vector, index=index)
        for index, vector in vectors_by_index.items()
    ]
    return SimpleNamespace(data=data)


async def test_embed_calls_openai_with_texts_and_model(monkeypatch):
    fake_client = _FakeClient(_response({0: [0.1, 0.2], 1: [0.3, 0.4]}))
    monkeypatch.setattr(embedder, "_client", lambda: fake_client)

    result = await _real_embed(["a", "b"])

    assert fake_client.embeddings.calls == [{"input": ["a", "b"], "model": "text-embedding-3-small"}]
    assert result == [[0.1, 0.2], [0.3, 0.4]]


async def test_embed_returns_vectors_in_input_order_even_if_response_is_out_of_order(monkeypatch):
    fake_client = _FakeClient(_response({1: [0.3, 0.4], 0: [0.1, 0.2]}))
    monkeypatch.setattr(embedder, "_client", lambda: fake_client)

    result = await _real_embed(["a", "b"])

    assert result == [[0.1, 0.2], [0.3, 0.4]]
