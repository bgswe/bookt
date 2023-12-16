from cosmos import UnitOfWork
from cosmos.decorators import Event, event

from message_handler.domain.model.account import AccountCreated
from message_handler.domain.model.user import User, UserRoles


@event
async def create_originator_user(uow: UnitOfWork, event: AccountCreated):
    """Create a new user for creator of new account"""

    user = User()

    user.create(
        account_id=event.stream_id,
        email=event.originator_email,
        roles=[UserRoles.ACCOUNT_ADMIN],
    )

    await uow.repository.save(aggregate=user)


EVENT_HANDLERS = {"AccountCreated": [create_originator_user]}


async def handle_event(event: Event):
    if isinstance(event, AccountCreated):
        await create_originator_user(event=event)
