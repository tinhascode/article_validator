from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, Date, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String(255), nullable=False)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    cpf = Column(String(32), unique=True, nullable=False)
    birthday = Column(Date, nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", backref="users")

    def __init__(
        self,
        name: str,
        username: str,
        email: str,
        password_hash: str,
        cpf: str,
        birthday: date,
        role_id: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.name = name
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.cpf = cpf
        self.birthday = birthday
        self.role_id = role_id