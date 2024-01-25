import logging
import socket
import sys
from time import sleep

import structlog
from confluent_kafka import Producer
from psycopg2 import pool

from message_relay.settings import settings

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
logger = structlog.get_logger()


def main():
    conf = {
        "bootstrap.servers": settings.kafka_host,
        "client.id": socket.gethostname(),
    }

    pending_messages = set()
    connection_pool = None

    try:
        connection_pool = None

        while connection_pool is None:
            try:
                connection_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=20,
                    user=settings.database_user,
                    password=settings.database_password,
                    host=settings.database_host,
                    database=settings.database_name,
                    port=settings.database_port,
                )
            except Exception as e:
                logger.error("cannot create connection pool")
                logger.error(e)
                sleep(1)
                continue

        logger.debug("connection pool created")

        while True:
            logger.info("--- MESSAGE RELAY ITERATION ---")

            def acked(err, msg):
                logger.info("--- ACKED ---")

                if err is not None:
                    log = log.bind(message=str(msg), error=str(err))
                    log.error("failed to deliver message")
                else:
                    key = str(msg.key(), encoding="utf-8")

                    connection = connection_pool.getconn()
                    if connection:
                        cursor = connection.cursor()
                        cursor.execute(
                            f"""
                            DELETE FROM
                                message_outbox
                            WHERE
                                id = '{key}'
                        """,
                        )
                        connection.commit()
                        cursor.close()
                        connection_pool.putconn(connection)

                    else:
                        logger.error("failed to acquire pg connection")

                    pending_messages.remove(key)

            connection = connection_pool.getconn()
            if connection:
                outbox_query = f"""
                    SELECT
                        *
                    FROM
                        message_outbox
                """

                # prevent querying for messages that are being processed
                if len(pending_messages) > 0:
                    pending_message_ids = [f"'{m}'" for m in pending_messages]
                    outbox_query = f"{outbox_query} WHERE id not in ({','.join(pending_message_ids)})"

                logger.debug(outbox_query)

                # query for messages, and map column names to returned column indexes
                cursor = connection.cursor()
                cursor.execute(outbox_query)
                messages = cursor.fetchall()

                if messages:
                    columns = {desc[0]: i for i, desc in enumerate(cursor.description)}
                    producer = Producer(conf)

                    for m in messages:
                        producer.poll(0)

                        message_id = m[columns["id"]]
                        producer.produce(
                            "messages",
                            key=message_id,
                            value=bytes(m[columns["message"]]),
                            callback=acked,
                        )
                        pending_messages.add(message_id)

                        logger.info(m)

                    producer.flush()

                else:
                    logger.debug("there are no messages to push")

                cursor.close()
                connection_pool.putconn(connection)
                sleep(1)
            else:
                logger.error("failed to acquire pg connection")

    finally:
        if connection_pool:
            connection_pool.closeall()


if __name__ == "__main__":
    main()
