from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:

    to_encode = data.copy()

    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY is undefined")

    if not settings.ALGORITHM:
        raise ValueError("ALGORITHM is undefined")

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    elif settings.ACCESS_TOKEN_EXPIRE_MINUTES:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    if "sub" in to_encode and isinstance(to_encode["sub"], UUID):
        to_encode["sub"] = str(to_encode["sub"])

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
