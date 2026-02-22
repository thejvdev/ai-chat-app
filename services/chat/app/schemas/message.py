import uuid
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    role: Literal["user", "assistant"]
    sub_type: Literal["text"] = "text"
    content: str


class MessageCreate(MessageBase):
    chat_id: uuid.UUID


class MessageStream(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    model_config = ConfigDict(str_strip_whitespace=True)


class MessageOut(MessageBase):
    model_config = ConfigDict(from_attributes=True)


class MessagesOut(BaseModel):
    messages: list[MessageOut]
