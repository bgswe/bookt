from uuid import UUID

from cosmos.domain import Command
from cosmos.contrib.pg.async_uow import AsyncUnitOfWorkPostgres
from pydantic import EmailStr

from domain import Organization


class Login(Command):
    email: str
    password: str


class Signup(Command):
    organization_id: UUID | None = None
    organization_name: str
    admin_email: EmailStr
    admin_password: str


async def handle_signup(
    uow: AsyncUnitOfWorkPostgres,
    command: Signup,
):
    """Creates Organization, and adds to the given repository."""

    async with uow as uow:
        org = Organization.create(
            id=command.organization_id,
            name=command.organization_name,
            admin_email=command.admin_email,
            admin_password=command.admin_password,
        )

        await uow.repository.add(org)


COMMAND_HANDLERS = {
    "Signup": handle_signup,
}
