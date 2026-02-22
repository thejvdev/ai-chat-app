import uuid
from typing import Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.chat import Chat


async def create_chat(db: AsyncSession, user_id: uuid.UUID) -> Chat:
    chat = Chat(owner_user_id=user_id, title="New chat")
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat


async def get_chat_by_id(db: AsyncSession, id: uuid.UUID) -> Chat | None:
    return await db.get(Chat, id)


async def get_chat_with_messages(db: AsyncSession, chat_id: uuid.UUID) -> Chat | None:
    result = await db.scalars(
        select(Chat).where(Chat.id == chat_id).options(selectinload(Chat.messages))
    )
    return result.one_or_none()


async def get_user_chats(db: AsyncSession, user_id: uuid.UUID) -> Sequence[Chat]:
    result = await db.scalars(
        select(Chat)
        .where(Chat.owner_user_id == user_id)
        .order_by(Chat.created_at.desc())
    )
    return result.all()


async def delete_user_chat(db: AsyncSession, chat: Chat):
    await db.delete(chat)
    await db.commit()


async def delete_user_chats(db: AsyncSession, user_id: uuid.UUID):
    await db.execute(delete(Chat).where(Chat.owner_user_id == user_id))
    await db.commit()


async def update_chat_title(db: AsyncSession, chat: Chat, title: str) -> Chat:
    chat.title = title
    await db.commit()
    await db.refresh(chat)
    return chat
