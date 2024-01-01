from confluent_kafka import Producer

conf = {
    "bootstrap.servers": "kafka:9092",
}

producer = Producer(conf)
