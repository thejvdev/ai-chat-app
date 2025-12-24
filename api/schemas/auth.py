from pydantic import BaseModel, EmailStr
from uuid import UUID


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
