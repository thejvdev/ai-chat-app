import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.hashing import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_id(db: Session, id: uuid.UUID) -> User | None:
    return db.get(User, id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalars().first()


def create_user(db: Session, user: UserCreate) -> User:
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
