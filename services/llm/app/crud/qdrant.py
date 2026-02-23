import uuid
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    PointStruct,
    ScoredPoint,
    Filter,
    FieldCondition,
    MatchValue,
)
from app.core.config import COLLECTION_NAME


async def upsert_points(client: AsyncQdrantClient, data: list[dict]):
    if not data:
        return

    points = [
        PointStruct(
            id=str(uuid.uuid4()), vector=item["vector"], payload=item["payload"]
        )
        for item in data
    ]

    await client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)


async def delete_chat_points(
    client: AsyncQdrantClient, chat_id: uuid.UUID | str, user_id: uuid.UUID | str
):
    await client.delete(
        collection_name=COLLECTION_NAME,
        filter=Filter(
            must=[
                FieldCondition(
                    key="chat_id",
                    match=MatchValue(value=str(chat_id)),
                ),
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=str(user_id)),
                ),
            ]
        ),
        wait=True,
    )


async def delete_user_points(client: AsyncQdrantClient, user_id: uuid.UUID | str):
    await client.delete(
        collection_name=COLLECTION_NAME,
        filter=Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=str(user_id)),
                )
            ]
        ),
        wait=True,
    )


async def search_similar(
    client: AsyncQdrantClient,
    chat_id: uuid.UUID | str,
    user_id: uuid.UUID | str,
    query_vector: list[float],
    top_k: int,
    score_threshold=0.5,
) -> list[ScoredPoint]:
    return (
        await client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="chat_id",
                        match=MatchValue(value=str(chat_id)),
                    ),
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=str(user_id)),
                    ),
                ]
            ),
            limit=top_k,
            with_payload=True,
            score_threshold=score_threshold,
        )
    ).points
