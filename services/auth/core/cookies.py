from fastapi import Response
from .jwt import ACCESS_TTL, REFRESH_TTL

SECURE = False
SAMESITE = "lax"


def set_access_cookies(response: Response, access_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=SECURE,
        samesite=SAMESITE,
        path="/",
        max_age=int(ACCESS_TTL.total_seconds()),
    )


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    set_access_cookies(response, access_token)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=SECURE,
        samesite=SAMESITE,
        path="/auth/refresh",
        max_age=int(REFRESH_TTL.total_seconds()),
    )


def clear_auth_cookies(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/auth/refresh")
