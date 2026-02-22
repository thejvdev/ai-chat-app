from typing import TypeVar, Type, AsyncIterator
from loguru import logger
from pydantic import BaseModel, ValidationError
from ollama import AsyncClient

T = TypeVar("T", bound=BaseModel)


async def generate(
    client: AsyncClient,
    model: str,
    messages: list,
    temperature: float = 0.7,
) -> AsyncIterator[dict]:
    try:
        response = await client.chat(
            model=model,
            messages=messages,
            stream=True,
            options={"temperature": temperature},
        )
        async for chunk in response:
            content = chunk.get("message", {}).get("content", "")
            yield {
                "type": "stream",
                "sub_type": "text",
                "content": content,
                "done": chunk.get("done", False),
            }

    except Exception as e:
        yield {"type": "error", "detail": str(e)}


async def predict_action(
    client: AsyncClient,
    model: str,
    messages: list,
    tools: list,
    temperature: float = 0,
) -> dict | None:
    json_instruction = {
        "role": "system",
        "content": "You are a router, your goal is to choose one tool or nothing. Briefly justify your choice in the 'reasoning' field.",
    }
    final_messages = [json_instruction] + messages

    try:
        response = await client.chat(
            model=model,
            messages=final_messages,
            tools=tools,
            stream=False,
            options={"temperature": temperature},
        )

        message = response.get("message", {})

        if tool_calls := message.get("tool_calls"):
            return tool_calls[0].model_dump()["function"]

    except Exception as e:
        logger.error(f"Error during LLM generation: {e}")

    return None


async def generate_json(
    client: AsyncClient,
    model: str,
    messages: list,
    schema: Type[T],
    temperature: float = 0,
) -> T | None:
    json_instruction = {
        "role": "system",
        "content": f"Output only valid JSON that matches this schema: {schema.model_json_schema()}",
    }
    final_messages = [json_instruction] + messages

    try:
        response = await client.chat(
            model=model,
            messages=final_messages,
            stream=False,
            format=schema.model_json_schema(),
            options={"temperature": temperature},
        )
        content = response.get("message", {}).get("content", "").strip()
        return schema.model_validate_json(content)

    except ValidationError as e:
        logger.error(f"LLM returned invalid JSON for schema {schema.__name__}: {e}")
    except Exception as e:
        logger.error(f"Error during LLM generation: {e}")

    return None
