from uuid import UUID, uuid4

import pytest
from cosmos.repository import AsyncRepository

from commands import CreateOrganization, handle_create_organization
from domain import Organization, Role


class MockOrganizationRepository(AsyncRepository):
    def __init__(self):
        self.repo = {}

        super().__init__()

    async def _add(self, agg: Organization):
        self.repo[agg.id] = agg

    async def _get(self, id: UUID):
        return self.repo[id]


@pytest.fixture
def make_organization(make_mock_uow):
    async def make(**kwargs):
        uuid = kwargs.get("id", uuid4())
        dummy_client_id = uuid4()

        repo = MockOrganizationRepository()
        uow = make_mock_uow(repository=repo)
        print(uuid)
        await handle_create_organization(
            uow=uow,
            command=CreateOrganization(
                client_id=dummy_client_id,
                organization_id=uuid,
                organization_name=kwargs.get("name", "Some Company LLC."),
                admin_email=kwargs.get("admin_email", "johndoe@example.com"),
                admin_password=kwargs.get("admin_password", "password"),
            ),
        )

        return await repo.get(id=uuid)

    return make


@pytest.mark.asyncio
async def test_information_requirements(make_organization):
    """Ensure informational requirements are satisfied."""

    kwargs = {
        "id": uuid4(),
        "name": "Some Company LLC.",
    }

    org = await make_organization(**kwargs)

    for attr, value in kwargs.items():
        assert getattr(org, attr, value) == value


@pytest.mark.asyncio
async def test_organization_creation_includes_default_admin(make_organization):
    """Ensure a newly created organization is created with a default admin."""

    email = "someuser@example.com"
    org = await make_organization(admin_email=email)

    assert len(org.users) == 1

    user = org.users.pop()

    assert user.email == email
    assert Role.SUPERUSER in user.roles


@pytest.mark.asyncio
async def test_password_not_available_on_user(make_organization):
    """Ensure a user's password is not accessable."""

    org = await make_organization(admin_password="bad2dabone")
    user = org.users.pop()

    try:
        user.password  # access attribute which shouldn't be there
        assert False  # fail on purpose
    except AttributeError:
        pass
