from confluent_kafka import Producer

from api.settings import settings

conf = {
    "bootstrap.servers": settings.kafka_host,
}

producer = Producer(conf)
