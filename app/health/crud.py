from sqlmodel import select

from app.core.utils.logger import logger_config
from app.core.utils.deps import AsyncSession
from .models import Health, Status

logger = logger_config(__name__)


async def get_health(db: AsyncSession) -> Health:
    db_status = await get_db_health(db=db)
    logger.info("%s.get_health.db_status: %s", __name__, db_status)
    return Health(app_status=Status.OK, db_status=db_status)


async def get_db_health(db: AsyncSession) -> Status:
    try:
        await db.exec(select(1))
        return Status.OK
    except Exception as e:
        logger.exception(e)

    return Status.NOT_OK
