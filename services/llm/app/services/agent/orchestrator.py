import uuid
from typing import AsyncIterator

from concurrent.futures import ThreadPoolExecutor
from loguru import logger

from ollama import AsyncClient as OllamaClient
from httpx import AsyncClient as HttpxClient
from unstructured_client import UnstructuredClient
from qdrant_client import AsyncQdrantClient
from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder

from app.services.llm.client import generate, predict_action
from app.services.llm.utils import get_tool_definition
from app.services.llm.formatters import format_rag_context
from app.services.agent.deep_research import deep_research

from app.schemas.llm import LLMStream
from app.schemas.tools.direct_answer import DirectAnswerSchema
from app.schemas.tools.deep_research import DeepResearchSchema


TOOLS = [
    get_tool_definition("direct_answer", DirectAnswerSchema),
    get_tool_definition("deep_research", DeepResearchSchema),
]


async def run_agent(
    ollama_client: OllamaClient,
    http_client: HttpxClient,
    unstructured_client: UnstructuredClient,
    qdrant_client: AsyncQdrantClient,
    models: tuple[TextEmbedding, TextCrossEncoder, ThreadPoolExecutor],
    payload: LLMStream,
    user_id: uuid.UUID,
    with_log: bool = False,
) -> AsyncIterator[dict]:
    model = payload.model
    temperature = payload.temperature
    messages = payload.messages
    chat_id = payload.chat_id

    tool_call = await predict_action(
        client=ollama_client, model=model, messages=messages, tools=TOOLS
    )
    logger.info(f"Tool call: {str(tool_call)}")

    context = ""

    if tool_call:
        if tool_call.get("name") == "deep_research":
            args = tool_call.get("arguments", {})

            try:
                async for update in deep_research(
                    http_client=http_client,
                    unstructured_client=unstructured_client,
                    qdrant_client=qdrant_client,
                    models=models,
                    chat_id=chat_id,
                    user_id=user_id,
                    query=args.get("query"),
                    web_queries=args.get("web_queries"),
                    web_categories=args.get("web_categories"),
                    with_log=with_log,
                ):
                    if update["type"] == "complete":
                        context = format_rag_context(documents=update["results"])
                        logger.info(f"Provided context:\n{context}")
                    else:
                        yield update

            except Exception as e:
                logger.error(f"Deep research execution failed: {e}")
                context = "Error during research. Please rely on internal knowledge but mention the technical issue."

    if context:
        system_instruction = {
            "role": "system",
            "content": (
                "You are a friendly assistant. Use the text below as your knowledge base and 'memory' to respond to the user.\n"
                "Instructions:\n"
                "1. Respond naturally, as if you already know this information.\n"
                "2. All your answers should be based solely on the context provided.\n"
                "3. Do not invent facts or use external knowledge that is not mentioned in the text.\n"
                f"Context:\n{context}\n"
            ),
        }
        final_messages = [system_instruction] + messages
    else:
        final_messages = messages

    async for chunk in generate(
        client=ollama_client,
        model=model,
        messages=final_messages,
        temperature=temperature,
    ):
        yield chunk
