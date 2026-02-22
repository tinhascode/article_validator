from __future__ import annotations

from pydantic import BaseModel


class BaseSchema(BaseModel):
    # Pydantic v2: use `model_config` and `from_attributes` (replaces `orm_mode`)
    model_config = {"from_attributes": True}
