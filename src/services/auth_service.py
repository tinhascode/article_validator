from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.models.user import User
from src.utils.password import PasswordManager
from src.utils.jwt_utils import JwtManager
from src.config.settings import get_db
from src.config.logger import get_logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthService:
    def __init__(
        self,
        db: Session,
        pwd_manager: Optional[PasswordManager] = None,
        jwt_manager: Optional[JwtManager] = None,
    ) -> None:
        self.db = db
        self.pwd = pwd_manager or PasswordManager()
        self.jwt = jwt_manager or JwtManager()
        self.logger = get_logger(self.__class__.__name__)

    def authenticate_user(
        self, username_or_email: str, password: str
    ) -> Optional[User]:
        try:
            user = (
                self.db.query(User)
                .filter(
                    or_(User.username == username_or_email, User.email == username_or_email)
                )
                .first()
            )
            if not user:
                self.logger.info("authentication failed: user not found for %s", username_or_email)
                return False
            if not self.pwd.verify(password, user.password_hash):
                self.logger.info("authentication failed: invalid password for %s", username_or_email)
                return False
            self.logger.info("authenticated user id=%s username=%s", getattr(user, "id", None), user.username)
            return user
        except Exception:
            self.logger.exception("error during authenticate_user for %s", username_or_email)
            raise

    def create_access_token_for_user(self, user: User) -> str:
        try:
            token = self.jwt.create_access_token(subject=str(user.id), username=user.username)
            self.logger.info("created access token for user id=%s", getattr(user, "id", None))
            return token
        except Exception:
            self.logger.exception("failed to create access token for user id=%s", getattr(user, "id", None))
            raise


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


logger = get_logger("AuthService")


async def get_current_user(
    token: str = Depends(oauth2_scheme), svc: AuthService = Depends(get_auth_service)
) -> User:
    try:
        payload = svc.jwt.decode_token(token)
    except ValueError as exc:
        logger.warning("invalid authentication credentials: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    sub = payload.get("sub")
    if not sub:
        logger.warning("invalid token payload: missing 'sub'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    user = svc.db.get(User, sub)
    if not user:
        logger.warning("user not found for sub=%s", sub)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    logger.info("retrieved current user id=%s", getattr(user, "id", None))
    return user
