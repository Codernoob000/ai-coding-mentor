import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"

@pytest.mark.asyncio
async def test_chat_validation_error(client):
    # Test min_length validation
    response = await client.post("/api/v1/chat", json={"message": ""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_chat_too_long(client):
    # Test max_length validation (assuming 10000 limit)
    long_message = "a" * 10001
    response = await client.post("/api/v1/chat", json={"message": long_message})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
