from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def fastapi_client() -> TestClient:
    return TestClient(app)


def test_command_create_organization(fastapi_client: TestClient):
    res = fastapi_client.post(
        "/command/create_organization/",
        json={
            "client_id": str(uuid4()),
            "organization_name": "Some Company, LLC",
            "organization_address": "1234 East Main Street, 00000, City, State",
            "admin_email": "admin@example.com",
            "admin_password": "P@$$word",
        },
    )

    assert res.status_code == 200
