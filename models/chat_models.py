from pydantic import BaseModel

class ChatInfo(BaseModel):
    chat_id: str
