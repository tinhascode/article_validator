from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.user import User
from src.models.role import Role
from src.schemas.user.user_create_schema import UserCreateSchema
from src.schemas.user.user_update_schema import UserUpdateSchema
from src.utils.password import PasswordManager
from fastapi import Depends
from src.config.settings import get_db
from src.utils.cpf_validator import CPFValidator
from src.config.logger import get_logger


class UserService:
    def __init__(
        self, db: Session, password_manager: Optional[PasswordManager] = None
    ) -> None:
        self.db = db
        self.pwd = password_manager or PasswordManager()
        self.cpf_validator = CPFValidator()
        self.logger = get_logger(self.__class__.__name__)

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
        self.logger.info("listing users skip=%d limit=%d", skip, limit)
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, *, user_in: UserCreateSchema) -> User:
        cpf_clean = self.cpf_validator.clean(user_in.cpf)
        if not self.cpf_validator.is_valid(cpf_clean):
            self.logger.warning("invalid cpf for username=%s", user_in.username)
            raise ValueError("invalid cpf")

        if self.get_by_username(user_in.username):
            self.logger.warning("attempt to create user with existing username=%s", user_in.username)
            raise ValueError("username already exists")
        if self.get_by_email(user_in.email):
            self.logger.warning("attempt to create user with existing email=%s", user_in.email)
            raise ValueError("email already exists")
        if self.get_by_cpf(cpf_clean):
            self.logger.warning("attempt to create user with existing cpf=%s", cpf_clean)
            raise ValueError("cpf already exists")

        password_hash = self.pwd.hash(user_in.password)
        if getattr(user_in, "role_id", None) is not None:
            if user_in.role_id and not self.db.get(Role, user_in.role_id):
                self.logger.warning("attempt to create user with non-existing role_id=%s", user_in.role_id)
                raise ValueError("role not found")

        user = User(
            name=user_in.name,
            username=user_in.username,
            email=user_in.email,
            password_hash=password_hash,
            cpf=cpf_clean,
            birthday=user_in.birthday,
            role_id=getattr(user_in, "role_id", None),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        self.logger.info("created user id=%s username=%s", getattr(user, "id", None), user.username)
        return user

    def update(self, user: User, *, user_in: UserUpdateSchema) -> User:
        changed = False
        if getattr(user_in, "cpf", None) is not None:
            raise ValueError("cpf cannot be updated")
        if user_in.name is not None:
            user.name = user_in.name
            changed = True
        if user_in.username is not None:
            existing = self.get_by_username(user_in.username)
            if existing and getattr(existing, "id", None) != getattr(user, "id", None):
                self.logger.warning("attempt to update user with existing username=%s", user_in.username)
                raise ValueError("username already exists")
            user.username = user_in.username
            changed = True
        if getattr(user_in, "role_id", None) is not None:
            if user_in.role_id and not self.db.get(Role, user_in.role_id):
                self.logger.warning("attempt to update user with non-existing role_id=%s", user_in.role_id)
                raise ValueError("role not found")
            user.role_id = user_in.role_id
            changed = True

        if changed:
            user.touch()
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        self.logger.info("updated user id=%s", getattr(user, "id", None))
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
        self.logger.info("deleted user id=%s", getattr(user, "id", None))


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)
