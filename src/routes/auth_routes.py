from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
import secrets

from src.schemas.auth.login_schema import LoginSchema
from src.schemas.auth.access_token_response_schema import AccessTokenResponseSchema
from src.services.auth_service import get_auth_service, AuthService
from src.services.token_service import get_token_service, TokenService
from src.config.jwt_config import JwtConfig
from src.models.user import User
from fastapi import Cookie


class AuthRoutes:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/auth", tags=["auth"])

        self.router.post("/login", response_model=AccessTokenResponseSchema)(self.login)
        self.router.post("/refresh", response_model=AccessTokenResponseSchema)(self.refresh)

    async def login(
        self,
        form: OAuth2PasswordRequestForm = Depends(),
        request: Request = None,
        response: Response = None,
        svc: AuthService = Depends(get_auth_service),
        token_svc: TokenService = Depends(get_token_service),
    ):
        username_or_email = form.username
        password = form.password
        user = svc.authenticate_user(username_or_email, password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

        token = svc.create_access_token_for_user(user)
        cfg = JwtConfig()
        cookie_name = cfg.refresh_cookie_name or "refresh_token"

        existing_raw = None
        if request:
            existing_raw = request.cookies.get(cookie_name)

        if existing_raw:
            existing_rt = token_svc.lookup_by_raw(existing_raw)
            if existing_rt and existing_rt.is_active():
                raw_refresh = existing_raw
            else:
                raw_refresh = token_svc.create_refresh_token(
                    user_id=str(user.id),
                    device_id=(request.headers.get("x-device-id") if request else None),
                    ip=(request.client.host if request and request.client else None),
                    user_agent=(request.headers.get("user-agent") if request else None),
                )
        else:
            raw_refresh = token_svc.create_refresh_token(
                user_id=str(user.id),
                device_id=(request.headers.get("x-device-id") if request else None),
                ip=(request.client.host if request and request.client else None),
                user_agent=(request.headers.get("user-agent") if request else None),
            )
        max_age = int(cfg.refresh_token_expires().total_seconds())
        cookie_name = cfg.refresh_cookie_name or "refresh_token"
        response.set_cookie(
            key=cookie_name,
            value=raw_refresh,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=max_age,
            path="/",
            domain=cfg.refresh_cookie_domain or None,
        )

        csrf_cookie_name = getattr(cfg, "refresh_csrf_cookie_name", None) or "refresh_csrf"
        existing_csrf = None
        if request:
            existing_csrf = request.cookies.get(csrf_cookie_name)
        if existing_csrf:
            csrf_value = existing_csrf
        else:
            csrf_value = secrets.token_urlsafe(32)
        response.set_cookie(
            key=csrf_cookie_name,
            value=csrf_value,
            httponly=False,
            secure=True,
            samesite="lax",
            max_age=max_age,
            path="/",
            domain=cfg.refresh_cookie_domain or None,
        )

        return AccessTokenResponseSchema(access_token=token)

    async def refresh(
        self,
        request: Request,
        response: Response,
        svc: AuthService = Depends(get_auth_service),
        token_svc: TokenService = Depends(get_token_service),
    ):
        cfg = JwtConfig()
        cookie_name = cfg.refresh_cookie_name or "refresh_token"
        raw_refresh = request.cookies.get(cookie_name)
        if not raw_refresh:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token missing")
        
        csrf_cookie_name = getattr(cfg, "refresh_csrf_cookie_name", None) or "refresh_csrf"
        csrf_cookie = request.cookies.get(csrf_cookie_name)
        csrf_header = request.headers.get("x-csrf-token")
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid csrf token")

        device_header = request.headers.get("x-device-id")
        lookup = token_svc.lookup_by_raw(raw_refresh)
        if lookup is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token")
        if getattr(lookup, "device_id", None) and device_header and lookup.device_id != device_header:
            try:
                token_svc.revoke_all_for_user_and_device(user_id=lookup.user_id, device_id=lookup.device_id)
            except Exception:
                pass
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="device mismatch")

        try:
            new_raw, user_id = token_svc.rotate(
                raw_refresh,
                device_id=(device_header if device_header else None),
                ip=(request.client.host if request and request.client else None),
                user_agent=(request.headers.get("user-agent") if request else None),
            )
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token")

        user = svc.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")

        access_token = svc.create_access_token_for_user(user)

        max_age = int(cfg.refresh_token_expires().total_seconds())
        cookie_name = cfg.refresh_cookie_name or "refresh_token"
        response.set_cookie(
            key=cookie_name,
            value=new_raw,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=max_age,
            path="/",
            domain=cfg.refresh_cookie_domain or None,
        )
        
        csrf_cookie_name = getattr(cfg, "refresh_csrf_cookie_name", None) or "refresh_csrf"
        new_csrf = secrets.token_urlsafe(32)
        response.set_cookie(
            key=csrf_cookie_name,
            value=new_csrf,
            httponly=False,
            secure=True,
            samesite="lax",
            max_age=max_age,
            path="/",
            domain=cfg.refresh_cookie_domain or None,
        )

        return AccessTokenResponseSchema(access_token=access_token)


auth_router = AuthRoutes().router
