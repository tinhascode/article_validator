from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status

from src.models.user import User
from src.services.auth_service import get_current_user


class AdminPermission:
    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        role = getattr(current_user, "role", None)
        name = getattr(role, "name", None)
        if not name or name.lower() != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="admin privileges required",
            )
        return current_user

    def ensure(self, user: Optional[User]) -> None:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="admin privileges required",
            )
        role = getattr(user, "role", None)
        name = getattr(role, "name", None)
        if not name or name.lower() != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="admin privileges required",
            )

admin_permission = AdminPermission()
