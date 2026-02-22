import asyncio
from concurrent.futures import ThreadPoolExecutor
from qdrant_client.models import ScoredPoint
from fastembed.rerank.cross_encoder import TextCrossEncoder


async def rerank_chunks(
    model: TextCrossEncoder,
    executor: ThreadPoolExecutor,
    query: str,
    points: list[ScoredPoint],
    top_k: int,
):
    chunks = [point.payload["content"] for point in points]
    if not chunks:
        return []

    loop = asyncio.get_running_loop()

    def sync_rerank():
        return list(model.rerank(query, documents=chunks, batch_size=32))

    scores = await loop.run_in_executor(executor, sync_rerank)

    results = []
    for point, score in zip(points, scores):
        results.append(
            {
                "content": point.payload["content"],
                "metadata": point.payload.get("metadata", {}),
                "score": score,
            }
        )

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
