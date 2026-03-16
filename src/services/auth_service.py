from __future__ import annotations
import secrets
from typing import Optional, Tuple
from fastapi import Depends, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models.user import User
from src.utils.password import PasswordManager
from src.utils.jwt_utils import JwtManager
from src.config.settings import get_db
from src.config.jwt_config import JwtConfig
from src.config.logger import get_logger
from src.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    InvalidTokenPayloadException,
    UserNotFoundInTokenException,
    RefreshTokenMissingException,
    InvalidCsrfTokenException,
    DeviceMismatchException,
    RefreshTokenInvalidException,
)
from src.schemas.auth.access_token_response_schema import AccessTokenResponseSchema
from src.services.token_service import TokenService
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthService:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db
        self.password_manager = PasswordManager()
        self.jwt_manager = JwtManager()
        self.token_service = TokenService(db)
        self.jwt_config = JwtConfig()
        self.logger = get_logger(self.__class__.__name__)

    def authenticate_user(
        self, username_or_email: str, password: str
    ) -> User:
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
                raise InvalidCredentialsException()
            if not self.password_manager.verify(password, user.password_hash):
                self.logger.info("authentication failed: invalid password for %s", username_or_email)
                raise InvalidCredentialsException()
            self.logger.info("authenticated user id=%s username=%s", getattr(user, "id", None), user.username)
            return user
        except InvalidCredentialsException:
            raise
        except Exception:
            self.logger.exception("error during authenticate_user for %s", username_or_email)
            raise

    def create_access_token_for_user(self, user: User) -> str:
        try:
            token = self.jwt_manager.create_access_token(subject=str(user.id), username=user.username)
            self.logger.info("created access token for user id=%s", getattr(user, "id", None))
            return token
        except Exception:
            self.logger.exception("failed to create access token for user id=%s", getattr(user, "id", None))
            raise

    def perform_login(
        self,
        form: OAuth2PasswordRequestForm,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> AccessTokenResponseSchema:
        try:
            user = self.authenticate_user(form.username, form.password)
            access_token = self.create_access_token_for_user(user)
            if request and response and self.token_service:
                self._setup_refresh_token_and_cookies(user, request, response)
            return AccessTokenResponseSchema(access_token=access_token)
        except Exception:
            self.logger.exception("error during perform_login")
            raise

    def perform_refresh(
        self,
        request: Request,
        response: Response,
    ) -> AccessTokenResponseSchema:
        try:
            cookie_name = self.jwt_config.refresh_cookie_name
            raw_refresh = request.cookies.get(cookie_name)
            if not raw_refresh:
                raise RefreshTokenMissingException()
            
            self._validate_csrf_token(request)
            
            new_raw, user_id = self._validate_and_rotate_token(request, raw_refresh, self.token_service)
            user = self.db.get(User, user_id)
            if not user:
                raise UserNotFoundInTokenException(user_id)
            
            access_token = self.create_access_token_for_user(user)
            
            self._update_refresh_cookies(response, new_raw)
            
            return AccessTokenResponseSchema(access_token=access_token)
        except Exception:
            self.logger.exception("error during perform_refresh")
            raise

    def _setup_refresh_token_and_cookies(
        self,
        user: User,
        request: Request,
        response: Response,
    ) -> None:
        cookie_name = self.jwt_config.refresh_cookie_name
        
        existing_raw = request.cookies.get(cookie_name)
        
        if existing_raw:
            existing_rt = self.token_service.lookup_by_raw(existing_raw)
            if existing_rt and existing_rt.is_active():
                raw_refresh = existing_raw
            else:
                raw_refresh = self._create_new_refresh_token(user, request, self.token_service)
        else:
            raw_refresh = self._create_new_refresh_token(user, request, self.token_service)
        
        self._set_refresh_cookie(response, raw_refresh)
        
        self._setup_csrf_cookie(request, response)

    def _create_new_refresh_token(self, user: User, request: Request) -> str:
        return self.token_service.create_refresh_token(
            user_id=str(user.id),
            device_id=request.headers.get("x-device-id") if request else None,
            ip=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )

    def _set_refresh_cookie(self, response: Response, raw_refresh: str) -> None:
        max_age = int(self.jwt_config.refresh_token_expires().total_seconds())
        cookie_name = self.jwt_config.refresh_cookie_name
        
        response.set_cookie(
            key=cookie_name,
            value=raw_refresh,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=max_age,
            path="/",
            domain=self.jwt_config.refresh_cookie_domain or None,
        )

    def _setup_csrf_cookie(self, request: Request, response: Response) -> None:
        csrf_cookie_name = self.jwt_config.refresh_csrf_cookie_name
        max_age = int(self.jwt_config.refresh_token_expires().total_seconds())

        existing_csrf = request.cookies.get(csrf_cookie_name)
        csrf_value = existing_csrf if existing_csrf else secrets.token_urlsafe(32)
        
        response.set_cookie(
            key=csrf_cookie_name,
            value=csrf_value,
            httponly=False,
            secure=True,
            samesite="lax",
            max_age=max_age,
            path="/",
            domain=self.jwt_config.refresh_cookie_domain or None,
        )

    def _validate_csrf_token(self, request: Request) -> None:
        csrf_cookie_name = self.jwt_config.refresh_csrf_cookie_name
        csrf_cookie = request.cookies.get(csrf_cookie_name)
        csrf_header = request.headers.get("x-csrf-token")
        
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            raise InvalidCsrfTokenException()

    def _validate_and_rotate_token(
        self, 
        request: Request, 
        raw_refresh: str, 
    ) -> Tuple[str, str]:
        device_header = request.headers.get("x-device-id")
        lookup = self.token_service.lookup_by_raw(raw_refresh)
        
        if lookup is None:
            raise RefreshTokenInvalidException("Refresh token not found")
        
        if getattr(lookup, "device_id", None) and device_header and lookup.device_id != device_header:
            try:
                self.token_service.revoke_all_for_user_and_device(
                    user_id=lookup.user_id, 
                    device_id=lookup.device_id
                )
            except Exception:
                pass
            raise DeviceMismatchException()

        try:
            new_raw, user_id = self.token_service.rotate(
                raw_refresh,
                device_id=device_header if device_header else None,
                ip=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None,
            )
            return new_raw, user_id
        except ValueError as exc:
            raise RefreshTokenInvalidException(str(exc)) from exc

    def _update_refresh_cookies(self, response: Response, new_raw: str) -> None:
        
        self._set_refresh_cookie(response, new_raw)
        csrf_cookie_name = self.jwt_config.refresh_csrf_cookie_name
        max_age = int(self.jwt_config.refresh_token_expires().total_seconds())
        new_csrf = secrets.token_urlsafe(32)
        
        response.set_cookie(
            key=csrf_cookie_name,
            value=new_csrf,
            httponly=False,
            secure=True,
            samesite="lax",
            max_age=max_age,
            path="/",
            domain=self.jwt_config.refresh_cookie_domain or None,
        )

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

logger = get_logger("AuthService")

async def get_current_user(
    token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)
) -> User:
    try:
        payload = auth_service.jwt_manager.decode_token(token)
    except ValueError as exc:
        logger.warning("invalid authentication credentials: %s", str(exc))
        raise InvalidTokenException(str(exc))

    sub = payload.get("sub")
    if not sub:
        logger.warning("invalid token payload: missing 'sub'")
        raise InvalidTokenPayloadException("Missing 'sub' claim in token")

    user = auth_service.db.get(User, sub)
    if not user:
        logger.warning("user not found for sub=%s", sub)
        raise UserNotFoundInTokenException(sub)

    logger.info("retrieved current user id=%s", getattr(user, "id", None))
    return user
