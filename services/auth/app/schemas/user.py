import uuid
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    full_name: str
    password: str


class UserLogin(UserBase):
    password: str


class UserOut(UserBase):
    id: uuid.UUID
    full_name: str
    model_config = ConfigDict(from_attributes=True)
