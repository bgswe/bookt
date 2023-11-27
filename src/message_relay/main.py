import socket
from time import sleep

import psycopg2
import structlog
from confluent_kafka import Producer

from message_relay.settings import (
    MESSAGE_OUTBOX_DATABASE_HOST,
    MESSAGE_OUTBOX_DATABASE_NAME,
    MESSAGE_OUTBOX_DATABASE_PASSWORD,
    MESSAGE_OUTBOX_DATABASE_USER,
)

logger = structlog.get_logger()


log = logger.bind(MESSAGE_OUTBOX_DATABASE_HOST=MESSAGE_OUTBOX_DATABASE_HOST)
log = log.bind(MESSAGE_OUTBOX_DATABASE_NAME=MESSAGE_OUTBOX_DATABASE_NAME)
log = log.bind(MESSAGE_OUTBOX_DATABASE_USER=MESSAGE_OUTBOX_DATABASE_USER)

log.info("starting message-relay application")


def main():
    conf = {
        "bootstrap.servers": "192.168.0.11:9092",
        "client.id": socket.gethostname(),
    }
    producer = Producer(conf)

    pending_messages = set()

    def acked(err, msg):
        key = str(msg.key(), encoding="utf-8")

        if err is not None:
            print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
        else:
            conn = psycopg2.connect(
                host=MESSAGE_OUTBOX_DATABASE_HOST,
                dbname=MESSAGE_OUTBOX_DATABASE_NAME,
                user=MESSAGE_OUTBOX_DATABASE_USER,
                password=MESSAGE_OUTBOX_DATABASE_PASSWORD,
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
            host=MESSAGE_OUTBOX_DATABASE_HOST,
            dbname=MESSAGE_OUTBOX_DATABASE_NAME,
            user=MESSAGE_OUTBOX_DATABASE_USER,
            password=MESSAGE_OUTBOX_DATABASE_PASSWORD,
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
                else:
                    print("There are no messages to push")

                producer.poll(1)
                sleep(1)


if __name__ == "__main__":
    main()
