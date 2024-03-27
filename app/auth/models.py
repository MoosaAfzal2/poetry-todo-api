from sqlmodel import Field, Relationship
from .schemas import UserBase

from typing import Optional, List , TYPE_CHECKING
from app.core.utils.generic_models import RoleEnum, BaseUUIDModel

if TYPE_CHECKING:
    from app.todo.models import Todo


class User(UserBase, BaseUUIDModel, table=True):
    __tablename__ = "users"
    hashed_password: str
    role: Optional[RoleEnum] = Field(default=RoleEnum.USER)

    todos: List["Todo"] = Relationship(back_populates="user")
