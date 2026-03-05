from sqlalchemy import Column, String
from datetime import datetime
from typing import Any, Dict, Optional
from src.models.base.base_model import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.name = name
        self.description = description
