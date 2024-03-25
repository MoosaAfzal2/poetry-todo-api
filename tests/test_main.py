import pytest
from httpx import AsyncClient
from app.health.models import Status


@pytest.mark.asyncio
async def test_root(test_client: AsyncClient):
    response = await test_client.get("/")
    assert response is not None
    assert response.status_code == 200
    assert response.json() == {"app_status": Status.OK, "db_status": Status.OK}
    await test_client.aclose()
