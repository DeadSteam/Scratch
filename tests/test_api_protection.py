"""Smoke tests: protected API routes require authentication."""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app

BASE = "http://test/api/v1"


@pytest.mark.asyncio
async def test_images_list_requires_auth():
    experiment_id = uuid4()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=BASE,
    ) as client:
        response = await client.get(f"/images/experiment/{experiment_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_experiment_get_requires_auth():
    experiment_id = uuid4()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=BASE,
    ) as client:
        response = await client.get(f"/experiments/{experiment_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_users_get_requires_auth():
    user_id = uuid4()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=BASE,
    ) as client:
        response = await client.get(f"/users/{user_id}")
    assert response.status_code == 401
