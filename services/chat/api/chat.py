from uuid import UUID
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import delete
from sqlalchemy.orm import Session

from services.llm import create_title, ask

from deps.chat import get_current_user_id
from core.db import get_db
from models.chat import Chat, Message
from schemas.chat import ChatsResponse, ChatItem, QueryRequest, MessagesResponse

router = APIRouter(prefix="/chats", tags=["chat"])


@router.get("", response_model=ChatsResponse, status_code=200)
def load_chats(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ChatsResponse:
    chats = (
        db.query(Chat)
        .filter(Chat.owner_user_id == user_id)
        .order_by(Chat.created_at.desc())
        .all()
    )
    return ChatsResponse(chats=[{"id": c.id, "title": c.title} for c in chats])


@router.post("", response_model=ChatItem, status_code=201)
async def create_chat(
    payload: QueryRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ChatItem:
    title = await create_title(payload.query)
    chat = Chat(owner_user_id=user_id, title=title)

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return ChatItem(id=chat.id, title=chat.title)


@router.get("/{chat_id}/messages", response_model=MessagesResponse, status_code=200)
def load_chat(
    chat_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> MessagesResponse:
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat.owner_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return MessagesResponse(
        messages=[{"role": m.role, "content": m.content} for m in messages]
    )


@router.delete("/{chat_id}", status_code=204)
def delete_chat(
    chat_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat.owner_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.execute(delete(Chat).where(Chat.id == chat_id))
    db.commit()

    return


@router.delete("", status_code=204)
def delete_all_chats(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    db.execute(delete(Chat).where(Chat.owner_user_id == user_id))
    db.commit()

    return


def sse_data(chunk: str) -> str:
    lines = chunk.splitlines() or [""]
    return "".join(f"data: {line}\n" for line in lines) + "\n"


@router.post("/{chat_id}/messages", status_code=201)
async def send_message(
    chat_id: UUID,
    payload: QueryRequest,
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat.owner_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = payload.query
    user_message = Message(chat_id=chat_id, role="user", content=query)

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .limit(5)
        .all()
    )

    messages = list(reversed(messages))
    history = [(m.role, m.content) for m in messages]

    async def event_stream():
        buff = StringIO()

        try:
            async for token in ask(history):
                if await request.is_disconnected():
                    break
                if not token:
                    continue

                buff.write(token)
                yield sse_data(token)

        finally:
            answer_text = buff.getvalue().strip()

            if answer_text:
                assistant_message = Message(
                    chat_id=chat_id, role="assistant", content=answer_text
                )

                db.add(assistant_message)
                db.commit()
                db.refresh(assistant_message)

        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
