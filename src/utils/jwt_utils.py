from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from jose import JWTError, jwt

from src.config.jwt_config import JwtConfig


class JwtManager:
    def __init__(self, config: Optional[JwtConfig] = None) -> None:
        self.config = config or JwtConfig()

    def create_access_token(self, subject: str, expires_delta: Optional[timedelta] = None, **claims: Any) -> str:
        now = datetime.utcnow()
        expire = now + (expires_delta or self.config.access_token_expires())

        to_encode: Dict[str, Any] = {**claims}
        to_encode.update({
            "sub": str(subject),
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        })

        encoded = jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
        return encoded

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            return payload
        except JWTError as exc:  # pragma: no cover - library raised
            raise ValueError("token is invalid") from exc
