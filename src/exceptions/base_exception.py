from __future__ import annotations

from typing import Optional


class BaseServiceException(Exception):
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        detail: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or message

    def __str__(self) -> str:
        return self.message