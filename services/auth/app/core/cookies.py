from typing import Literal
from fastapi import Response
from app.core.config import ACCESS_TTL, REFRESH_TTL

SECURE = False
SAMESITE = "lax"


def set_token_cookies(
    response: Response,
    token: str,
    token_type: Literal["access", "refresh"],
):
    ttl = ACCESS_TTL if token_type == "access" else REFRESH_TTL

    response.set_cookie(
        key=f"{token_type}_token",
        value=token,
        httponly=True,
        secure=SECURE,
        samesite=SAMESITE,
        path="/",
        max_age=int(ttl.total_seconds()),
    )


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    set_token_cookies(response=response, token=access_token, token_type="access")
    set_token_cookies(response=response, token=refresh_token, token_type="refresh")


def clear_auth_cookies(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
