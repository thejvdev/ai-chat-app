import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

from httpx import AsyncClient as HttpxClient
from unstructured_client import UnstructuredClient
from qdrant_client import AsyncQdrantClient
from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder

from app.core.config import VECTOR_SIZE
from app.crud.qdrant import upsert_points, search_similar
from app.services.web_search import web_parse
from app.services.llm.utils import save_to_json
from app.services.rag.chunking import get_chunks
from app.services.rag.vectorizer import embed_texts
from app.services.rag.reranking import rerank_chunks


async def deep_research(
    http_client: HttpxClient,
    unstructured_client: UnstructuredClient,
    qdrant_client: AsyncQdrantClient,
    models: tuple[TextEmbedding, TextCrossEncoder, ThreadPoolExecutor],
    chat_id: uuid.UUID,
    user_id: uuid.UUID,
    query: str,
    web_queries: list[str],
    web_categories: list[str],
    with_log: bool = False,
) -> list[dict]:
    embedding_model, reranker_model, executor = models

    records = await web_parse(
        client=http_client,
        queries=web_queries,
        categories=web_categories,
        limit_per_query=1,
        format="html",
    )

    chunking_tasks = [
        get_chunks(
            client=unstructured_client,
            text=record["content"],
            format="html",
            size=VECTOR_SIZE,
        )
        for record in records
    ]

    chunks_per_record = await asyncio.gather(*chunking_tasks)

    flat_chunks = []
    flat_data = []

    for chunks, record in zip(chunks_per_record, records):
        for chunk in chunks:
            flat_chunks.append(chunk)
            flat_data.append(
                {
                    "payload": {
                        "chat_id": str(chat_id),
                        "user_id": str(user_id),
                        "content": chunk,
                        "metadata": record["metadata"],
                    }
                }
            )

    vectors = await embed_texts(
        model=embedding_model, executor=executor, texts=flat_chunks
    )

    for i, vector in enumerate(vectors):
        flat_data[i]["vector"] = vector

    await upsert_points(client=qdrant_client, data=flat_data)

    query_vector = (
        await embed_texts(model=embedding_model, executor=executor, texts=[query])
    )[0]

    points = await search_similar(
        client=qdrant_client, query_vector=query_vector, top_k=20
    )

    results = await rerank_chunks(
        model=reranker_model, executor=executor, query=query, points=points, top_k=5
    )

    if with_log:
        save_to_json("1_records", {"records": records})
        save_to_json("2_flat_data", {"flat_data": flat_data})
        save_to_json("3_points", {"points": points})
        save_to_json("4_results", {"results": results})

    return results
