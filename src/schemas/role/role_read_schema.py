
from datetime import datetime
from src.schemas.base import BaseSchema

class RoleReadSchema(BaseSchema):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime