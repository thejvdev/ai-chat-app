from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

from fastapi import FastAPI

from ollama import AsyncClient as AsyncOllamaClient
from httpx import AsyncClient as AsyncHttpxClient, Limits
from unstructured_client import UnstructuredClient

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PayloadSchemaType

from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder

from app.api.llm import router as llm_router
from app.api.vectors import router as vectors_router

from app.core.config import (
    OLLAMA_HOST,
    UNSTRUCTURED_API_URL,
    QDRANT_URL,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    RERANKER_MODEL,
    VECTOR_SIZE,
    LOG_DIR,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    app.state.ollama_client = AsyncOllamaClient(host=OLLAMA_HOST)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/",
    }

    app.state.http_client = AsyncHttpxClient(
        timeout=60,
        limits=Limits(max_connections=50, max_keepalive_connections=10),
        headers=headers,
        follow_redirects=True,
    )

    app.state.unstructured_client = UnstructuredClient(
        server_url=UNSTRUCTURED_API_URL, api_key_auth=""
    )

    app.state.qdrant_client = AsyncQdrantClient(url=QDRANT_URL)

    app.state.embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL)
    app.state.reranker_model = TextCrossEncoder(model_name=RERANKER_MODEL)
    app.state.executor = ThreadPoolExecutor(max_workers=2)

    try:
        from qdrant_client.models import Distance, VectorParams

        exists = await app.state.qdrant_client.collection_exists(COLLECTION_NAME)
        if not exists:
            await app.state.qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
                wait=True,
            )
            logger.info(f"Created new collection: {COLLECTION_NAME}")

            await app.state.qdrant_client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="chat_id",
                field_schema=PayloadSchemaType.KEYWORD,
                wait=True,
            )

            await app.state.qdrant_client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="user_id",
                field_schema=PayloadSchemaType.KEYWORD,
                wait=True,
            )
            logger.info("Created payload index on 'user_id' and 'chat_id'")

        logger.info("Successfully connected to Qdrant")
    except Exception as e:
        logger.error(f"Error connecting to Qdrant: {e}")

    yield

    await app.state.http_client.aclose()
    await app.state.qdrant_client.close()
    app.state.executor.shutdown(wait=True)


app = FastAPI(lifespan=lifespan)
app.include_router(llm_router)
app.include_router(vectors_router)
