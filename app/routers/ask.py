from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class AskRequest(BaseModel):
    question: str


class Citation(BaseModel):
    source: str
    chunk_id: int
    version: int
    snippet: str


class AskResponse(BaseModel):
    answer: str | None
    citations: list[Citation]
    grounding: Literal["grounded", "not_found"]


@router.get("/api/ask", response_model=AskResponse)
async def ask(question: str) -> AskResponse:
    raise HTTPException(status_code=501, detail="not implemented — Epic 7B")
