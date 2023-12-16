import socket
from time import sleep

import psycopg2
import structlog
from confluent_kafka import Producer

from message_relay.settings import (
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

log.info("starting message-relay application")


def main():
    conf = {
        "bootstrap.servers": KAFKA_HOST,
        "client.id": socket.gethostname(),
    }

    pending_messages = set()

    def acked(err, msg):
        key = str(msg.key(), encoding="utf-8")

        if err is not None:
            log = log.bind(message=str(msg), error=str(err))
            log.error("failed to deliver message")
        else:
            conn = psycopg2.connect(
                host=EVENT_STORE_DATABASE_HOST,
                dbname=EVENT_STORE_DATABASE_NAME,
                user=EVENT_STORE_DATABASE_USER,
                password=EVENT_STORE_DATABASE_PASSWORD,
            )

            with conn:
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
        conn = psycopg2.connect(
            host=EVENT_STORE_DATABASE_HOST,
            dbname=EVENT_STORE_DATABASE_NAME,
            user=EVENT_STORE_DATABASE_USER,
            password=EVENT_STORE_DATABASE_PASSWORD,
        )

        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        *
                    FROM
                        message_outbox
                """
                )

                columns = {desc[0]: i for i, desc in enumerate(cursor.description)}

                messages = cursor.fetchall()

                if messages:
                    producer = Producer(conf)

                    for m in messages:
                        message_id = m[columns["id"]]

                        if message_id in pending_messages:
                            continue

                        producer.produce(
                            "messages",
                            key=message_id,
                            value=bytes(m[columns["message"]]),
                            callback=acked,
                        )

                        pending_messages.add(message_id)

                    producer.poll(1)
                else:
                    logger.info("there are no messages to push")

                sleep(1)


if __name__ == "__main__":
    main()
