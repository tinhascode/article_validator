from __future__ import annotations

# Base exception
from src.exceptions.base_exception import BaseServiceException

# Auth exceptions  
from src.exceptions.auth.auth_exceptions import (
    InvalidCredentialsException,
    InvalidTokenPayloadException,
    InvalidTokenException,
    UserNotFoundInTokenException,
    AdminPrivilegesRequiredException,
)

# User exceptions
from src.exceptions.users.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCpfException,
    CpfUpdateNotAllowedException,
    RoleNotFoundForUserException,
)

# Role exceptions
from src.exceptions.roles.role_exceptions import (
    RoleNotFoundException,
    RoleAlreadyExistsException,
)

# Token exceptions
from src.exceptions.token.token_exceptions import (
    RefreshTokenNotFoundException,
    RefreshTokenInvalidException,
    RefreshTokenMissingException,
    InvalidCsrfTokenException,
    DeviceMismatchException,
)

__all__ = [
    # Base
    "BaseServiceException",
    # Auth
    "InvalidCredentialsException",
    "InvalidTokenPayloadException", 
    "InvalidTokenException",
    "UserNotFoundInTokenException",
    "AdminPrivilegesRequiredException",
    # Users
    "UserNotFoundException",
    "UserAlreadyExistsException",
    "InvalidCpfException",
    "CpfUpdateNotAllowedException", 
    "RoleNotFoundForUserException",
    # Roles
    "RoleNotFoundException",
    "RoleAlreadyExistsException",
    # Tokens
    "RefreshTokenNotFoundException",
    "RefreshTokenInvalidException",
    "RefreshTokenMissingException",
    "InvalidCsrfTokenException",
    "DeviceMismatchException",
]