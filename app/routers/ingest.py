import asyncpg
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.db import get_pool
from app.services import change_detector

router = APIRouter()


class IngestItem(BaseModel):
    source_path: str
    content: str


class IngestCounts(BaseModel):
    new: int
    changed: int
    unchanged: int
    removed: int


@router.post("/api/ingest", response_model=IngestCounts)
async def ingest(items: list[IngestItem], pool: asyncpg.Pool = Depends(get_pool)) -> IngestCounts:
    batch = {item.source_path: item.content for item in items}
    counts = await change_detector.apply_ingest(pool, batch)
    return IngestCounts(**counts)
