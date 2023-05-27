from uuid import UUID

from cosmos.domain import Command
from cosmos.unit_of_work import AsyncUnitOfWork
from pydantic import EmailStr

from domain import Organization


class CreateOrganization(Command):
    organization_id: UUID | None = None
    organization_name: str
    organization_address: str
    admin_email: EmailStr
    admin_password: str


async def handle_create_organization(
    uow: AsyncUnitOfWork,
    command: CreateOrganization,
):
    """Creates Organization, and adds to the given repository."""

    async with uow as uow:
        org = Organization.create(
            id=command.organization_id,
            name=command.organization_name,
            address=command.organization_address,
            admin_email=command.admin_email,
            admin_password=command.admin_password,
        )

        await uow.repository.add(org)


COMMAND_HANDLERS = {
    "CreateOrganization": handle_create_organization,
}
