import asyncio
import logging
import pickle

import structlog
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


async def main(consumer):
    consumer.subscribe(["messages"])
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
                    log.info("It's an event, handle it!")
                else:
                    log.info("It's not an event, ingore it!")
    finally:
        consumer.close()


if __name__ == "__main__":
    asyncio.run(main(consumer=consumer))
