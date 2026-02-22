from __future__ import annotations

import hashlib
from typing import Optional

from passlib.context import CryptContext
from passlib.exc import UnknownHashError


class PasswordManager:
    def __init__(self, scheme: str = "bcrypt") -> None:
        self._ctx: Optional[CryptContext] = CryptContext(schemes=[scheme], deprecated="auto")

    def hash(self, password: str) -> str:
        return self._ctx.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        try:
            return self._ctx.verify(plain, hashed)
        except UnknownHashError:
            return hashlib.sha256(plain.encode("utf-8")).hexdigest() == hashed
