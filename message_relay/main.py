import logging
import socket
from time import sleep

import structlog
from confluent_kafka import Producer
from psycopg2 import pool

from message_relay.settings import settings

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
logger = structlog.get_logger()


def get_connection_pool():
    connection_pool = None

    while connection_pool is None:
        try:
            connection_pool = pool.SimpleConnectionPool(
                minconn=settings.database_min_connections,
                maxconn=settings.database_max_connections,
                user=settings.database_user,
                password=settings.database_password,
                host=settings.database_host,
                database=settings.database_name,
                port=settings.database_port,
            )
        except Exception as e:
            log = logger.bind(exception=str(e))
            log.warning("unable to create connection pool")

            sleep(1)
            continue

    return connection_pool


def acknowledge_callback(connection_pool, pending_messages):
    def ack(err, msg):
        log = logger.bind(err=err, msg=msg)
        log.debug("ack invoked")

        if err is not None:
            logger.error("failed to deliver message")
        else:
            key = str(msg.key(), encoding="utf-8")
            log = logger.bind(key=key)
            log.debug("ack message received")

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
                cursor.close()
                connection.commit()
                connection_pool.putconn(connection)

            else:
                logger.error("failed to acquire pg connection")

            pending_messages.remove(key)

    return ack


def main():
    conf = {
        "bootstrap.servers": settings.kafka_host,
        "client.id": socket.gethostname(),
    }

    pending_messages = set()
    connection_pool = None

    try:
        connection_pool = get_connection_pool()

        while True:
            connection = connection_pool.getconn()
            if connection:
                outbox_query = f"""
                    SELECT
                        *
                    FROM
                        message_outbox;
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
                            callback=acknowledge_callback(
                                connection_pool=connection_pool,
                                pending_messages=pending_messages,
                            ),
                        )
                        pending_messages.add(message_id)

                    producer.flush()

                else:
                    logger.debug("there are no messages to push")

                cursor.close()
                connection_pool.putconn(connection)
            else:
                logger.error("failed to acquire pg connection")

            sleep(settings.iteration_sleep_duration)

    finally:
        if connection_pool:
            connection_pool.closeall()


if __name__ == "__main__":
    main()
