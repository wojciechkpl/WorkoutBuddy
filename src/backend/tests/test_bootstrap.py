import pytest
import asyncio
from fastapi.testclient import TestClient
from app.core.bootstrap import create_app


@pytest.mark.asyncio
async def test_app_bootstrap_and_health():
    app = await create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
