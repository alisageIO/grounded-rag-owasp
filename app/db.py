import asyncpg
from fastapi import Request


async def create_pool(database_url: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(database_url)


def get_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db
