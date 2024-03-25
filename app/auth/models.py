from sqlmodel import Field, Relationship
from .schemas import UserBase
# from app.todo import models

from typing import Optional, List
from app.core.utils.generic_models import RoleEnum, BaseUUIDModel


class User(UserBase, BaseUUIDModel, table=True):
    __tablename__ = "users"
    hashed_password: str
    role: Optional[RoleEnum] = Field(default=RoleEnum.USER)

    # todos: List["Todo"] = Relationship(back_populates="users")
