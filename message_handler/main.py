import asyncio
import logging
import pickle

import structlog
from bookt_domain.model import Account
from bookt_domain.service.command_handlers import handle_command
from bookt_domain.service.event_handlers import handle_event
from confluent_kafka import Consumer
from cosmos.contrib.pg.containers import PostgresDomainContainer
from cosmos.domain import Command, Event

from message_handler.settings import settings

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
logger = structlog.get_logger()

conf = {
    "bootstrap.servers": settings.kafka_host,
    "group.id": settings.kafka_group_id,
    "auto.offset.reset": "earliest",
}


async def main():
    try:
        consumer = Consumer(conf)
        consumer.subscribe(["messages"])

        while True:
            message = consumer.poll(timeout=1.0)
            if message is None:
                continue

            if error := message.error():
                logger.error(error)
                continue
            else:
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

    container.config.from_dict(
        {
            "database_host": settings.database_host,
            "database_name": settings.database_name,
            "database_user": settings.database_user,
            "database_port": settings.database_port,
            "database_password": settings.database_password,
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
