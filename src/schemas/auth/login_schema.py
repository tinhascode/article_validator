from __future__ import annotations

from pydantic import BaseModel, Field


class LoginSchema(BaseModel):
    username_or_email: str = Field(..., description="Username or email of the user")
    password: str = Field(..., description="Plain text password")
