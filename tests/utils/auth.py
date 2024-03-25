from httpx import AsyncClient
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.auth.models import User
from app.auth.schemas import UserCreate, UserUpdate
from app.auth.crud import create_user, get_user, update_user

from tests.utils.helpers import create_random_email, create_random_lower_string


async def create_random_user(session: AsyncSession) -> User:
    email = create_random_email()
    password = create_random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = await create_user(session=session, user_create=user_in)
    return user


async def user_authentication_headers(
    *, client: AsyncClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}

    res = await client.post("/auth/login", data=data)
    response = res.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


async def get_user_token_headers(
    *, client: AsyncClient, email: str, username: str, password, session: AsyncSession
) -> dict[str, str]:
    """
    Return a valid token for the user with given credentials.

    If the user doesn't exist it is created first.
    """
    user = await get_user(session=session, email=email, username=username)
    if not user:
        user_in_create = UserCreate(email=email, password=password, username=username)
        user = await create_user(session=session, user_create=user_in_create)

    return await user_authentication_headers(
        client=client, email=email, password=password
    )


async def get_admin_token_headers(test_client: AsyncClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER_EMAIL,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await test_client.post("/auth/login", data=login_data)
    if r.status_code == 200:
        tokens = r.json()
        a_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {a_token}"}
        return headers
    else:
        raise Exception("Failed to get admin token headers")
