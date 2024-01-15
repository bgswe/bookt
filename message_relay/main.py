import logging
import socket
from time import sleep

import structlog
from confluent_kafka import Producer
from psycopg_pool import ConnectionPool

from message_relay.settings import (
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

log = logger.bind(DATABASE_HOST=DATABASE_HOST)
log = log.bind(DATABASE_NAME=DATABASE_NAME)
log = log.bind(DATABASE_USER=DATABASE_USER)
log = log.bind(KAFKA_HOST=KAFKA_HOST)

log.info("starting message-relay application")


def main():
    conf = {
        "bootstrap.servers": KAFKA_HOST,
        "client.id": socket.gethostname(),
    }

    pending_messages = set()

    with ConnectionPool(min_size=2) as pool:

        def acked(err, msg):
            if err is not None:
                log = log.bind(message=str(msg), error=str(err))
                log.error("failed to deliver message")
            else:
                key = str(msg.key(), encoding="utf-8")

                with pool.connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            f"""
                            DELETE FROM
                                message_outbox
                            WHERE
                                id = '{key}'
                        """,
                        )

                        pending_messages.remove(key)

        while True:
            logger.info("--- MESSAGE RELAY ITERATION ---")

            with pool.connection() as conn:
                with conn.cursor() as cursor:
                    outbox_query = f"""
                        SELECT
                            *
                        FROM
                            message_outbox
                    """

                    # prevent querying for messages that are being processed
                    if len(pending_messages) > 0:
                        outbox_query = f"{outbox_query} WHERE id not in ({','.join(pending_messages)})"

                    logger.debug(outbox_query)

                    # query for messages, and map column names to returned column indexes
                    cursor.execute(outbox_query)
                    messages = cursor.fetchall()

                    if messages:
                        columns = {
                            desc[0]: i for i, desc in enumerate(cursor.description)
                        }
                        producer = Producer(conf)

                        for m in messages:
                            message_id = m[columns["id"]]
                            producer.produce(
                                "messages",
                                key=message_id,
                                value=bytes(m[columns["message"]]),
                                callback=acked,
                            )

                            pending_messages.add(message_id)

                        producer.poll(1)
                    else:
                        logger.debug("there are no messages to push")

                    sleep(1)


if __name__ == "__main__":
    main()
