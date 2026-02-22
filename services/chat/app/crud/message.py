import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import Message
from app.schemas.message import MessageCreate


async def create_message(db: AsyncSession, message: MessageCreate) -> Message:
    new_message = Message(**message.model_dump())
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message


async def get_chat_messages(
    db: AsyncSession, chat_id: uuid.UUID, limit: int
) -> Sequence[Message]:
    result = await db.scalars(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    return result.all()[::-1]
