from __future__ import annotations

from typing import Optional

from fastapi import Depends

from src.models.user import User
from src.services.auth_service import get_current_user
from src.exceptions import AdminPrivilegesRequiredException


class AdminPermission:
    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        role = getattr(current_user, "role", None)
        name = getattr(role, "name", None)
        if not name or name.lower() != "admin":
            raise AdminPrivilegesRequiredException()
        return current_user

    def ensure(self, user: Optional[User]) -> None:
        if not user:
            raise AdminPrivilegesRequiredException()
        role = getattr(user, "role", None)
        name = getattr(role, "name", None)
        if not name or name.lower() != "admin":
            raise AdminPrivilegesRequiredException()

admin_permission = AdminPermission()
