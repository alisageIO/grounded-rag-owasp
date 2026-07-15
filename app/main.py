from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.db import create_pool
from app.routers import ask, documents, ingest


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.db = await create_pool(settings.database_url)
    yield
    await app.state.db.close()


app = FastAPI(title="Stage 7 — Retrieval-Grounded Answering with Citations", lifespan=lifespan)

app.include_router(ingest.router)
app.include_router(documents.router)
app.include_router(ask.router)
