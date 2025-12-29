import uuid
from fastapi import Cookie, HTTPException
from jwt import InvalidTokenError, ExpiredSignatureError

from core.jwt import verify_access_token


def get_current_user_id(
    access_token: str | None = Cookie(default=None),
) -> uuid.UUID:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = verify_access_token(access_token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    try:
        return uuid.UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token subject")
