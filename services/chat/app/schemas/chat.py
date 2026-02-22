import uuid
from pydantic import BaseModel, ConfigDict, Field


class ChatTitleCreate(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    model_config = ConfigDict(str_strip_whitespace=True)


class ChatOut(BaseModel):
    id: uuid.UUID
    title: str
    model_config = ConfigDict(from_attributes=True)


class ChatsOut(BaseModel):
    chats: list[ChatOut]


class ChatTitleOut(BaseModel):
    title: str
    model_config = ConfigDict(from_attributes=True)
