from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import EmailStr, Field
from src.schemas.base import BaseSchema


class UserCreateSchema(BaseSchema):
    name: str = Field(..., max_length=255)
    username: str = Field(..., max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8)
    cpf: str = Field(..., max_length=32)
    birthday: date
    role_id: Optional[str] = None
