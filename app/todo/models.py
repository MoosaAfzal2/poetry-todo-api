from sqlmodel import Field, Relationship
from app.core.utils.generic_models import BaseUUIDModel
# from app.auth.models import User

from typing import Optional
from uuid import UUID

from .schemas import TodoBase


class Todo(TodoBase, BaseUUIDModel, table=True):
    user_id: UUID = Field(foreign_key="users.id", index=True)
    # user: Optional[User] = Relationship(back_populates="todo")
