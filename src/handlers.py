from cosmos.contrib.pg.async_uow import AsyncUnitOfWorkPostgres

from commands import Signup
from domain import Organization, User
from events import OrganizationCreated
from repository import OrganizationRepository, UserRepository


async def handle_signup(
    uow: AsyncUnitOfWorkPostgres,
    command: Signup,
):
    """Initiates the signup process by creating an Organization"""

    async with uow.context(Repository=OrganizationRepository) as uow:
        org = Organization.create(
            id=command.organization_id,
            name=command.organization_name,
            admin_email=command.admin_email,
        )

        await uow.repository.add(org)


COMMAND_HANDLERS = {
    "Signup": handle_signup,
}


async def create_initial_user_on_signup(
    uow: AsyncUnitOfWorkPostgres,
    event: OrganizationCreated,
):
    async with uow.context(Repository=UserRepository) as uow:
        await uow.repository.add(
            aggregate=User.create(
                organization_id=event.organization_id,
                email=event.admin_email,
                password="password",  # TODO: unsafe, randomly generate
            )
        )


EVENT_HANDLERS = {
    "OrganizationCreated": [
        create_initial_user_on_signup,
    ],
}
