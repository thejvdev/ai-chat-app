import uuid
from fastapi import Cookie, HTTPException, Request
from httpx import AsyncClient
from app.core.jwt import verify_token_and_get_user_id


def get_current_user_id(access_token: str | None = Cookie(default=None)) -> uuid.UUID:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return verify_token_and_get_user_id(token=access_token, expected_type="access")


def get_http_client(request: Request) -> AsyncClient:
    return request.app.state.http_client
