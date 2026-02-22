
from __future__ import annotations

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class JwtConfig:
	def __init__(self) -> None:
		self.secret_key: str = os.getenv("JWT_SECRET_KEY")
		self.algorithm: str = os.getenv("JWT_ALGORITHM")
		try:
			self.access_token_expires_minutes: int = int(
				os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
			)
		except Exception:
			self.access_token_expires_minutes = 15

	def access_token_expires(self) -> timedelta:
		return timedelta(minutes=self.access_token_expires_minutes)
