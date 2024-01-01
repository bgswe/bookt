import asyncio
from time import sleep

import structlog
from bookt_domain.model import Account, AccountCreated
from bookt_domain.service.command_handlers import handle_command
from bookt_domain.service.event_handlers import handle_event
from confluent_kafka import Consumer
from cosmos.contrib.pg.containers import PostgresDomainContainer
from cosmos.domain import Command, Event

from message_handler.settings import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_USER,
    KAFKA_HOST,
)

logger = structlog.get_logger()

log = logger.bind(DATABASE_HOST=DATABASE_HOST)
log = log.bind(DATABASE_NAME=DATABASE_NAME)
log = log.bind(DATABASE_USER=DATABASE_USER)
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
                sleep(0.1)
                continue

            if error := message.error():
                logger.error(error)
            else:
                import pickle

                message = pickle.loads(message.value())

                log.info(message)

                if isinstance(message, Event):
                    await handle_event(event=message)

                elif isinstance(message, Command):
                    await handle_command(command=message)

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


if __name__ == "__main__":
    container = PostgresDomainContainer()

    container.config.from_dict(
        {
            "database_host": DATABASE_HOST,
            "database_name": DATABASE_NAME,
            "database_user": DATABASE_USER,
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
            "bookt_domain.service.event_handlers",
            "bookt_domain.service.command_handlers",
        ]
    )

    asyncio.run(main())
