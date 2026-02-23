import uuid
import json
from io import StringIO
from typing import AsyncIterator

from fastapi import Depends, APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient, HTTPError

from app.deps import get_current_user_id, get_http_client
from app.core.config import LLM_SERVICE_URL, LLM_MODEL
from app.core.db import get_db
from app.crud.chat import (
    create_chat,
    get_chat_by_id,
    get_chat_with_messages,
    get_user_chats,
    delete_user_chat,
    delete_user_chats,
    update_chat_title,
)
from app.crud.message import create_message, get_chat_messages

from app.schemas.chat import ChatTitleCreate, ChatOut, ChatsOut, ChatTitleOut
from app.schemas.message import MessageCreate, MessageStream, MessagesOut
from app.schemas.llm import LLMMessage, LLMStreamRequest, LLMTitleRequest

router = APIRouter(prefix="/chats", tags=["chat"])


@router.post("/", response_model=ChatOut, status_code=201)
async def create_new_chat(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await create_chat(db=db, user_id=user_id)


@router.get("/", response_model=ChatsOut, status_code=200)
async def load_chats(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    chats = await get_user_chats(user_id=user_id, db=db)
    return {"chats": chats}


@router.get("/{chat_id}/messages", response_model=MessagesOut, status_code=200)
async def load_chat(
    chat_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    chat = await get_chat_with_messages(db=db, chat_id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.owner_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {"messages": chat.messages}


@router.delete("/{chat_id}", status_code=204)
async def delete_chat(
    request: Request,
    chat_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    client: AsyncClient = Depends(get_http_client),
):

    chat = await get_chat_by_id(db=db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.owner_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    user_cookies = request.cookies

    try:
        await client.delete(
            f"{LLM_SERVICE_URL}/vectors/{chat_id}", cookies=user_cookies, timeout=10.0
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete vectors: {str(e)}"
        )

    await delete_user_chat(db=db, chat=chat)


@router.delete("/", status_code=204)
async def delete_chats(
    request: Request,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    client: AsyncClient = Depends(get_http_client),
):
    user_cookies = request.cookies

    try:
        await client.delete(
            f"{LLM_SERVICE_URL}/vectors/", cookies=user_cookies, timeout=10.0
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete vectors: {str(e)}"
        )

    await delete_user_chats(db=db, user_id=user_id)


def sse(data: dict):
    return f"data: {json.dumps(data)}\n\n"


async def event_generator(
    body: LLMStreamRequest, request: Request, client: AsyncClient, db: AsyncSession
) -> AsyncIterator[str]:
    payload_json = body.model_dump(mode="json")
    user_cookies = request.cookies

    buf = StringIO()

    try:
        async with client.stream(
            "POST",
            f"{LLM_SERVICE_URL}/llm/stream",
            json=payload_json,
            cookies=user_cookies,
            timeout=120.0,
        ) as response:
            if response.status_code != 200:
                error_detail = await response.aread()
                yield sse({"type": "error", "detail": error_detail})
                return

            current_sub_type = "text"

            async for line in response.aiter_lines():
                if await request.is_disconnected():
                    break
                if not line:
                    continue

                yield f"{line}\n\n"

                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data.get("type") == "error":
                            return

                        new_sub_type = data.get("sub_type", "text")
                        if current_sub_type != new_sub_type:
                            content = buf.getvalue().strip()
                            if content:
                                await create_message(
                                    db=db,
                                    message=MessageCreate(
                                        role="assistant",
                                        sub_type=current_sub_type,
                                        content=content,
                                        chat_id=body.chat_id,
                                    ),
                                )
                                buf.truncate(0)
                                buf.seek(0)
                            current_sub_type = new_sub_type

                        chunk = data.get("content")
                        if chunk:
                            buf.write(chunk)

                        if data.get("done"):
                            return
                    except:
                        continue

    except HTTPError as e:
        yield sse({"type": "error", "detail": str(e)})
    except Exception as e:
        yield sse({"type": "error", "detail": str(e)})

    finally:
        content = buf.getvalue().strip()
        if content:
            await create_message(
                db=db,
                message=MessageCreate(
                    role="assistant",
                    sub_type=current_sub_type,
                    content=content,
                    chat_id=body.chat_id,
                ),
            )


@router.post("/{chat_id}/stream")
async def stream_chat_response(
    payload: MessageStream,
    request: Request,
    chat_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    client: AsyncClient = Depends(get_http_client),
    db: AsyncSession = Depends(get_db),
):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be blank")

    chat = await get_chat_by_id(db=db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.owner_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await create_message(
        db=db, message=MessageCreate(role="user", content=query, chat_id=chat_id)
    )

    db_messages = await get_chat_messages(db=db, chat_id=chat_id, limit=5)
    messages = [LLMMessage.model_validate(msg) for msg in db_messages]

    body = LLMStreamRequest(
        model=LLM_MODEL, temperature=0.7, messages=messages, chat_id=chat_id
    )

    return StreamingResponse(
        event_generator(body=body, request=request, client=client, db=db),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.patch("/{chat_id}", response_model=ChatTitleOut, status_code=200)
async def create_chat_title(
    payload: ChatTitleCreate,
    request: Request,
    chat_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    client: AsyncClient = Depends(get_http_client),
    db: AsyncSession = Depends(get_db),
):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be blank")

    chat = await get_chat_by_id(db=db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.owner_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    body = LLMTitleRequest(model=LLM_MODEL, temperature=0.3, query=query)
    payload_json = body.model_dump(mode="json")

    user_cookies = request.cookies

    response = await client.post(
        f"{LLM_SERVICE_URL}/llm/generate-title",
        json=payload_json,
        cookies=user_cookies,
        timeout=20.0,
    )
    response.raise_for_status()

    data = response.json()
    title = data.get("title", "New chat")
    updated_chat = await update_chat_title(db=db, chat=chat, title=title)

    return updated_chat
