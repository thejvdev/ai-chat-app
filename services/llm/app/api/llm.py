import json
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

from fastapi import Depends, APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

from ollama import AsyncClient as OllamaClient
from httpx import AsyncClient as HttpxClient
from unstructured_client import UnstructuredClient
from qdrant_client import AsyncQdrantClient
from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder

from app.deps import (
    get_current_user_id,
    get_ollama_client,
    get_http_client,
    get_unstructured_client,
    get_qdrant_client,
    get_models_with_executor,
)
from app.services.chat.naming import create_title
from app.services.agent.orchestrator import run_agent
from app.schemas.llm import LLMStream, LLMTitleCreate, LLMTitleOut

router = APIRouter(prefix="/llm", tags=["llm"])


def sse(data: dict):
    return f"data: {json.dumps(data)}\n\n"


@router.post(
    "/stream",
    dependencies=[Depends(get_current_user_id)],
    status_code=200,
)
async def stream(
    payload: LLMStream,
    request: Request,
    ollama_client: OllamaClient = Depends(get_ollama_client),
    http_client: HttpxClient = Depends(get_http_client),
    unstructured_client: UnstructuredClient = Depends(get_unstructured_client),
    qdrant_client: AsyncQdrantClient = Depends(get_qdrant_client),
    models: tuple[TextEmbedding, TextCrossEncoder, ThreadPoolExecutor] = Depends(
        get_models_with_executor
    ),
):
    async def event_generator():
        async for data in run_agent(
            ollama_client=ollama_client,
            http_client=http_client,
            unstructured_client=unstructured_client,
            qdrant_client=qdrant_client,
            models=models,
            payload=payload,
            with_log=True,
        ):
            if await request.is_disconnected():
                logger.warning("Client disconnected, stopping agent execution")
                break
            yield sse(data)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post(
    "/generate-title",
    dependencies=[Depends(get_current_user_id)],
    response_model=LLMTitleOut,
    status_code=200,
)
async def create_chat_title(
    payload: LLMTitleCreate,
    ollama_client: OllamaClient = Depends(get_ollama_client),
):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be blank")

    result = await create_title(
        client=ollama_client,
        query=query,
        model=payload.model,
        temperature=payload.temperature,
    )

    if not result:
        return {"title": "New chat"}

    return result
