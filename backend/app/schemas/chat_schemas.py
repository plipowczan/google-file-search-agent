from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    store_id: int
    message: str
    model: Optional[str] = "gemini-2.5-flash"

class ChatResponse(BaseModel):
    response: str
    citations: Optional[List[str]] = []
