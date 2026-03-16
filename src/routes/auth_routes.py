from __future__ import annotations

from fastapi import APIRouter, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.auth.access_token_response_schema import AccessTokenResponseSchema
from src.services.auth_service import get_auth_service, AuthService
from src.services.token_service import get_token_service, TokenService


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
        auth_service: AuthService = Depends(get_auth_service),
        token_service: TokenService = Depends(get_token_service),
    ):
        return auth_service.perform_login(
            form=form,
            request=request,
            response=response,
        )

    async def refresh(
        self,
        request: Request,
        response: Response,
        auth_service: AuthService = Depends(get_auth_service),
        token_service: TokenService = Depends(get_token_service),
    ):
        return auth_service.perform_refresh(
            request=request,
            response=response,
            token_service=token_service
        )


auth_router = AuthRoutes().router
