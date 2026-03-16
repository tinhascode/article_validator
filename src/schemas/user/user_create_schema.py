from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import EmailStr, Field, field_validator
from src.schemas.base import BaseSchema


class UserCreateSchema(BaseSchema):
    name: str = Field(..., max_length=255)
    username: str = Field(..., max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    cpf: str = Field(..., max_length=32)
    birthday: date
    role_id: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password_byte_length(cls, v: str) -> str:
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (maximum 72 bytes when encoded)')
        return v
