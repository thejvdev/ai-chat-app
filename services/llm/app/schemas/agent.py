from typing import Literal
from pydantic import BaseModel, Field

CategoryType = Literal["general", "it"]


class DeepResearchSchema(BaseModel):
    """
    Use this tool for all requests requiring factual, recent, or specialized knowledge
    absent from your internal training.
    Mandatory for queries containing: 'latest', 'recent', 'current', 'news',
    or specific dates/events.
    Avoid using internal memory; prioritize this tool for high-precision retrieval.
    """

    reasoning: str = Field(
        ...,
        description="Briefly justify your choice based on clear words from the user's query. "
        "The explanation should be short.",
    )
    query: str = Field(
        ...,
        description="Transform the input into a dense search string. "
        "Remove fillers and add technical synonyms to maximize retrieval accuracy.",
    )
    web_queries: list[str] = Field(
        min_length=2,
        max_length=3,
        description=(
            "Generate 2-3 concise, keyword-focused search queries. "
            "Focus on core entities and search intent, avoiding conversational filler or full questions."
        ),
    )
    web_categories: list[CategoryType] = Field(
        min_length=1,
        max_length=2,
        description=(
            "Select 1-2 categories that will improve search engine results. "
            "Assign 'it' for all technical queries (programming, cloud, infrastructure, etc.). "
            "Use 'general' for non-technical topics."
        ),
    )
