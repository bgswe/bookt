from cosmos import UnitOfWork
from cosmos.decorators import Event, event

from domain.model.account import AccountCreated


@event
async def create_originator_user(uow: UnitOfWork, event: AccountCreated):
    print("Top of create_originator_user")

    print("Event:", event)

    print("Bottom of create_originator_user")


EVENT_HANDLERS = {"AccountCreated": [create_originator_user]}


async def handle_event(event: Event):
    if isinstance(event, AccountCreated):
        await create_originator_user(event=event)
