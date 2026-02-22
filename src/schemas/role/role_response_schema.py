from src.schemas.base import BaseSchema
from src.schemas.role.role_read_schema import RoleReadSchema


class RoleResponseSchema(BaseSchema):
    message: str
    role: RoleReadSchema
