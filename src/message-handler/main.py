import asyncio

from confluent_kafka import Consumer
from cosmos.contrib.pg.containers import PostgresDomainContainer
from cosmos.domain import Command, Event

from domain.model import Account, AccountCreated
from domain.service.command_handlers import handle_command
from domain.service.event_handlers import handle_event

conf = {
    "bootstrap.servers": "192.168.0.11:9092",
    "group.id": "foo",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(conf)


async def main():
    # TODO: Listen for messages from MessageQueue and feed
    # them into the service layer command, and event handlers

    try:
        consumer.subscribe(["messages"])

        while True:
            message = consumer.poll(timeout=1.0)
            if message is None:
                continue

            if message.error():
                print("ERROR")
            else:
                import pickle

                message = pickle.loads(message.value())

                print("handle message", type(message))

                if isinstance(message, Event):
                    print("is event")
                    await handle_event(event=message)

                elif isinstance(message, Command):
                    await handle_command(command=message)

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


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

    container.wire(
        modules=[
            __name__,
            "domain.service.event_handlers",
            "domain.service.command_handlers",
        ]
    )

    asyncio.run(main())