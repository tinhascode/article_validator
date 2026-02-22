from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, Date, String

from .base.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String(255), nullable=False)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    cpf = Column(String(32), unique=True, nullable=False)
    birthday = Column(Date, nullable=False)

    def __init__(
        self,
        name: str,
        username: str,
        email: str,
        password_hash: str,
        cpf: str,
        birthday: date,
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "cpf": self.cpf,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "created_at": (
                self.created_at.isoformat()
                if isinstance(self.created_at, datetime)
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if isinstance(self.updated_at, datetime)
                else None
            ),
        }

    def __repr__(self) -> str:
        created = (
            self.created_at.isoformat()
            if isinstance(self.created_at, datetime)
            else "<none>"
        )
        return f"<User id={self.id} username={self.username} name={self.name} created_at={created}>"
