from pydantic import BaseModel, Field


class ChatTitleSchema(BaseModel):
    title: str = Field(
        description="Make a short topic title (1-3 words) based on the user's query. "
        "Do not use quotes, punctuation, or extra words."
    )
