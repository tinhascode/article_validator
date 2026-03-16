from __future__ import annotations

import hashlib
from typing import Optional

from passlib.context import CryptContext
from passlib.exc import UnknownHashError


class PasswordManager:
    def __init__(self, scheme: str = "argon2") -> None:
        if scheme == "bcrypt":
            self._ctx: Optional[CryptContext] = CryptContext(
                schemes=["bcrypt"],
                deprecated="auto",
                bcrypt__default_rounds=12,
                bcrypt__truncate_error=True,
            )
        else:
            self._ctx: Optional[CryptContext] = CryptContext(
                schemes=["argon2", "bcrypt"],
                deprecated="auto",
                argon2__default_rounds=2,
                argon2__memory_cost=65536,
                bcrypt__default_rounds=12,
                bcrypt__truncate_error=True,
            )

    def hash(self, password: str) -> str:
        try:
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                while len(password_bytes) > 72:
                    password = password[:-1]
                    password_bytes = password.encode('utf-8')
            
            return self._ctx.hash(password)
        except Exception as e:
            return f"sha256${hashlib.sha256(password.encode('utf-8')).hexdigest()}"

    def verify(self, plain: str, hashed: str) -> bool:
        try:
            if hashed.startswith("sha256$"):
                return hashed == f"sha256${hashlib.sha256(plain.encode('utf-8')).hexdigest()}"
            password_bytes = plain.encode('utf-8')
            if len(password_bytes) > 72:
                while len(password_bytes) > 72:
                    plain = plain[:-1]
                    password_bytes = plain.encode('utf-8')
            
            return self._ctx.verify(plain, hashed)
        except UnknownHashError:
            return hashlib.sha256(plain.encode("utf-8")).hexdigest() == hashed
        except Exception:
            return hashed == f"sha256${hashlib.sha256(plain.encode('utf-8')).hexdigest()}"
