from sqlmodel import Field, Relationship, SQLModel, Column, VARCHAR
from pydantic import EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum
from app.core.utils.generic_models import RoleEnum


class UserBase(SQLModel):
    email: EmailStr = Field(sa_column=Column("email", VARCHAR, unique=True))
    username: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    email_verified: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=True)


# Properties to receive via API on creation
class UserCreate(SQLModel):
    email: EmailStr
    username: str
    password: str


class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None  # type: ignore
    username: Optional[str] = None  # type: ignore
    password: Optional[str] = None
    full_name: Optional[str] = None


class UserOut(UserBase):
    pass


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


class NewPassword(SQLModel):
    token: str
    new_password: str


class TokenTypeEnum(str, Enum):
    BEARER = "bearer"


class Token(SQLModel):
    access_token: str
    token_type: TokenTypeEnum
    expires_in: datetime | float


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: Optional[UUID] = None
    username: Optional[str] = None
