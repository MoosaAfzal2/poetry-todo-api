from fastapi import Depends, APIRouter, HTTPException, status

from sqlalchemy.orm import Session

from app.core.utils.deps import SessionDep, CurrentUserDep
from app.core.utils.logger import logger
from app.core.utils.generic_models import Message

from .models import Todo
from .schemas import TodoOut, TodoRead, TodoUpdate, TodoCreate, TodoDelete
from .crud import TodoCrudDep

from typing import Annotated
from uuid import UUID

TodoRouter = APIRouter()


######## GET METHOD ########
@TodoRouter.get("/", response_model=list[TodoOut])
async def get_all_todos_route(
    current_user: CurrentUserDep,
    TodoCrud: TodoCrudDep,
):
    try:
        if not isinstance(current_user.id, UUID):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        result = await TodoCrud.get_all_todos(user_id=current_user.id)
        todos = [TodoOut(**todo.model_dump()) for todo in result]

        return todos

    except HTTPException as e:
        logger.info(str(e))
        raise e

    except Exception as e:
        logger.info(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Getting Todos",
        )


######## GET METHOD ########
@TodoRouter.get("/{todo_id}", response_model=TodoOut)
async def get_todo_route(
    todo_id: UUID,
    current_user: CurrentUserDep,
    TodoCrud: TodoCrudDep,
):
    try:
        if not isinstance(current_user.id, UUID):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        result = await TodoCrud.get_todo(todo_id=todo_id, user_id=current_user.id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
            )
        return TodoOut(**result.model_dump())

    except HTTPException as e:
        logger.info(str(e))
        raise e

    except Exception as e:
        logger.info(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Getting Todo",
        )


####### POST METHOD ########
@TodoRouter.post("/", response_model=TodoOut)
async def add_todo_route(
    new_todo: TodoCreate,
    current_user: CurrentUserDep,
    TodoCrud: TodoCrudDep,
):
    try:
        if not isinstance(current_user.id, UUID):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        created_todo = await TodoCrud.add_todo(
            new_todo=new_todo, user_id=current_user.id
        )
        return created_todo

    except HTTPException as e:
        logger.info(str(e))
        raise e

    except Exception as e:
        logger.info(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Adding Todo",
        )


# ######## UPDATE METHOD ########
@TodoRouter.patch("/{todo_id}" , response_model=TodoOut)
async def update_todo_route(
    todo_id: UUID,
    updated_todo: TodoUpdate,
    current_user: CurrentUserDep,
    TodoCrud: TodoCrudDep,
):
    try:
        if not isinstance(current_user.id, UUID):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        created_todo = await TodoCrud.update_todo(
            todo_id=todo_id, updated_todo=updated_todo, user_id=current_user.id
        )
        return created_todo

    except HTTPException as e:
        logger.info(str(e))
        raise e

    except Exception as e:
        logger.info(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Updating Todo",
        )


# ######## DELETE METHOD ########
@TodoRouter.delete("/{todo_id}")
async def delete_todo_route(
    todo_id: UUID,
    current_user: CurrentUserDep,
    TodoCrud: TodoCrudDep,
):
    try:
        if not isinstance(current_user.id, UUID):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        deleted_todo = await TodoCrud.delete_todo(
            todo_id=todo_id, user_id=current_user.id
        )
        return Message(message=f"Todo with id: {deleted_todo.id} deleted successfully")

    except HTTPException as e:
        logger.info(str(e))
        raise e

    except Exception as e:
        logger.info(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Deleting Todo",
        )
