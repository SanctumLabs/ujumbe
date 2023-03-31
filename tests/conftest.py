from httpx import AsyncClient
import pytest
from app import app


@pytest.fixture
async def client(request):
    async with AsyncClient(app=app, base_url="http://test") as client:
        request.cls.client = client
        yield client
