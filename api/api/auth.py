from fastapi import APIRouter, Response, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from jwt import InvalidTokenError, ExpiredSignatureError

from deps.auth import get_current_user
from core.db import get_db
from core.password import verify_password, hash_password
from core.jwt import create_access_token, create_refresh_token, decode_and_validate
from core.cookies import set_access_cookies, set_auth_cookies, clear_auth_cookies

from models.user import User
from schemas.auth import TokenResponse, RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, status_code=200)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))

    set_auth_cookies(response, access_token=access, refresh_token=refresh)

    return TokenResponse(id=user.id, full_name=user.full_name, email=user.email)


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    payload: RegisterRequest, response: Response, db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))

    set_auth_cookies(response, access_token=access, refresh_token=refresh)

    return TokenResponse(id=user.id, full_name=user.full_name, email=user.email)


@router.get("/me", response_model=TokenResponse, status_code=200)
def me(user: User = Depends(get_current_user)) -> TokenResponse:
    return TokenResponse(id=user.id, full_name=user.full_name, email=user.email)


@router.post("/logout", status_code=204)
def logout(response: Response):
    clear_auth_cookies(response)
    return


@router.post("/refresh", status_code=200)
def refresh(response: Response, refresh_token: str | None = Cookie(default=None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = decode_and_validate(refresh_token, expected_type="refresh")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload["sub"]
    access = create_access_token(user_id)

    set_access_cookies(response, access_token=access)

    return {"ok": True}
