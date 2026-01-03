from typing import List, Literal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ChatItem(BaseModel):
    id: UUID
    title: str


class ChatsResponse(BaseModel):
    chats: List[ChatItem]


class StreamRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    chat_id: UUID | None = None
    query: str = Field(..., min_length=1, max_length=4000)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class MessagesResponse(BaseModel):
    messages: List[Message]


class ChatTitleRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    query: str = Field(..., min_length=1, max_length=4000)


class ChatTitleResponse(BaseModel):
    title: str
