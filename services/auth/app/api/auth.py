import uuid
from fastapi import Depends, Cookie, APIRouter, Response, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.core.db import get_db
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token_and_get_user_id,
)
from app.core.hashing import verify_password
from app.core.cookies import set_auth_cookies, clear_auth_cookies
from app.crud.user import get_user_by_id, get_user_by_email, create_user

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def create_auth_session(response: Response, user_id: uuid.UUID | str):
    access = create_access_token(str(user_id))
    refresh = create_refresh_token(str(user_id))
    set_auth_cookies(response, access_token=access, refresh_token=refresh)


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    if get_user_by_email(db=db, email=payload.email) is not None:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = create_user(db=db, user=payload)
    create_auth_session(response=response, user_id=user.id)
    return user


@router.post("/login", response_model=UserOut, status_code=200)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = get_user_by_email(db=db, email=payload.email)

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    create_auth_session(response=response, user_id=user.id)
    return user


@router.get("/me", response_model=UserOut, status_code=200)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/logout", status_code=204)
def logout(response: Response):
    clear_auth_cookies(response)
    return


@router.post("/refresh", response_model=UserOut, status_code=200)
def refresh(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    user_id = verify_token_and_get_user_id(token=refresh_token, expected_type="refresh")

    user = get_user_by_id(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    create_auth_session(response=response, user_id=user.id)
    return user
