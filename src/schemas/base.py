from __future__ import annotations

from pydantic import BaseModel


class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}
