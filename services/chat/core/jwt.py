import jwt
from jwt import InvalidTokenError
from .config import JWT_ALG, JWT_PUBLIC_KEY


def verify_access_token(access_token: str) -> dict:
    payload = jwt.decode(
        access_token,
        JWT_PUBLIC_KEY,
        algorithms=[JWT_ALG],
        options={"require": ["exp", "sub"]},
    )

    if payload.get("type") != "access":
        raise InvalidTokenError("Wrong token type")

    return payload
