from __future__ import annotations

from src.exceptions.base_exception import BaseServiceException

class RefreshTokenNotFoundException(BaseServiceException):
    def __init__(self) -> None:
        super().__init__(message="Refresh token not found", status_code=401)

class RefreshTokenInvalidException(BaseServiceException):
    def __init__(self, detail: str = "Refresh token is invalid or expired") -> None:
        super().__init__(message="Invalid refresh token", status_code=401, detail=detail)

class RefreshTokenMissingException(BaseServiceException):
    def __init__(self) -> None:
        super().__init__(message="Refresh token is required", status_code=401)

class InvalidCsrfTokenException(BaseServiceException):
    def __init__(self) -> None:
        super().__init__(message="Invalid CSRF token", status_code=401)

class DeviceMismatchException(BaseServiceException):
    def __init__(self) -> None:
        super().__init__(message="Device mismatch detected", status_code=401)