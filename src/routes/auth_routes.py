from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.auth.login_schema import LoginSchema
from src.schemas.auth.access_token_response_schema import AccessTokenResponseSchema
from src.services.auth_service import get_auth_service, AuthService


class AuthRoutes:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/auth", tags=["auth"])

        self.router.post("/login", response_model=AccessTokenResponseSchema)(self.login)

    async def login(self, payload: LoginSchema, svc: AuthService = Depends(get_auth_service)):
        user = svc.authenticate_user(payload.username_or_email, payload.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

        token = svc.create_access_token_for_user(user)
        return AccessTokenResponseSchema(access_token=token)


auth_router = AuthRoutes().router
