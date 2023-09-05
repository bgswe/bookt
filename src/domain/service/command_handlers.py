from cosmos import UnitOfWork, command

from domain.model import Account
from domain.service.commands import Register


@command(command_type=Register)
async def handle_registration(
    uow: UnitOfWork,
    command: Register,
):
    """Initiates the registration process by creating an Account"""

    account = Account()

    account.create(
        id=command.account_id,
        originator_email=command.originator_email,
    )

    await uow.repository.save(account)


COMMAND_HANDLERS = {
    "Register": handle_registration,
}
