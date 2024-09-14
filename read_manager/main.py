import asyncio
import logging
import pickle

import asyncpg
import structlog
from bookt_domain.model.tenant import TenantRegistered
from bookt_domain.model.user import UserCreated
from confluent_kafka import Consumer
from cosmos.domain import Event

from read_manager.settings import settings

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
logger = structlog.get_logger()

conf = {
    "bootstrap.servers": settings.kafka_host,
    "group.id": settings.kafka_group_id,
    "auto.offset.reset": "earliest",
}

consumer = Consumer(conf)


async def insert_new_account(
    event: TenantRegistered,
    connection: asyncpg.Connection,
):
    await connection.execute(
        """
        INSERT INTO tenant(id, name) VALUES($1, $2)
    """,
        str(event.stream_id),
        event.tenant_name,
    )


async def insert_new_user(
    event: UserCreated,
    connection: asyncpg.Connection,
):
    await connection.execute(
        """
        INSERT INTO usr(id, email, first_name, last_name, tenant_id, hash)
        VALUES($1, $2, $3, $4, $5, $6)
    """,
        str(event.stream_id),
        event.email,
        event.first_name,
        event.last_name,
        str(event.tenant_id),
        "$2b$12$60a1iSYRlr5HO2gu4Ed76OYQ.zTw1ZT.1Bf1KrH6WB1IqeP06PERO",
    )


EVENT_HANDLERS = {
    "TenantRegistered": [insert_new_account],
    "UserCreated": [insert_new_user],
}


async def main(consumer):
    consumer.subscribe(["messages"])

    pool = await asyncpg.create_pool(
        host=settings.database_host,
        database=settings.database_name,
        user=settings.database_user,
        port=settings.database_port,
        password=settings.database_password,
    )

    try:
        while True:
            message = consumer.poll(timeout=1.0)
            if message is None:
                continue

            if error := message.error():
                logger.error(error)
                continue
            else:
                message = pickle.loads(message.value())
                log = logger.bind(event=message)

                if isinstance(message, Event):
                    handlers = EVENT_HANDLERS.get(message.name, [])

                    async with pool.acquire() as connection:
                        async with connection.transaction():
                            for handler in handlers:
                                await handler(event=message, connection=connection)

                else:
                    log.info("It's not an event, ingore it!")
    finally:
        consumer.close()
        pool.close()


if __name__ == "__main__":
    asyncio.run(main(consumer=consumer))
