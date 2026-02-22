import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi import Cookie, HTTPException, Request
from ollama import AsyncClient as OllamaClient
from httpx import AsyncClient as HttpxClient
from unstructured_client import UnstructuredClient
from qdrant_client import AsyncQdrantClient
from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder

from app.core.jwt import verify_token_and_get_user_id


def get_current_user_id(access_token: str | None = Cookie(default=None)) -> uuid.UUID:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return verify_token_and_get_user_id(token=access_token, expected_type="access")


def get_ollama_client(request: Request) -> OllamaClient:
    return request.app.state.ollama_client


def get_http_client(request: Request) -> HttpxClient:
    return request.app.state.http_client


def get_unstructured_client(request: Request) -> UnstructuredClient:
    return request.app.state.unstructured_client


def get_qdrant_client(request: Request) -> AsyncQdrantClient:
    return request.app.state.qdrant_client


def get_models_with_executor(
    request: Request,
) -> tuple[TextEmbedding, TextCrossEncoder, ThreadPoolExecutor]:
    state = request.app.state
    return (state.embedding_model, state.reranker_model, state.executor)
