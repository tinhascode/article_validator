from __future__ import annotations

import hashlib
from typing import Optional

try:
    from passlib.context import CryptContext
except Exception:  # pragma: no cover - optional dependency
    CryptContext = None


class PasswordManager:
    def __init__(self, scheme: str = "bcrypt") -> None:
        if CryptContext is not None:
            self._ctx = CryptContext(schemes=[scheme], deprecated="auto")
        else:
            self._ctx = None

    def hash(self, password: str) -> str:
        if self._ctx:
            return self._ctx.hash(password)
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify(self, plain: str, hashed: str) -> bool:
        if self._ctx:
            return self._ctx.verify(plain, hashed)
        return hashlib.sha256(plain.encode("utf-8")).hexdigest() == hashed
