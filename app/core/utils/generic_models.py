from uuid import UUID
from .uuid6 import uuid7
from sqlmodel import SQLModel, Field
from sqlalchemy.orm import declared_attr
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# # id: implements proposal uuid7 draft4
# class _SQLModel(SQLModel):
#     @declared_attr  # type: ignore
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()


class BaseUUIDModel(SQLModel):
    id: Optional[UUID] = Field(default_factory=uuid7, primary_key=True, index=True)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.utcnow())
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.utcnow(),
        sa_column_kwargs={"onupdate": lambda: datetime.utcnow()},
    )


class Message(SQLModel):
    message: str


class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"
