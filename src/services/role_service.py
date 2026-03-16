from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.role import Role
from src.schemas.role.role_create_schema import RoleCreateSchema
from src.schemas.role.role_update_schema import RoleUpdateSchema
from fastapi import Depends
from src.config.settings import get_db
from src.config.logger import get_logger
from typing import Optional as _Optional
from src.models.user import User as _User
from src.utils.permissions import admin_permission
from src.exceptions.roles.role_exceptions import (
    RoleNotFoundException,
    RoleAlreadyExistsException,
)
from src.schemas.role.role_response_schema import RoleResponseSchema
from src.schemas.role.role_read_schema import RoleReadSchema

class RoleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = get_logger(self.__class__.__name__)

    def _get_by_filter(self, **kwargs) -> Optional[Role]:
        try:
            self.logger.info("fetching role by filter: %s", kwargs)
            return self.db.query(Role).filter_by(**kwargs).first()
        except Exception:
            self.logger.exception("error fetching role by filter: %s", kwargs)
            raise

    def get(self, role_id: str) -> Optional[Role]:
        try:
            self.logger.info("fetching role by id=%s", role_id)
            return self.db.get(Role, role_id)
        except Exception:
            self.logger.exception("error getting role id=%s", role_id)
            raise

    def get_by_name(self, name: str) -> Optional[Role]:
        try:
            self.logger.info("fetching role by name=%s", name)
            return self._get_by_filter(name=name)
        except Exception:
            self.logger.exception("error getting role by name=%s", name)
            raise

    def list(self, skip: int = 0, limit: int = 100) -> List[Role]:
        try:
            self.logger.info("listing roles skip=%d limit=%d", skip, limit)
            return self.db.query(Role).offset(skip).limit(limit).all()
        except Exception:
            self.logger.exception("error listing roles skip=%d limit=%d", skip, limit)
            raise

    def create(self, *, role_in: RoleCreateSchema, current_user: _Optional[_User] = None) -> Role:
        try:
            admin_permission.ensure(current_user)
            if self.get_by_name(role_in.name):
                self.logger.warning("attempt to create role with existing name=%s", role_in.name)
                raise RoleAlreadyExistsException(role_in.name)

            role = Role(name=role_in.name, description=role_in.description)
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
            self.logger.info("created role id=%s name=%s", getattr(role, "id", None), role.name)
            return role
        except RoleAlreadyExistsException:
            raise
        except Exception:
            self.logger.exception("failed to create role name=%s", getattr(role_in, "name", None))
            raise

    def get_with_validation(self, role_id: str) -> Role:
        role = self.get(role_id)
        if not role:
            raise RoleNotFoundException(role_id)
        return role

    def create_with_response(self, *, role_in: RoleCreateSchema, current_user: _Optional[_User] = None) -> RoleResponseSchema:
        role = self.create(role_in=role_in, current_user=current_user)
        return RoleResponseSchema(
            message="role created", 
            role=RoleReadSchema.from_orm(role)
        )

    def list_with_schema(self, skip: int = 0, limit: int = 100) -> list[RoleReadSchema]:
        roles = self.list(skip, limit)
        return [RoleReadSchema.from_orm(r) for r in roles]

    def get_with_schema(self, role_id: str) -> RoleReadSchema:
        role = self.get_with_validation(role_id)
        return RoleReadSchema.from_orm(role)

    def update_with_validation(
        self,
        role_id: str,
        role_in: RoleUpdateSchema,
        current_user: _Optional[_User] = None
    ) -> RoleReadSchema:
        role = self.get_with_validation(role_id)
        updated_role = self.update(role, role_in=role_in, current_user=current_user)
        return RoleReadSchema.from_orm(updated_role)

    def delete_with_validation(self, role_id: str, current_user: _Optional[_User] = None) -> None:
        role = self.get_with_validation(role_id)
        self.delete(role, current_user=current_user)

    def update(self, role: Role, *, role_in: RoleUpdateSchema, current_user: _Optional[_User] = None) -> Role:
        try:
            admin_permission.ensure(current_user)
            changed = False
            if role_in.name is not None:
                role.name = role_in.name
                changed = True
            if role_in.description is not None:
                role.description = role_in.description
                changed = True

            if changed:
                role.touch()
                self.db.add(role)
                self.db.commit()
                self.db.refresh(role)

            self.logger.info("updated role id=%s", getattr(role, "id", None))
            return role
        except Exception:
            self.logger.exception("error updating role id=%s", getattr(role, "id", None))
            raise

    def delete(self, role: Role, current_user: _Optional[_User] = None) -> None:
        try:
            admin_permission.ensure(current_user)
            self.db.delete(role)
            self.db.commit()
            self.logger.info("deleted role id=%s", getattr(role, "id", None))
        except Exception:
            self.logger.exception("error deleting role id=%s", getattr(role, "id", None))
            raise

def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    return RoleService(db)
