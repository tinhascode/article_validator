from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import EmailStr, Field
from src.schemas.base import BaseSchema


class UserUpdateSchema(BaseSchema):
    name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    cpf: Optional[str] = Field(None, max_length=32)
    birthday: Optional[date] = None
