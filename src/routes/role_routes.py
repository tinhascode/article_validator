from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status

from src.schemas.role.role_create_schema import RoleCreateSchema
from src.schemas.role.role_read_schema import RoleReadSchema
from src.schemas.role.role_response_schema import RoleResponseSchema
from src.schemas.role.role_update_schema import RoleUpdateSchema
from src.services.role_service import RoleService, get_role_service
from src.services.auth_service import get_current_user
from src.utils.permissions import admin_permission
from src.models.user import User


class RoleRoutes:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/roles", tags=["roles"], dependencies=[Depends(admin_permission)])

        self.router.post(
            "/", response_model=RoleResponseSchema, status_code=status.HTTP_201_CREATED
        )(self.create_role)
        self.router.get("/", response_model=List[RoleReadSchema])(self.list_roles)
        self.router.get("/{role_id}", response_model=RoleReadSchema)(self.get_role)
        self.router.patch("/{role_id}", response_model=RoleReadSchema)(self.update_role)
        self.router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)(
            self.delete_role
        )

    async def create_role(
        self,
        role_in: RoleCreateSchema,
        role_service: RoleService = Depends(get_role_service),
        current_user: User = Depends(get_current_user),
    ):
        return role_service.create_with_response(role_in=role_in, current_user=current_user)

    async def list_roles(self, svc: RoleService = Depends(get_role_service)) -> List[RoleReadSchema]:
        return svc.list_with_schema()

    async def get_role(self, role_id: str, svc: RoleService = Depends(get_role_service)) -> RoleReadSchema:
        return svc.get_with_schema(role_id)

    async def update_role(
        self,
        role_id: str,
        payload: RoleUpdateSchema,
        role_service: RoleService = Depends(get_role_service),
        current_user: User = Depends(get_current_user),
    ) -> RoleReadSchema:
        return role_service.update_with_validation(role_id, payload, current_user)

    async def delete_role(self, role_id: str, role_service: RoleService = Depends(get_role_service), current_user: User = Depends(get_current_user)) -> None:
        role_service.delete_with_validation(role_id, current_user)


role_router = RoleRoutes().router
