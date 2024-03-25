from collections.abc import AsyncGenerator, Generator

import asyncio
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import test_settings
from app.main import app

from tests.utils.auth import get_user_token_headers, get_admin_token_headers

base_url = "http://localhost:8000/api/v1"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


test_async_connection_string = (
    str(test_settings.POSTGRES_DATABASE_URL)
    .replace("postgresql", "postgresql+asyncpg")
    .replace("sslmode=require", "")
)

test_async_engine = create_async_engine(
    url=test_async_connection_string,
    # echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30.0,
    pool_recycle=600,
)


@pytest.fixture(name="test_session", scope="session", autouse=True)
async def test_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        bind=test_async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(name="test_client", scope="module")
async def test_async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url=base_url) as aclient:
        yield aclient


@pytest.fixture(scope="module")
async def user_token_headers(
    test_client: AsyncClient, test_session: AsyncSession
) -> dict[str, str]:
    return await get_user_token_headers(
        client=test_client,
        session=test_session,
        email=test_settings.TEST_USER_EMAIL,
        username=test_settings.TEST_USER_USERNAME,
        password=test_settings.TEST_USER_PASSWORD,
    )


@pytest.fixture(scope="module")
async def admin_token_headers(test_client: AsyncClient) -> dict[str, str]:
    return await get_admin_token_headers(test_client)
