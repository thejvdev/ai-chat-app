from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db import get_db

from models.user import User
from schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserRead], status_code=200)
def read_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()
