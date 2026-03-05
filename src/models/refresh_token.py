from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String

from src.models.base.base_model import BaseModel


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    jti = Column(String(36), unique=True, nullable=False)
    token_hash = Column(String(128), nullable=False, unique=True)
    device_id = Column(String(255), nullable=True)
    ip = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    rotated_from = Column(String(36), ForeignKey("refresh_tokens.id"), nullable=True)
    rotated_at = Column(DateTime(timezone=True), nullable=True)

    def __init__(
        self,
        user_id: str,
        jti: str,
        token_hash: str,
        device_id: Optional[str] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_at: datetime = None,
        revoked: bool = False,
        rotated_from: Optional[str] = None,
        rotated_at: Optional[datetime] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.user_id = user_id
        self.jti = jti
        self.token_hash = token_hash
        self.device_id = device_id
        self.ip = ip
        self.user_agent = user_agent
        self.expires_at = expires_at
        self.revoked = revoked
        self.rotated_from = rotated_from
        self.rotated_at = rotated_at

    def is_active(self) -> bool:
        if self.revoked:
            return False
        if self.expires_at is None:
            return False
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return expires > datetime.now(timezone.utc)
