import asyncio
from uuid import UUID, uuid4

from cosmos.contrib.pg.containers import PostgresDomainContainer

from domain.model import Account, AccountCreated
from domain.service.command_handlers import handle_registration
from domain.service.commands import Register


async def main():
    # TODO: Listen for messages from MessageQueue and feed
    # them into the service layer command, and event handlers

    command = Register(
        message_id=uuid4(),
        account_id=uuid4(),
        originator_email="email@example.com",
    )

    await handle_registration(command=command)


if __name__ == "__main__":
    container = PostgresDomainContainer()

    # TODO: this path is likely to break
    container.config.from_yaml("./message-handler/config.yaml")
    container.config.event_hydration_mapping.from_dict(
        {
            "AccountCreated": AccountCreated,
        }
    )
    container.config.aggregate_root_mapping.from_dict(
        {
            "Account": Account,
        }
    )

    container.wire(modules=[__name__])

    asyncio.run(main())
