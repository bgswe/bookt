from confluent_kafka import Producer

conf = {
    "bootstrap.servers": "kafka:29092",
}

producer = Producer(conf)
