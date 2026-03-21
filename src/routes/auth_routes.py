from __future__ import annotations

from fastapi import APIRouter, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.auth.access_token_response_schema import AccessTokenResponseSchema
from src.services.auth_service import get_auth_service, AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=AccessTokenResponseSchema)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    response: Response = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.perform_login(form, request=request, response=response)


@router.post("/refresh", response_model=AccessTokenResponseSchema)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.perform_refresh(request=request, response=response)


auth_router = router
