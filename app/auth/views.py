from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import col, delete, func, select
from sqlalchemy.exc import IntegrityError

from typing import Any, Annotated
from datetime import datetime, timedelta, timezone

from app.core.utils.deps import CurrentUserDep, SessionDep
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token

from .models import User
from .schemas import Token, UserBase, UserCreate, UserUpdate
import app.auth.crud as AuthCrud

AuthRouter = APIRouter()


@AuthRouter.post("/sign-up", response_model=Token)
async def signUp_route(session: SessionDep, user_create: UserCreate):
    """
    Signs-up, creates a new user & return an access token.
    """
    try:
        user = await AuthCrud.get_user(
            session=session, email=user_create.email, username=user_create.username
        )
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A User with this email or username Already Exists",
            )

        created_user = await AuthCrud.create_user(
            session=session, user_create=user_create
        )
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
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = await AuthCrud.authenticate(
            session=session, email=form_data.username, password=form_data.password
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


# @AuthRouter.post(
#     "/", response_model=UserOut
# )
# def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
#     """
#     Create new user.
#     """
#     user = crud.get_user_by_email(session=session, email=user_in.email)
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="The user with this email already exists in the system.",
#         )

#     user = crud.create_user(session=session, user_create=user_in)
#     # if settings.emails_enabled and user_in.email:
#     #     email_data = generate_new_account_email(
#     #         email_to=user_in.email, username=user_in.email, password=user_in.password
#     #     )
#     #     send_email(
#     #         email_to=user_in.email,
#     #         subject=email_data.subject,
#     #         html_content=email_data.html_content,
#     #     )
#     return user


# @AuthRouter.patch("/me", response_model=UserOut)
# def update_user_me(
#     *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUserDep
# ) -> Any:
#     """
#     Update own user.
#     """

#     if user_in.email:
#         existing_user = crud.get_user_by_email(session=session, email=user_in.email)
#         if existing_user and existing_user.id != current_user.id:
#             raise HTTPException(
#                 status_code=409, detail="User with this email already exists"
#             )
#     user_data = user_in.model_dump(exclude_unset=True)
#     current_user.sqlmodel_update(user_data)
#     session.add(current_user)
#     session.commit()
#     session.refresh(current_user)
#     return current_user


# @AuthRouter.patch("/me/password", response_model=Message)
# def update_password_me(
#     *, session: SessionDep, body: UpdatePassword, current_user: CurrentUserDep
# ) -> Any:
#     """
#     Update own password.
#     """
#     if not verify_password(body.current_password, current_user.hashed_password):
#         raise HTTPException(status_code=400, detail="Incorrect password")
#     if body.current_password == body.new_password:
#         raise HTTPException(
#             status_code=400, detail="New password cannot be the same as the current one"
#         )
#     hashed_password = get_password_hash(body.new_password)
#     current_user.hashed_password = hashed_password
#     session.add(current_user)
#     session.commit()
#     return Message(message="Password updated successfully")


# @AuthRouter.get("/me", response_model=UserOut)
# def read_user_me(session: SessionDep, current_user: CurrentUserDep) -> Any:
#     """
#     Get current user.
#     """
#     return current_user


# @AuthRouter.post("/open", response_model=UserOut)
# def create_user_open(session: SessionDep, user_in: UserCreateOpen) -> Any:
#     """
#     Create new user without the need to be logged in.
#     """
#     if not settings.USERS_OPEN_REGISTRATION:
#         raise HTTPException(
#             status_code=403,
#             detail="Open user registration is forbidden on this server",
#         )
#     user = crud.get_user_by_email(session=session, email=user_in.email)
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="The user with this email already exists in the system",
#         )
#     user_create = UserCreate.from_orm(user_in)
#     user = crud.create_user(session=session, user_create=user_create)
#     return user


# @AuthRouter.get("/{user_id}", response_model=UserOut)
# def read_user_by_id(
#     user_id: int, session: SessionDep, current_user: CurrentUserDep
# ) -> Any:
#     """
#     Get a specific user by id.
#     """
#     user = session.get(User, user_id)
#     if user == current_user:
#         return user
#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=403,
#             detail="The user doesn't have enough privileges",
#         )
#     return user


# @AuthRouter.patch(
#     "/{user_id}",
#     dependencies=[Depends(get_current_active_superuser)],
#     response_model=UserOut,
# )
# def update_user(
#     *,
#     session: SessionDep,
#     user_id: int,
#     user_in: UserUpdate,
# ) -> Any:
#     """
#     Update a user.
#     """

#     db_user = session.get(User, user_id)
#     if not db_user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this id does not exist in the system",
#         )
#     if user_in.email:
#         existing_user = crud.get_user_by_email(session=session, email=user_in.email)
#         if existing_user and existing_user.id != user_id:
#             raise HTTPException(
#                 status_code=409, detail="User with this email already exists"
#             )

#     db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
#     return db_user


# @AuthRouter.delete("/{user_id}")
# def delete_user(
#     session: SessionDep, current_user: CurrentUserDep, user_id: int
# ) -> Message:
#     """
#     Delete a user.
#     """
#     user = session.get(User, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     elif user != current_user and not current_user.is_superuser:
#         raise HTTPException(
#             status_code=403, detail="The user doesn't have enough privileges"
#         )
#     elif user == current_user and current_user.is_superuser:
#         raise HTTPException(
#             status_code=403, detail="Super users are not allowed to delete themselves"
#         )

#     statement = delete(Item).where(col(Item.owner_id) == user_id)
#     session.exec(statement)  # type: ignore
#     session.delete(user)
#     session.commit()
#     return Message(message="User deleted successfully")
