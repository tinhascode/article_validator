from __future__ import annotations

from src.schemas.base import BaseSchema

from .user_read_schema import UserReadSchema


class UserResponseSchema(BaseSchema):
    message: str
    user: UserReadSchema
