import socket

from confluent_kafka import Producer

conf = {
    "bootstrap.servers": "192.168.0.11:9092",
    "client.id": socket.gethostname(),
}

producer = Producer(conf)
