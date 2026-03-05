
from __future__ import annotations

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class JwtConfig:
	def __init__(self) -> None:
		self.secret_key: str = os.getenv("JWT_SECRET_KEY")
		if not self.secret_key:
			raise RuntimeError("JWT_SECRET_KEY is not set in environment")
		self.algorithm: str = os.getenv("JWT_ALGORITHM")
		if not self.algorithm:
			raise RuntimeError("JWT_ALGORITHM is not set in environment")
		try:
			self.access_token_expires_minutes: int = int(
				os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
			)
		except Exception:
			self.access_token_expires_minutes = 15

		try:
			self.refresh_token_expires_days: int = int(
				os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS")
			)
		except Exception:
			self.refresh_token_expires_days = 7

		self.refresh_cookie_name: str = os.getenv("JWT_REFRESH_COOKIE_NAME")
		if not self.refresh_cookie_name:
			raise RuntimeError("JWT_REFRESH_COOKIE_NAME is not set in environment")
		self.refresh_cookie_domain: str | None = os.getenv("JWT_REFRESH_COOKIE_DOMAIN") or None

	def access_token_expires(self) -> timedelta:
		return timedelta(minutes=self.access_token_expires_minutes)

	def refresh_token_expires(self) -> timedelta:
		return timedelta(days=self.refresh_token_expires_days)
