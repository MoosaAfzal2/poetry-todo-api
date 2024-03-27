from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import col, delete, func, select
from sqlalchemy.exc import IntegrityError

from typing import Any, Annotated
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.core.utils.deps import CurrentUserDep
from app.core.config import settings
from app.core.utils.generic_models import Message
from app.core.security import get_password_hash, verify_password, create_access_token

from .models import User
from .schemas import Token, UserCreate, UserOut, UserUpdate
from .crud import AuthCrudDep

AuthRouter = APIRouter()


@AuthRouter.post("/sign-up", response_model=Token)
async def signUp_route(AuthCrud: AuthCrudDep, user_create: UserCreate):
    """
    Signs-up, creates a new user & return an access token.
    """
    try:
        user = await AuthCrud.get_user(
            email=user_create.email, username=user_create.username
        )
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A User with this email or username Already Exists",
            )

        created_user = await AuthCrud.create_user(user_create=user_create)
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Creating User",
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data={"sub": created_user.id, "username": created_user.username},
            expires_delta=access_token_expires,
        )
        if not access_token:
            raise HTTPException(
                status_code=500,
                detail="Error Signing Up",
            )
        return Token(
            access_token=access_token,
            expires_in=access_token_expires.total_seconds(),
            token_type="bearer",
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An Unexpected error occurred",
        )


@AuthRouter.post("/login", response_model=Token)
async def login_route(
    AuthCrud: AuthCrudDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = await AuthCrud.authenticate(
            email=form_data.username, password=form_data.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User Does Not Exist"
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data={"sub": user.id, "username": user.username},
            expires_delta=access_token_expires,
        )
        if not access_token:
            raise HTTPException(
                status_code=500,
                detail="Error Logging In",
            )
        return Token(
            access_token=access_token,
            expires_in=access_token_expires.total_seconds(),
            token_type="bearer",
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An Unexpected error occurred",
        )


@AuthRouter.delete("/delete-account", response_model=Message)
async def delete_account_route(AuthCrud: AuthCrudDep, current_user: CurrentUserDep):
    try:
        if not isinstance(current_user.id, UUID):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        deleted_user = await AuthCrud.delete_user(user_id=current_user.id)

        if deleted_user and deleted_user is not None:
            return Message(message="User Account deleted successfully")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An Unexpected error occurred",
        )


@AuthRouter.get("/profile", response_model=UserOut)
async def get_profile_route(current_user: CurrentUserDep):
    try:
        if not isinstance(current_user.id, UUID):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return UserOut(**current_user.model_dump())

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An Unexpected error occurred",
        )


@AuthRouter.patch("/profile", response_model=UserOut)
async def update_profile_route(
    AuthCrud: AuthCrudDep, current_user: CurrentUserDep, user_update: UserUpdate
):
    try:
        if not isinstance(current_user.id, UUID):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        updated_user = await AuthCrud.update_user(
            user_id=current_user.id, updated_data=user_update
        )
        return UserOut(**updated_user.model_dump())

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An Unexpected error occurred",
        )
