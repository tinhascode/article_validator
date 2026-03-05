from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from fastapi import Depends

from src.config.settings import get_db

from src.config.jwt_config import JwtConfig
from src.models.refresh_token import RefreshToken
from src.config.logger import get_logger


class TokenService:
    def __init__(self, db: Session, config: Optional[JwtConfig] = None) -> None:
        self.db = db
        self.config = config or JwtConfig()
        self.logger = get_logger(self.__class__.__name__)

    def _hash(self, raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    def create_refresh_token(self, user_id: str, device_id: Optional[str] = None, ip: Optional[str] = None, user_agent: Optional[str] = None) -> str:
        try:
            raw = secrets.token_urlsafe(64)
            token_hash = self._hash(raw)
            jti = str(uuid.uuid4())
            expires_at = datetime.now(timezone.utc) + self.config.refresh_token_expires()

            rt = RefreshToken(
                user_id=user_id,
                jti=jti,
                token_hash=token_hash,
                device_id=device_id,
                ip=ip,
                user_agent=user_agent,
                expires_at=expires_at,
            )
            self.db.add(rt)
            self.db.commit()
            self.db.refresh(rt)
            return raw
        except Exception:
            self.logger.exception("failed to create refresh token for user_id=%s", user_id)
            raise

    def revoke_by_raw(self, raw: str) -> None:
        try:
            h = self._hash(raw)
            token = self.db.query(RefreshToken).filter(RefreshToken.token_hash == h).first()
            if not token:
                return
            token.revoked = True
            token.rotated_at = datetime.now(timezone.utc)
            self.db.add(token)
            self.db.commit()
        except Exception:
            self.logger.exception("failed to revoke refresh token by raw")
            raise

    def rotate(self, raw: str, device_id: Optional[str] = None, ip: Optional[str] = None, user_agent: Optional[str] = None) -> Tuple[str, str]:
        try:
            h = self._hash(raw)
            token = self.db.query(RefreshToken).filter(RefreshToken.token_hash == h).first()
            if not token:
                raise ValueError("refresh token not found")
            now = datetime.now(timezone.utc)
            expires = token.expires_at
            if expires is not None and expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if token.revoked or (expires is not None and expires <= now):
                try:
                    self.revoke_all_for_user_and_device(user_id=token.user_id, device_id=token.device_id)
                except Exception:
                    pass
                raise ValueError("refresh token invalid")

            token.revoked = True
            token.rotated_at = datetime.now(timezone.utc)
            self.db.add(token)
            self.db.commit()

            new_raw = secrets.token_urlsafe(64)
            new_hash = self._hash(new_raw)
            new_jti = str(uuid.uuid4())
            expires_at = datetime.now(timezone.utc) + self.config.refresh_token_expires()

            new_token = RefreshToken(
                user_id=token.user_id,
                jti=new_jti,
                token_hash=new_hash,
                device_id=device_id or token.device_id,
                ip=ip or token.ip,
                user_agent=user_agent or token.user_agent,
                expires_at=expires_at,
                rotated_from=token.id,
            )
            self.db.add(new_token)
            self.db.commit()
            self.db.refresh(new_token)
            return new_raw, token.user_id
        except ValueError:
            raise
        except Exception:
            self.logger.exception("failed to rotate refresh token")
            raise

    def revoke_all_for_user_and_device(self, user_id: str, device_id: Optional[str] = None) -> None:
        try:
            q = self.db.query(RefreshToken).filter(RefreshToken.user_id == user_id)
            if device_id:
                q = q.filter(RefreshToken.device_id == device_id)
            tokens = q.all()
            if not tokens:
                return
            now = datetime.now(timezone.utc)
            for t in tokens:
                t.revoked = True
                t.rotated_at = now
                self.db.add(t)
            self.db.commit()
        except Exception:
            self.logger.exception("failed to revoke all tokens for user_id=%s device_id=%s", user_id, device_id)
            raise

    def lookup_by_raw(self, raw: str) -> Optional[RefreshToken]:
        try:
            h = self._hash(raw)
            token = self.db.query(RefreshToken).filter(RefreshToken.token_hash == h).first()
            return token
        except Exception:
            self.logger.exception("failed to lookup refresh token by raw")
            raise


def get_token_service(db: Session = Depends(get_db)) -> TokenService:
    return TokenService(db)
