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
from typing import Optional as _Optional
from src.models.user import User as _User
from src.utils.permissions import admin_permission
from src.exceptions.users.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCpfException,
    CpfUpdateNotAllowedException,
    RoleNotFoundForUserException,
)
from src.schemas.user.user_response_schema import UserResponseSchema
from src.schemas.user.user_read_schema import UserReadSchema


class UserService:
    def __init__(
        self, db: Session
    ) -> None:
        self.db = db
        self.password_manager = PasswordManager()
        self.cpf_validator = CPFValidator()
        self.logger = get_logger(self.__class__.__name__)

    def _get_by_filter(self, **kwargs) -> Optional[User]:
        try:
            self.logger.info("fetching user by filter: %s", kwargs)
            return self.db.query(User).filter_by(**kwargs).first()
        except Exception:
            self.logger.exception("error fetching user by filter: %s", kwargs)
            raise

    def get(self, user_id: str) -> Optional[User]:
        try:
            self.logger.info("fetching user by id=%s", user_id)
            return self.db.get(User, user_id)
        except Exception:
            self.logger.exception("error getting user id=%s", user_id)
            raise

    def get_by_email(self, email: str) -> Optional[User]:
        try:
            self.logger.info("fetching user by email=%s", email)
            return self._get_by_filter(email=email)
        except Exception:
            self.logger.exception("error getting user by email=%s", email)
            raise

    def get_by_username(self, username: str) -> Optional[User]:
        try:
            self.logger.info("fetching user by username=%s", username)
            return self._get_by_filter(username=username)
        except Exception:
            self.logger.exception("error getting user by username=%s", username)
            raise

    def get_by_cpf(self, cpf: str) -> Optional[User]:
        try:
            self.logger.info("fetching user by cpf=%s", cpf)
            return self._get_by_filter(cpf=cpf)
        except Exception:
            self.logger.exception("error getting user by cpf=%s", cpf)
            raise

    def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            self.logger.info("listing users skip=%d limit=%d", skip, limit)
            return self.db.query(User).offset(skip).limit(limit).all()
        except Exception:
            self.logger.exception("error listing users skip=%d limit=%d", skip, limit)
            raise

    def create(self, *, user_in: UserCreateSchema, current_user: _Optional[_User] = None) -> User:
        try:
            admin_permission.ensure(current_user)
            cpf_clean = self.cpf_validator.clean(user_in.cpf)
            
            self.logger.info("creating user with cpf=%s", cpf_clean)
            if not self.cpf_validator.is_valid(cpf_clean):
                self.logger.warning("invalid cpf for username=%s", user_in.username)
                raise InvalidCpfException(cpf_clean)
            
            if self.get_by_username(user_in.username):
                self.logger.warning("attempt to create user with existing username=%s", user_in.username)
                raise UserAlreadyExistsException("username", user_in.username)
            
            if self.get_by_email(user_in.email):
                self.logger.warning("attempt to create user with existing email=%s", user_in.email)
                raise UserAlreadyExistsException("email", user_in.email)
            
            if self.get_by_cpf(cpf_clean):
                self.logger.warning("attempt to create user with existing cpf=%s", cpf_clean)
                raise UserAlreadyExistsException("cpf", cpf_clean)

            password_hash = self.password_manager.hash(user_in.password)
            if getattr(user_in, "role_id", None) is not None:
                if user_in.role_id and not self.db.get(Role, user_in.role_id):
                    self.logger.warning("attempt to create user with non-existing role_id=%s", user_in.role_id)
                    raise RoleNotFoundForUserException(user_in.role_id)

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
        except (UserAlreadyExistsException, InvalidCpfException, RoleNotFoundForUserException):
            raise
        except Exception:
            self.logger.exception("error creating user username=%s", getattr(user_in, "username", None))
            raise

    def get_with_validation(self, user_id: str) -> User:
        user = self.get(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user

    def create_with_response(self, *, user_in: UserCreateSchema, current_user: _Optional[_User] = None) -> UserResponseSchema:
        user = self.create(user_in=user_in, current_user=current_user)
        return UserResponseSchema(
            message="user created", 
            user=UserReadSchema.from_orm(user)
        )

    def list_with_schema(self, skip: int = 0, limit: int = 100) -> list[UserReadSchema]:
        users = self.list(skip, limit)
        return [UserReadSchema.from_orm(u) for u in users]

    def get_with_schema(self, user_id: str) -> UserReadSchema:
        user = self.get_with_validation(user_id)
        return UserReadSchema.from_orm(user)

    def update_with_validation(
        self,
        user_id: str,
        user_in: UserUpdateSchema,
        current_user: _Optional[_User] = None
    ) -> UserReadSchema:
        user = self.get_with_validation(user_id)
        updated_user = self.update(user, user_in=user_in, current_user=current_user)
        return UserReadSchema.from_orm(updated_user)

    def delete_with_validation(self, user_id: str, current_user: _Optional[_User] = None) -> None:
        user = self.get_with_validation(user_id)
        self.delete(user, current_user=current_user)

    def update(self, user: User, *, user_in: UserUpdateSchema, current_user: _Optional[_User] = None) -> User:
        try:
            self.logger.info("updating user id=%s", getattr(user, "id", None))
            admin_permission.ensure(current_user)
            changed = False
            
            if getattr(user_in, "cpf", None) is not None:
                raise CpfUpdateNotAllowedException()
            
            if user_in.name is not None:
                user.name = user_in.name
                changed = True
                
            if user_in.username is not None:
                existing = self.get_by_username(user_in.username)
                
                if existing and getattr(existing, "id", None) != getattr(user, "id", None):
                    self.logger.warning("attempt to update user with existing username=%s", user_in.username)
                    raise UserAlreadyExistsException("username", user_in.username)
                
                user.username = user_in.username
                changed = True
                
            if getattr(user_in, "role_id", None) is not None:
                if user_in.role_id and not self.db.get(Role, user_in.role_id):
                    self.logger.warning("attempt to update user with non-existing role_id=%s", user_in.role_id)
                    raise RoleNotFoundForUserException(user_in.role_id)
                user.role_id = user_in.role_id
                changed = True

            if changed:
                user.touch()
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)

            self.logger.info("updated user id=%s", getattr(user, "id", None))
            return user
        except (CpfUpdateNotAllowedException, UserAlreadyExistsException, RoleNotFoundForUserException):
            raise
        except Exception:
            self.logger.exception("error updating user id=%s", getattr(user, "id", None))
            raise

    def delete(self, user: User, current_user: _Optional[_User] = None) -> None:
        try:
            admin_permission.ensure(current_user)
            self.db.delete(user)
            self.db.commit()
            self.logger.info("deleted user id=%s", getattr(user, "id", None))
        except Exception:
            self.logger.exception("error deleting user id=%s", getattr(user, "id", None))
            raise

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)
