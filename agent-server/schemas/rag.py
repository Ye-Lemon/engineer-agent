from typing import Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None
    top_k: int = Field(5, ge=1, le=20)
    collection_name: Optional[str] = None
    model: Optional[str] = Field(None, min_length=1, max_length=100)


class KnowledgeBaseRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
