from sqlmodel import SQLModel, Session, select, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.utils.generic_models import RoleEnum

from app.auth.models import User
from app.auth.schemas import UserCreate
from app.auth.crud import create_user
from app.todo.models import Todo

async_connection_string = (
    str(settings.POSTGRES_DATABASE_URL)
    .replace("postgresql", "postgresql+asyncpg")
    .replace("sslmode=require", "")
)

async_engine = create_async_engine(
    url=async_connection_string,
    # echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30.0,
    pool_recycle=600,
)


async def init_db(Engine=async_engine) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines

    # This works because the models are already imported and registered from app
    async with Engine.begin() as async_conn:
        await async_conn.run_sync(SQLModel.metadata.create_all)


    async_session = async_sessionmaker(
        bind=Engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:

        user = (
            await session.exec(
                select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
            )
        ).first()
        if not user:
            user_in = UserCreate(
                username=settings.FIRST_SUPERUSER_USERNAME,
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                role=RoleEnum.ADMIN,
            )
            user = await create_user(session=session, user_create=user_in)
