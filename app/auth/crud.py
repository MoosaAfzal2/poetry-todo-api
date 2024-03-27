from typing import Any, Optional, Annotated
from uuid import UUID

from email_validator import validate_email, EmailNotValidError

from fastapi import HTTPException, status, Depends

from sqlmodel import select, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.utils.deps import SessionDep
from app.core.security import get_password_hash, verify_password
from app.core.utils.logger import logger

from .schemas import UserCreate, UserUpdate
from .models import User
from datetime import datetime, timezone


class AuthCrud:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, user_create: UserCreate) -> User:
        """
        Creates a new user in the database.

        Args:
            user_create (UserCreate): The user data to be created.

        Returns:
            User
        """
        try:
            db_obj = User.model_validate(
                user_create,
                update={"hashed_password": get_password_hash(user_create.password)},
            )
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)
            return db_obj

        except Exception as e:
            await self.session.rollback()
            logger.info(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Creating User",
            )

    async def update_user(self, db_user: User, user_in: UserUpdate) -> User:
        """
        Asynchronously updates a user in the database.

        Args:
            db_user (User): The user to be updated.
            user_in (UserUpdate): The updated user data.

        Returns:
            User: The updated user.
        """
        try:
            user_data = user_in.model_dump(exclude_unset=True)
            extra_data = {}
            if "password" in user_data:
                password = user_data["password"]
                hashed_password = get_password_hash(password)
                extra_data["hashed_password"] = hashed_password
            db_user.sqlmodel_update(user_data, update=extra_data)
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            return db_user

        except Exception as e:
            await self.session.rollback()
            logger.info(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Updating User",
            )

    async def delete_user(self, user_id: UUID) -> User:
        """
        A function that deletes a user based on the provided user_id.

        Parameters:
            user_id (UUID): The unique identifier of the user to be deleted.

        Returns:
            User: The user that was deleted.
        """
        try:
            statement = select(User).where(User.id == user_id)
            user_to_delete = (await self.session.exec(statement)).first()
            if user_to_delete is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User Does Not Exist",
                )

            await self.session.delete(user_to_delete)
            await self.session.commit()

            return user_to_delete

        except Exception as e:
            await self.session.rollback()
            logger.info(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Deleting User",
            )

    async def get_user(self, email: str, username: Optional[str] = None) -> User | None:
        """
        Retrieves a user from the database based on the provided email and optional username.

        Parameters:
            email (str): The email of the user to retrieve.
            username (Optional[str], optional): The username of the user to retrieve. Defaults to None.

        Returns:
            Union[User, None]: The retrieved user if found, otherwise None.

        Raises:
            HTTPException: If the email is invalid or if there is an error getting the user from the database.
        """
        try:
            # Validate Email
            validate_email(email, check_deliverability=False)

            statement = select(User).where(
                or_(User.email == email, User.username == username)
            )
            session_user = (await self.session.exec(statement)).first()
            return session_user

        except EmailNotValidError as e:
            logger.info(str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Email",
            )

        except Exception as e:
            logger.info(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Getting User",
            )

    async def authenticate(self, email: str, password: str) -> User | None:
        """
        Authenticates a user with the given email and password.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            User | None: The authenticated user if successful, None otherwise.

        Raises:
            HTTPException: If the user does not exist or the password is incorrect.
            HTTPException: If there is an error authenticating the user.
        """
        try:
            db_user = await self.get_user(email=email)
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User Does Not Exist",
                )
            if not verify_password(password, db_user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return db_user

        except HTTPException as e:
            logger.info(str(e))
            raise e

        except Exception as e:
            logger.info(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Authenticating User",
            )


async def get_auth_crud(session: SessionDep) -> AuthCrud:
    return AuthCrud(session=session)


AuthCrudDep = Annotated[AuthCrud, Depends(get_auth_crud)]
