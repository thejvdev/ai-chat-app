from ollama import AsyncClient
from app.services.llm.client import generate_json
from app.schemas.naming import ChatTitleSchema


async def create_title(
    client: AsyncClient,
    query: str,
    model: str = "mistral",
    temperature: float = 0.3,
) -> ChatTitleSchema | None:
    return await generate_json(
        client=client,
        model=model,
        messages=[{"role": "user", "content": query}],
        schema=ChatTitleSchema,
        temperature=temperature,
    )
