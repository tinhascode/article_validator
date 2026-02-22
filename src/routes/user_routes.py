from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.user.user_create_schema import UserCreateSchema
from src.schemas.user.user_read_schema import UserReadSchema
from src.schemas.user.user_response_schema import UserResponseSchema
from src.schemas.user.user_update_schema import UserUpdateSchema
from src.services.user_service import UserService, get_user_service



class UserRoutes:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/users", tags=["users"])

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
        self, user_in: UserCreateSchema, svc: UserService = Depends(get_user_service)
    ):
        try:
            user = svc.create(user_in=user_in)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            )
        return {"message": "user created", "user": UserReadSchema.from_orm(user)}

    async def list_users(
        self, svc: UserService = Depends(get_user_service)
    ) -> List[UserReadSchema]:
        users = svc.list()
        return [UserReadSchema.from_orm(u) for u in users]

    async def get_user(
        self, user_id: str, svc: UserService = Depends(get_user_service)
    ) -> UserReadSchema:
        user = svc.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )
        return UserReadSchema.from_orm(user)

    async def update_user(
        self,
        user_id: str,
        payload: UserUpdateSchema,
        svc: UserService = Depends(get_user_service),
    ) -> UserReadSchema:
        user = svc.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )
        updated = svc.update(user, user_in=payload)
        return UserReadSchema.from_orm(updated)

    async def delete_user(
        self, user_id: str, svc: UserService = Depends(get_user_service)
    ) -> None:
        user = svc.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )
        svc.delete(user)


user_router = UserRoutes().router
