from collections.abc import AsyncGenerator, Generator

import asyncio
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import test_settings
from app.core.utils.deps import get_async_session
from app.main import app

from tests.utils.auth import get_user_token_headers, get_admin_token_headers
from app.core.db import init_db

from sqlalchemy.pool import NullPool

base_url = "http://localhost:8000/api/v1"


@pytest.fixture(scope="module")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


test_async_connection_string = (
    str(test_settings.TEST_POSTGRES_DATABASE_URL)
    .replace("postgresql", "postgresql+asyncpg")
    .replace("sslmode=require", "")
)

test_async_engine = create_async_engine(
    url=test_async_connection_string, poolclass=NullPool
)


async def get_test_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        bind=test_async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture(name="test_session", scope="module", autouse=True)
async def test_async_session() -> AsyncGenerator[AsyncSession, None]:
    # Intialize DB
    await init_db(test_async_engine)

    async_session = async_sessionmaker(
        bind=test_async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(name="test_client", scope="module")
async def test_async_client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_async_session] = get_test_async_session
    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url=base_url) as aclient:
        yield aclient


@pytest.fixture(scope="module")
async def user_token_headers(
    test_client: AsyncClient, test_session: AsyncSession
) -> dict[str, str]:
    user_token_headers = await get_user_token_headers(
        client=test_client,
        session=test_session,
        email=test_settings.TEST_USER_EMAIL,
        username=test_settings.TEST_USER_USERNAME,
        password=test_settings.TEST_USER_PASSWORD,
    )
    return user_token_headers


@pytest.fixture(scope="module")
async def admin_token_headers(test_client: AsyncClient) -> dict[str, str]:
    return await get_admin_token_headers(test_client)
