from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.models.user import User
from src.utils.password import PasswordManager
from src.utils.jwt_utils import JwtManager
from src.config.settings import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class AuthService:
	def __init__(self, db: Session, pwd_manager: Optional[PasswordManager] = None, jwt_manager: Optional[JwtManager] = None) -> None:
		self.db = db
		self.pwd = pwd_manager or PasswordManager()
		self.jwt = jwt_manager or JwtManager()

	def authenticate_user(self, username_or_email: str, password: str) -> Optional[User]:
		user = (
			self.db.query(User)
			.filter(or_(User.username == username_or_email, User.email == username_or_email))
			.first()
		)
		if not user:
			return None
		if not self.pwd.verify(password, user.password_hash):
			return None
		return user

	def create_access_token_for_user(self, user: User) -> str:
		return self.jwt.create_access_token(subject=str(user.id), username=user.username)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
	return AuthService(db)

async def get_current_user(token: str = Depends(oauth2_scheme), svc: AuthService = Depends(get_auth_service)) -> User:
	try:
		payload = svc.jwt.decode_token(token)
	except ValueError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

	sub = payload.get("sub")
	if not sub:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

	user = svc.db.get(User, sub)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

	return user

