from typing import List, Literal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ChatItem(BaseModel):
    id: UUID
    title: str


class ChatsResponse(BaseModel):
    chats: List[ChatItem]


class QueryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    query: str = Field(..., min_length=1, max_length=4000)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class MessagesResponse(BaseModel):
    messages: List[Message]
