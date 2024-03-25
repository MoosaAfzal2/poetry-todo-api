from fastapi import APIRouter
from app.health.views import HealthRouter
from app.todo.views import TodoRouter
from app.auth.views import AuthRouter

api_router = APIRouter()
api_router.include_router(HealthRouter, prefix="", tags=["Health"])
api_router.include_router(AuthRouter, prefix="/auth", tags=["Auth"])
api_router.include_router(TodoRouter, prefix="/todo", tags=["Todo"])
