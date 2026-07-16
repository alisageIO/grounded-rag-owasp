import asyncpg
from fastapi import Request
from pgvector.asyncpg import register_vector


async def create_pool(database_url: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(database_url, init=register_vector)


def get_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db
