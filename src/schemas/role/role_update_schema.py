from __future__ import annotations

from typing import Optional
from pydantic import Field
from src.schemas.base import BaseSchema


class RoleUpdateSchema(BaseSchema):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
