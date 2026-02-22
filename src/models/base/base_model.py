from __future__ import annotations

import uuid
from abc import ABCMeta
from datetime import date, datetime, timezone
from typing import Any, Dict, Iterable, Optional, Sequence

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeMeta

from src.config.settings import Base


class ModelMeta(DeclarativeMeta, ABCMeta):
    pass


class BaseModel(Base, metaclass=ModelMeta):
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __init__(
        self,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        if id is not None:
            self.id = str(id)
        if created_at is not None:
            self.created_at = created_at
        elif getattr(self, "created_at", None) is None:
            self.created_at = now
        if updated_at is not None:
            self.updated_at = updated_at
        elif getattr(self, "updated_at", None) is None:
            self.updated_at = now

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(
        self,
        columns: Optional[Iterable[str]] = None,
        exclude: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        mapper = inspect(self).mapper
        cols = [c.key for c in mapper.column_attrs]
        if columns is not None:
            cols = [c for c in cols if c in set(columns)]
        if exclude:
            exclude_set = set(exclude)
            cols = [c for c in cols if c not in exclude_set]

        result: Dict[str, Any] = {}
        for name in cols:
            value = getattr(self, name)
            if isinstance(value, (datetime, date)):
                result[name] = value.isoformat()
            else:
                result[name] = value
        return result

    def __repr__(self) -> str:
        created = (
            self.created_at.isoformat()
            if getattr(self, "created_at", None)
            else "<none>"
        )
        return f"<{self.__class__.__name__} id={self.id} created_at={created}>"
