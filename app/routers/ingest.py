from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

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
async def ingest(items: list[IngestItem]) -> IngestCounts:
    raise HTTPException(status_code=501, detail="not implemented — Epic 7A")
