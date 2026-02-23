import uuid

from fastapi import Depends, APIRouter
from qdrant_client import AsyncQdrantClient

from app.deps import get_current_user_id, get_qdrant_client
from app.crud.qdrant import delete_chat_points, delete_user_points

router = APIRouter(prefix="/vectors", tags=["vectors"])


@router.delete("/{chat_id}", status_code=204)
async def delete_chat(
    chat_id: str,
    user_id: uuid.UUID = Depends(get_current_user_id),
    qdrant_client: AsyncQdrantClient = Depends(get_qdrant_client),
):
    await delete_chat_points(client=qdrant_client, chat_id=chat_id, user_id=user_id)


@router.delete("/", status_code=204)
async def delete_user_chats(
    user_id: uuid.UUID = Depends(get_current_user_id),
    qdrant_client: AsyncQdrantClient = Depends(get_qdrant_client),
):
    await delete_user_points(client=qdrant_client, user_id=user_id)
