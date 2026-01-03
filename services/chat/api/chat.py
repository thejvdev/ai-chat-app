from uuid import UUID
from io import StringIO
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import delete
from sqlalchemy.orm import Session

from services.llm import create_title, ask

from deps.chat import get_current_user_id
from core.db import get_db
from models.chat import Chat, Message
from schemas.chat import (
    ChatsResponse,
    StreamRequest,
    MessagesResponse,
    ChatTitleRequest,
    ChatTitleResponse,
)

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


@router.delete("", status_code=204)
def delete_chats(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    db.execute(delete(Chat).where(Chat.owner_user_id == user_id))
    db.commit()
    return


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


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def stream_chat_response(
    payload: StreamRequest,
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be blank")

    chat_id = payload.chat_id

    if chat_id is not None:
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        if chat.owner_user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        messages = (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(5)
            .all()
        )
        messages.reverse()
        history = [(m.role, m.content) for m in messages]
    else:
        chat = Chat(owner_user_id=user_id, title="New chat")
        db.add(chat)
        db.commit()
        db.refresh(chat)

        chat_id = chat.id
        history = []

    history.append(("user", query))

    user_message = Message(chat_id=chat_id, role="user", content=query)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    async def event_stream():
        if payload.chat_id is None:
            yield sse("meta", {"chat_id": str(chat_id)})

        buf = StringIO()

        try:
            async for chunk in ask(history):
                if await request.is_disconnected():
                    break
                if not chunk:
                    continue

                buf.write(chunk)
                yield sse("stream", {"text": chunk})
        except Exception:
            yield sse("error", {"message": "Generation failed"})
            return
        finally:
            answer_text = buf.getvalue().strip()
            if answer_text:
                assistant_message = Message(
                    chat_id=chat_id, role="assistant", content=answer_text
                )
                db.add(assistant_message)
                db.commit()
                db.refresh(assistant_message)

        yield sse("done", {})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.patch("/{chat_id}", response_model=ChatTitleResponse, status_code=200)
async def regenerate_chat_title(
    chat_id: UUID,
    payload: ChatTitleRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ChatTitleResponse:
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be blank")

    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.owner_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    title = await create_title(query)
    chat.title = title

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return ChatTitleResponse(id=chat.id, title=chat.title)
