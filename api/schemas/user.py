from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class UserRead(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    hashed_password: str
    created_at: datetime
