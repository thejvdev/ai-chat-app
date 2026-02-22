import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastembed import TextEmbedding


async def embed_texts(
    model: TextEmbedding, executor: ThreadPoolExecutor, texts: list[str]
) -> list[list[float]]:
    if not texts:
        return []

    loop = asyncio.get_running_loop()

    def sync_embedding():
        vectors = model.embed(texts, batch_size=32)
        return [vector.tolist() for vector in vectors]

    return await loop.run_in_executor(executor, sync_embedding)
