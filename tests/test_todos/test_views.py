import pytest
from httpx import AsyncClient


class TestTodos:
    
    async def test_get_all_todos(self, test_client: AsyncClient, user_token_headers):
        response = await test_client.get("/todo/", headers=user_token_headers)
        assert response.status_code == 200

    async def test_create_todo(self, test_client: AsyncClient, user_token_headers):
        response = await test_client.post(
            "/todo/",
            json={"title": "Test Title", "description": "Test Description"},
            headers=user_token_headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert data["title"] == "Test Title"
        assert data["description"] == "Test Description"

    async def test_update_todo(self, test_client: AsyncClient, user_token_headers):
        response = await test_client.post(
            "/todo/",
            json={"title": "Test Title", "description": "Test Description"},
            headers=user_token_headers,
        )
        data = response.json()
        todo_id = data["id"]

        response = await test_client.patch(
            f"/todo/{todo_id}",
            json={"title": "Updated Title", "description": "Updated Description"},
            headers=user_token_headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated Description"

    async def test_delete_todo(self, test_client: AsyncClient, user_token_headers):
        response = await test_client.post(
            "/todo/",
            json={"title": "Test Title", "description": "Test Description"},
            headers=user_token_headers,
        )
        data = response.json()
        todo_id = data["id"]

        response = await test_client.delete(
            f"/todo/{todo_id}", headers=user_token_headers
        )

        assert response.status_code == 200

        data = response.json()

        response = await test_client.get(f"/todo/{todo_id}", headers=user_token_headers)

        assert response.status_code == 404

        data = response.json()

        assert data["detail"] == "Todo not found"
