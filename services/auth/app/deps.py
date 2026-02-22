from fastapi import Depends, Cookie, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.jwt import verify_token_and_get_user_id
from app.crud.user import get_user_by_id
from app.models.user import User


def get_current_user(
    db: Session = Depends(get_db), access_token: str | None = Cookie(default=None)
) -> User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = verify_token_and_get_user_id(token=access_token, expected_type="access")

    user = get_user_by_id(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
