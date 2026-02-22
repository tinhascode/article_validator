from src.schemas.base import BaseSchema
from pydantic import Field

class RoleCreateSchema(BaseSchema):
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=255)