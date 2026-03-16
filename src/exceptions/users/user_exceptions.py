from __future__ import annotations

from src.exceptions.base_exception import BaseServiceException


class UserNotFoundException(BaseServiceException):
    def __init__(self, user_id: str | None = None) -> None:
        message = f"User with id '{user_id}' not found" if user_id else "User not found"
        super().__init__(message=message, status_code=404)

class UserAlreadyExistsException(BaseServiceException):
    def __init__(self, field: str, value: str) -> None:
        message = f"User with {field} '{value}' already exists"
        super().__init__(message=message, status_code=400)

class InvalidCpfException(BaseServiceException):
    def __init__(self, cpf: str | None = None) -> None:
        message = f"Invalid CPF format: {cpf}" if cpf else "Invalid CPF format"
        super().__init__(message=message, status_code=400)

class CpfUpdateNotAllowedException(BaseServiceException):
    def __init__(self) -> None:
        super().__init__(message="CPF cannot be updated", status_code=400)

class RoleNotFoundForUserException(BaseServiceException):
    def __init__(self, role_id: str) -> None:
        message = f"Role with id '{role_id}' not found"
        super().__init__(message=message, status_code=400)