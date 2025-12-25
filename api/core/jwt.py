from datetime import datetime, timezone, timedelta
import uuid

import jwt
from jwt import InvalidTokenError
from .config import ALGORITHM, PRIVATE_KEY, PUBLIC_KEY

ACCESS_TTL = timedelta(minutes=1)
REFRESH_TTL = timedelta(minutes=5)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_token(user_id: str, token_type: str, ttl: timedelta) -> str:
    now = _now()
    payload = {
        "sub": user_id,
        "type": token_type,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + ttl,
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: str) -> str:
    return create_token(user_id=user_id, token_type="access", ttl=ACCESS_TTL)


def create_refresh_token(user_id: str) -> str:
    return create_token(user_id, token_type="refresh", ttl=REFRESH_TTL)


def decode_and_validate(token: str, expected_type: str) -> dict:
    payload = jwt.decode(
        token, PUBLIC_KEY, algorithms=[ALGORITHM], options={"require": ["exp", "sub"]}
    )

    if payload.get("type") != expected_type:
        raise InvalidTokenError("Wrong token type")

    return payload
