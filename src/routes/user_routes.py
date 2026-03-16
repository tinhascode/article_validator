from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status

from src.schemas.user.user_create_schema import UserCreateSchema
from src.schemas.user.user_read_schema import UserReadSchema
from src.schemas.user.user_response_schema import UserResponseSchema
from src.schemas.user.user_update_schema import UserUpdateSchema
from src.services.user_service import UserService, get_user_service
from src.services.auth_service import get_current_user
from src.models.user import User
from src.utils.permissions import admin_permission



class UserRoutes:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(admin_permission)])

        self.router.post(
            "/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED
        )(self.create_user)
        self.router.get("/", response_model=List[UserReadSchema])(self.list_users)
        self.router.get("/{user_id}", response_model=UserReadSchema)(self.get_user)
        self.router.patch("/{user_id}", response_model=UserReadSchema)(self.update_user)
        self.router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)(
            self.delete_user
        )

    async def create_user(
        self,
        user_in: UserCreateSchema,
        user_service: UserService = Depends(get_user_service),
        current_user: User = Depends(get_current_user),
    ):
        return user_service.create_with_response(user_in=user_in, current_user=current_user)

    async def list_users(
        self, user_service: UserService = Depends(get_user_service)
    ) -> List[UserReadSchema]:
        return user_service.list_with_schema()

    async def get_user(
        self, user_id: str, user_service: UserService = Depends(get_user_service)
    ) -> UserReadSchema:
        return user_service.get_with_schema(user_id)

    async def update_user(
        self,
        user_id: str,
        payload: UserUpdateSchema,
        user_service: UserService = Depends(get_user_service),
        current_user: User = Depends(get_current_user),
    ) -> UserReadSchema:
        return user_service.update_with_validation(user_id, payload, current_user)

    async def delete_user(
        self, user_id: str, user_service: UserService = Depends(get_user_service), current_user: User = Depends(get_current_user)
    ) -> None:
        user_service.delete_with_validation(user_id, current_user)


user_router = UserRoutes().router
