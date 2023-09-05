import asyncio
from uuid import uuid4

from cosmos.contrib.pg.containers import PostgresDomainContainer

from domain.model import Account, AccountCreated
from domain.service.command_handlers import handle_registration
from domain.service.commands import Register


async def main():
    # TODO: Listen for messages from MessageQueue and feed
    # them into the service layer command, and event handlers

    command = Register(
        account_id=uuid4(),
        originator_email="email@example.com",
    )

    await handle_registration(command=command)


if __name__ == "__main__":
    container = PostgresDomainContainer()

    container.config.from_yaml("./apps/domain/config.yaml")
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
