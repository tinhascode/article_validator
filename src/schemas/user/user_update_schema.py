from __future__ import annotations

from typing import Optional
from pydantic import Field
from src.schemas.base import BaseSchema


class UserUpdateSchema(BaseSchema):
    name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=150)
    role_id: Optional[str] = None
