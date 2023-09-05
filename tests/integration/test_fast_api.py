from uuid import uuid4

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def fastapi_client() -> TestClient:
    app.pool = None

    return TestClient(app)


# def test_command_create_organization(fastapi_client: TestClient):
#     res = fastapi_client.post(
#         "/command/create_organization/",
#         json={
#             "client_id": str(uuid4()),
#             "organization_name": "Some Company, LLC",
#             "admin_email": "admin@example.com",
#             "admin_password": "P@$$word",
#         },
#     )

#     assert res.status_code == 200
