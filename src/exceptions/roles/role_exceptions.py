from __future__ import annotations

from src.exceptions.base_exception import BaseServiceException


class RoleNotFoundException(BaseServiceException):
    def __init__(self, role_id: str | None = None) -> None:
        message = f"Role with id '{role_id}' not found" if role_id else "Role not found"
        super().__init__(message=message, status_code=404)


class RoleAlreadyExistsException(BaseServiceException):
    def __init__(self, name: str) -> None:
        message = f"Role with name '{name}' already exists"
        super().__init__(message=message, status_code=400)