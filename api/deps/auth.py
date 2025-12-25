from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from jwt import InvalidTokenError, ExpiredSignatureError

from core.db import get_db
from core.jwt import decode_and_validate

from models.user import User


def get_current_user(
    access_token: str = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_and_validate(access_token, expected_type="access")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
