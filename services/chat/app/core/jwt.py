import uuid
from typing import Literal

import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
from fastapi import HTTPException
from app.core.config import JWT_ALG, JWT_PUBLIC_KEY


def verify_token(token: str, expected_type: Literal["access", "refresh"]) -> dict:
    payload = jwt.decode(
        token, JWT_PUBLIC_KEY, algorithms=[JWT_ALG], options={"require": ["exp", "sub"]}
    )
    if payload.get("type") != expected_type:
        raise InvalidTokenError("Wrong token type")
    return payload


def verify_token_and_get_user_id(
    token: str, expected_type: Literal["access", "refresh"]
) -> uuid.UUID:
    try:
        payload = verify_token(token, expected_type=expected_type)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401, detail=f"Invalid {expected_type} token payload"
            )

        return uuid.UUID(user_id)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401, detail=f"{expected_type.capitalize()} token expired"
        )
    except (InvalidTokenError, ValueError):
        raise HTTPException(status_code=401, detail=f"Invalid {expected_type} token")
