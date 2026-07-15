from datetime import datetime

import asyncpg
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.db import get_pool

router = APIRouter()


class DocumentSummary(BaseModel):
    source_path: str
    version: int
    ingested_at: datetime
    status: str


@router.get("/api/documents", response_model=list[DocumentSummary])
async def list_documents(pool: asyncpg.Pool = Depends(get_pool)) -> list[DocumentSummary]:
    rows = await pool.fetch(
        "SELECT source_path, latest_version AS version, ingested_at, status FROM documents ORDER BY source_path"
    )
    return [DocumentSummary(**row) for row in rows]
