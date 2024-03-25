from typing import List, Annotated, Optional
from uuid import UUID

from fastapi import HTTPException, status, Depends

from sqlmodel import Session, select, and_
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.utils.deps import SessionDep
from app.core.utils.logger import logger

from .schemas import TodoCreate, TodoRead, TodoUpdate, TodoDelete, TodoOut
from .models import Todo

from datetime import datetime, timezone


class TodoCRUD:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_todos(self, user_id: UUID) -> List[Todo]:
        """
        A function that retrieves all todos for a specific user based on the provided user_id.

        Parameters:
            user_id (UUID): The unique identifier of the user whose todos are to be retrieved.

        Returns:
            List[Todo]: A list of Todo objects associated with the user.
        """
        try:
            statement = select(Todo).where(Todo.user_id == user_id)
            result = (await self.session.exec(statement)).all()
            return list(result)

        except Exception as e:
            logger.info(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Getting Todos",
            )

    async def get_todo(self, todo_id: UUID, user_id: UUID) -> Optional[Todo]:
        """
        Asynchronously retrieves a specific todo item based on the provided todo_id and user_id.

        Parameters:
            todo_id (UUID): The unique identifier of the todo item to retrieve.
            user_id (UUID): The unique identifier of the user who owns the todo item.

        Returns:
            Todo: The todo item corresponding to the provided todo_id and user_id.
        """
        try:
            statement = select(Todo).where(
                and_(Todo.user_id == user_id, Todo.id == todo_id)
            )
            result = (await self.session.exec(statement)).first()
            return result

        except Exception as e:
            logger.info(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Getting Todos",
            )

    async def add_todo(
        self,
        new_todo: TodoCreate,
        user_id: UUID,
    ) -> TodoOut:
        """
        A function to add a new todo item for a specific user, returning the added todo item.

        Parameters:
            new_todo (TodoCreate): The new todo item to be added.
            user_id (UUID): The unique identifier of the user.

        Returns:
            TodoOut: The added todo item.
        """
        try:
            session = self.session
            validated_todo = Todo.model_validate(new_todo, update={"user_id": user_id})

            session.add(validated_todo)
            await session.commit()
            await session.refresh(validated_todo)

            return TodoOut(**validated_todo.model_dump())

        except Exception as e:
            logger.info(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Adding Todo",
            )

    async def update_todo(
        self,
        todo_id: UUID,
        updated_todo: TodoUpdate,
        user_id: UUID,
    ) -> TodoOut:
        """
        A function to update a todo item based on the provided information.

        Parameters:
            - updated_todo: TodoUpdate - The updated todo object
            - user_id: UUID - The user ID associated with the todo

        Returns:
            TodoOut - The updated todo item
        """
        try:
            session = self.session

            todo_to_update = await self.get_todo(todo_id=todo_id, user_id=user_id)

            if todo_to_update is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
                )
            for key, value in updated_todo.model_dump().items():
                if value is not None:
                    setattr(todo_to_update, key, value)

            setattr(todo_to_update, "updated_at", datetime.now(timezone.utc))
            await session.commit()
            await session.refresh(todo_to_update)
            return TodoOut(**todo_to_update.model_dump())

        except Exception as e:
            logger.info(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Updating Todo",
            )

    async def delete_todo(self, todo_id: UUID, user_id: UUID) -> TodoOut:
        """
        A function to delete a specific todo item based on the provided todo_id and user_id.

        Parameters:
            todo_id (UUID): The unique identifier of the todo item to delete.
            user_id (UUID): The unique identifier of the user who owns the todo item.

        Returns:
            None
        """
        try:
            session = self.session
            todo_to_delete = await self.get_todo(todo_id=todo_id, user_id=user_id)
            if todo_to_delete is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
                )
            await session.delete(todo_to_delete)
            await self.session.commit()
            return TodoOut(**todo_to_delete.model_dump())

        except HTTPException as e:
            logger.info(str(e))
            raise e

        except Exception as e:
            logger.info(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Deleting Todo",
            )


async def get_todo_crud(session: SessionDep) -> TodoCRUD:
    return TodoCRUD(session=session)


TodoCrudDep = Annotated[TodoCRUD, Depends(get_todo_crud)]
