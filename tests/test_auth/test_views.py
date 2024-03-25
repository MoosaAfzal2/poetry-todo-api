import pytest
from httpx import AsyncClient
from app.core.config import test_settings
from tests.utils.helpers import create_random_email, create_random_lower_string


class TestSignUp:
    @pytest.mark.parametrize(
        "method, endpoint, data, expected_status, expected_response",
        [
            (
                "post",
                "/auth/sign-up",
                {
                    "email": test_settings.FIRST_SUPERUSER_EMAIL,
                    "username": test_settings.FIRST_SUPERUSER_USERNAME,
                    "password": test_settings.FIRST_SUPERUSER_PASSWORD,
                },
                409,
                {
                    "detail": "A User with this email or username Already Exists",
                },
            ),
            (
                "post",
                "/auth/sign-up",
                {
                    "email": create_random_email(),
                    "username": create_random_lower_string(),
                    "password": "123456",
                },
                200,
                None,
            ),
        ],
    )
    async def test(
        self,
        test_client: AsyncClient,
        method,
        endpoint,
        data,
        expected_status,
        expected_response,
    ):
        if method == "get":
            response = await test_client.get(endpoint)
        elif method == "put":
            response = await test_client.put(endpoint, json=data)
        elif method == "delete":
            response = await test_client.delete(endpoint)
        else:  # Default to POST
            response = await test_client.post(endpoint, json=data)

        assert response.status_code == expected_status
        if expected_response is not None:
            assert response.json() == expected_response


class TestLogin:
    @pytest.mark.parametrize(
        "method, endpoint, data, expected_status, expected_response",
        [
            (
                "post",
                "/auth/login",
                {"username": "invalidEmail", "password": "123456"},
                400,
                {"detail": "Invalid Email"},
            ),
            (
                "post",
                "/auth/login",
                {"username": create_random_email(), "password": "123456"},
                404,
                {"detail": "User Does Not Exist"},
            ),
            (
                "post",
                "/auth/login",
                {
                    "username": test_settings.FIRST_SUPERUSER_EMAIL,
                    "password": test_settings.FIRST_SUPERUSER_PASSWORD,
                },
                200,
                None,
            ),
        ],
    )
    async def test(
        self,
        test_client: AsyncClient,
        method,
        endpoint,
        data,
        expected_status,
        expected_response,
    ):
        if method == "get":
            response = await test_client.get(endpoint)
        elif method == "put":
            response = await test_client.put(endpoint, json=data)
        elif method == "delete":
            response = await test_client.delete(endpoint)
        else:  # Default to POST
            response = await test_client.post(endpoint, data=data)

        assert response.status_code == expected_status
        if expected_response is not None:
            assert response.json() == expected_response
