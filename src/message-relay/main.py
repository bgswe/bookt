import socket
from time import sleep

import psycopg2
from confluent_kafka import Producer


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
            conn = psycopg2.connect(dbname="bookt", user="postgres", password="")

            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""
                        INSERT INTO
                            processed_messages (id)
                        VALUES
                            ('{key}');
                    """,
                    )

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
        conn = psycopg2.connect(dbname="bookt", user="postgres", password="")

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
                            value=m[columns["message"]].tobytes(),
                            callback=acked,
                        )

                        pending_messages.add(message_id)
                else:
                    print("There are no messages to push")

                producer.poll(1)
                sleep(1)


if __name__ == "__main__":
    main()