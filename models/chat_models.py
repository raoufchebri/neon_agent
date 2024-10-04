from typing import Any, Dict, Optional
from pydantic import BaseModel

class ChatInfo(BaseModel):
    chat_id: str

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    action_result: Optional[Dict[str, Any]] = None

class NewChatResponse(BaseModel):
    chat_id: str