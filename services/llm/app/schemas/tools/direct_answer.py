from pydantic import BaseModel, Field


class DirectAnswerSchema(BaseModel):
    """
    Use this tool for direct, concise answers to straightforward questions.
    Ideal for queries seeking specific facts, definitions, or simple explanations.
    Avoid using this tool for complex reasoning, multi-step tasks, or when detailed context is required.
    """

    reasoning: str = Field(
        ...,
        description="Briefly justify your choice based on clear words from the user's query. "
        "The explanation should be short.",
    )
