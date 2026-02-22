from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.role import Role
from src.schemas.role.role_create_schema import RoleCreateSchema
from src.schemas.role.role_update_schema import RoleUpdateSchema
from fastapi import Depends
from src.config.settings import get_db


class RoleService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_by_filter(self, **kwargs) -> Optional[Role]:
        return self.db.query(Role).filter_by(**kwargs).first()

    def get(self, role_id: str) -> Optional[Role]:
        return self.db.get(Role, role_id)

    def get_by_name(self, name: str) -> Optional[Role]:
        return self._get_by_filter(name=name)

    def list(self, skip: int = 0, limit: int = 100) -> List[Role]:
        return self.db.query(Role).offset(skip).limit(limit).all()

    def create(self, *, role_in: RoleCreateSchema) -> Role:
        if self.get_by_name(role_in.name):
            raise ValueError("name already exists")

        role = Role(name=role_in.name, description=role_in.description)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update(self, role: Role, *, role_in: RoleUpdateSchema) -> Role:
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

        return role

    def delete(self, role: Role) -> None:
        self.db.delete(role)
        self.db.commit()


def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    return RoleService(db)
