async def test_list_documents_empty(client):
    response = await client.get("/api/documents")
    assert response.status_code == 200
    assert response.json() == []
