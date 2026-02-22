from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from pydantic import EmailStr
from src.schemas.base import BaseSchema
from src.schemas.role.role_read_schema import RoleReadSchema


class UserReadSchema(BaseSchema):
    id: str
    name: str
    username: str
    email: EmailStr
    role: Optional[RoleReadSchema] = None
    cpf: str
    birthday: date
    created_at: datetime
    updated_at: datetime
