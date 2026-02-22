from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.role.role_create_schema import RoleCreateSchema
from src.schemas.role.role_read_schema import RoleReadSchema
from src.schemas.role.role_response_schema import RoleResponseSchema
from src.schemas.role.role_update_schema import RoleUpdateSchema
from src.services.role_service import RoleService, get_role_service
from src.services.auth_service import get_current_user


class RoleRoutes:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/roles", tags=["roles"], dependencies=[Depends(get_current_user)])

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
        self, role_in: RoleCreateSchema, svc: RoleService = Depends(get_role_service)
    ):
        try:
            role = svc.create(role_in=role_in)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            )
        return {"message": "role created", "role": RoleReadSchema.from_orm(role)}

    async def list_roles(self, svc: RoleService = Depends(get_role_service)) -> List[RoleReadSchema]:
        roles = svc.list()
        return [RoleReadSchema.from_orm(r) for r in roles]

    async def get_role(self, role_id: str, svc: RoleService = Depends(get_role_service)) -> RoleReadSchema:
        role = svc.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="role not found"
            )
        return RoleReadSchema.from_orm(role)

    async def update_role(
        self,
        role_id: str,
        payload: RoleUpdateSchema,
        svc: RoleService = Depends(get_role_service),
    ) -> RoleReadSchema:
        role = svc.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="role not found"
            )
        updated = svc.update(role, role_in=payload)
        return RoleReadSchema.from_orm(updated)

    async def delete_role(self, role_id: str, svc: RoleService = Depends(get_role_service)) -> None:
        role = svc.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="role not found"
            )
        svc.delete(role)


role_router = RoleRoutes().router
