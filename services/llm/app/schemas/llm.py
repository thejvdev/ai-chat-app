import uuid
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class LLMMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    model_config = ConfigDict(from_attributes=True)


class LLMBaseRequest(BaseModel):
    model: str
    temperature: float


class LLMStream(LLMBaseRequest):
    messages: list[LLMMessage]
    chat_id: uuid.UUID


class LLMTitleCreate(LLMBaseRequest):
    query: str = Field(..., min_length=1, max_length=4000)
    model_config = ConfigDict(str_strip_whitespace=True)


class LLMTitleOut(BaseModel):
    title: str
    model_config = ConfigDict(from_attributes=True)
