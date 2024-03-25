from fastapi import APIRouter, Depends, status
from sqlmodel import select

from app.core.utils.deps import SessionDep
from .crud import get_health
from .models import Health
from app.core.utils.logger import logger_config

HealthRouter = APIRouter()
logger = logger_config(__name__)


@HealthRouter.get("/", response_model=Health)
async def health(db: SessionDep):
    return await get_health(db=db)
