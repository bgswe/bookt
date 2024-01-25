import asyncio
import logging
import pickle
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

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
logger = structlog.get_logger()

conf = {
    "bootstrap.servers": KAFKA_HOST,
    "group.id": "message-handler",
    "auto.offset.reset": "earliest",
}


async def main():
    try:
        log = logger.bind(conf=conf)
        log.debug("kafka consumer conf")

        consumer = Consumer(conf)

        log = logger.bind(consumer=consumer)
        log.debug("kafka consumer connected")

        consumer.subscribe(["messages"])

        while True:
            logger.info("--- MESSAGE HANDLER ITERATION ---")

            message = consumer.poll(timeout=1)
            if message is None:
                log.debug("no messages")
                continue

            if error := message.error():
                logger.error(error)
                continue
            else:
                message = pickle.loads(message.value())

                log.info(message)
                if isinstance(message, Event):
                    await handle_event(event=message)

                elif isinstance(message, Command):
                    await handle_command(command=message)

                sleep(1)

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
            "database_password": DATABASE_PASSWORD,
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
