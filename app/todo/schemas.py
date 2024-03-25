from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID
from app.core.utils.generic_models import BaseUUIDModel

class TodoBase(SQLModel):
    title: str
    description: Optional[str]
    iscompleted: Optional[bool] = Field(default=False)


class TodoRead(SQLModel):
    id: UUID


class TodoCreate(TodoBase):
    pass


class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    iscompleted: Optional[bool] = False


class TodoDelete(SQLModel):
    id: UUID


class TodoOut(TodoBase , BaseUUIDModel):
    pass