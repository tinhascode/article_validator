from __future__ import annotations

from datetime import date, datetime
from pydantic import EmailStr
from src.schemas.base import BaseSchema


class UserReadSchema(BaseSchema):
    id: str
    name: str
    username: str
    email: EmailStr
    cpf: str
    birthday: date
    created_at: datetime
    updated_at: datetime
