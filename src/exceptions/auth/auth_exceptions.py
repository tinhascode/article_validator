from __future__ import annotations

from src.exceptions.base_exception import BaseServiceException

class InvalidCredentialsException(BaseServiceException):
    def __init__(self) -> None:
        super().__init__(message="Invalid username or password", status_code=401)

class InvalidTokenPayloadException(BaseServiceException):
    def __init__(self, detail: str = "Token payload is malformed") -> None:
        super().__init__(message="Invalid token", status_code=401, detail=detail)

class InvalidTokenException(BaseServiceException):
    def __init__(self, detail: str = "Token is invalid or expired") -> None:
        super().__init__(message="Invalid authentication token", status_code=401, detail=detail)

class UserNotFoundInTokenException(BaseServiceException):
    def __init__(self, user_id: str) -> None:
        super().__init__(message=f"User '{user_id}' from token not found", status_code=401)

class AdminPrivilegesRequiredException(BaseServiceException):
    def __init__(self) -> None:
        super().__init__(message="Admin privileges required", status_code=403)