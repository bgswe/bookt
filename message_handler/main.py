import asyncio
from time import sleep

import structlog
from confluent_kafka import Consumer
from cosmos.contrib.pg.containers import PostgresDomainContainer
from cosmos.domain import Command, Event

from message_handler.domain.model import Account, AccountCreated
from message_handler.domain.service.command_handlers import handle_command
from message_handler.domain.service.event_handlers import handle_event
from message_handler.settings import (
    EVENT_STORE_DATABASE_HOST,
    EVENT_STORE_DATABASE_NAME,
    EVENT_STORE_DATABASE_PASSWORD,
    EVENT_STORE_DATABASE_USER,
    KAFKA_HOST,
)

logger = structlog.get_logger()

log = logger.bind(MESSAGE_OUTBOX_DATABASE_HOST=EVENT_STORE_DATABASE_HOST)
log = log.bind(MESSAGE_OUTBOX_DATABASE_NAME=EVENT_STORE_DATABASE_NAME)
log = log.bind(MESSAGE_OUTBOX_DATABASE_USER=EVENT_STORE_DATABASE_USER)
log = log.bind(KAFKA_HOST=KAFKA_HOST)

log.info("starting message-handler application")


conf = {
    "bootstrap.servers": KAFKA_HOST,
    "group.id": "message-handler",
    "auto.offset.reset": "earliest",
}


async def main():
    # TODO: Listen for messages from MessageQueue and feed
    # them into the service layer command, and event handlers

    try:
        log = logger.bind(conf=conf)
        log.info("kafka consumer conf")

        consumer = Consumer(conf)

        log = logger.bind(consumer=consumer)
        log.info("kafka consumer connected")

        consumer.subscribe(["messages"])

        logger.info("subscribed to messages topic")

        while True:
            message = consumer.poll(timeout=1.0)
            if message is None:
                log.info("no messages")
                sleep(1)
                continue

            if error := message.error():
                logger.error(error)
            else:
                import pickle

                message = pickle.loads(message.value())

                if isinstance(message, Event):
                    await handle_event(event=message)

                elif isinstance(message, Command):
                    await handle_command(command=message)

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


if __name__ == "__main__":
    container = PostgresDomainContainer()

    # TODO: this path is likely to break
    container.config.from_dict(
        {
            "database_name": EVENT_STORE_DATABASE_NAME,
            "database_user": EVENT_STORE_DATABASE_USER,
        }
    )
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
            "message_handler.domain.service.event_handlers",
            "message_handler.domain.service.command_handlers",
        ]
    )

    asyncio.run(main())
