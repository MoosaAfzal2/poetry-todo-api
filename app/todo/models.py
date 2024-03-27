from sqlmodel import Field, Relationship
from app.core.utils.generic_models import BaseUUIDModel

from typing import Optional , TYPE_CHECKING
from uuid import UUID

from .schemas import TodoBase

if TYPE_CHECKING:
    from app.auth.models import User

class Todo(TodoBase, BaseUUIDModel, table=True):
    user_id: UUID = Field(foreign_key="users.id", index=True)
    user: "User" = Relationship(back_populates="todos")
