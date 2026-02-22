from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.user.user_create_schema import UserCreateSchema
from src.schemas.user.user_update_schema import UserUpdateSchema
from src.utils.password import PasswordManager
from fastapi import Depends
from src.config.settings import get_db


class UserService:
    def __init__(
        self, db: Session, password_manager: Optional[PasswordManager] = None
    ) -> None:
        self.db = db
        self.pwd = password_manager or PasswordManager()

    def _get_by_filter(self, **kwargs) -> Optional[User]:
        return self.db.query(User).filter_by(**kwargs).first()

    def get(self, user_id: str) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self._get_by_filter(email=email)

    def get_by_username(self, username: str) -> Optional[User]:
        return self._get_by_filter(username=username)

    def get_by_cpf(self, cpf: str) -> Optional[User]:
        return self._get_by_filter(cpf=cpf)

    def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, *, user_in: UserCreateSchema) -> User:
        if self.get_by_username(user_in.username):
            raise ValueError("username already exists")
        if self.get_by_email(user_in.email):
            raise ValueError("email already exists")
        if self.get_by_cpf(user_in.cpf):
            raise ValueError("cpf already exists")

        password_hash = self.pwd.hash(user_in.password)
        user = User(
            name=user_in.name,
            username=user_in.username,
            email=user_in.email,
            password_hash=password_hash,
            cpf=user_in.cpf,
            birthday=user_in.birthday,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username_or_email: str, password: str) -> Optional[User]:
        user = self.get_by_email(username_or_email) or self.get_by_username(
            username_or_email
        )
        if not user:
            return None
        if not self.pwd.verify(password, user.password_hash):
            return None
        return user

    def update(self, user: User, *, user_in: UserUpdateSchema) -> User:
        changed = False
        if user_in.name is not None:
            user.name = user_in.name
            changed = True
        if user_in.username is not None:
            user.username = user_in.username
            changed = True
        if user_in.email is not None:
            user.email = user_in.email
            changed = True
        if user_in.cpf is not None:
            user.cpf = user_in.cpf
            changed = True
        if user_in.birthday is not None:
            user.birthday = user_in.birthday
            changed = True
        if user_in.password is not None:
            user.password_hash = self.pwd.hash(user_in.password)
            changed = True

        if changed:
            user.touch()
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)
