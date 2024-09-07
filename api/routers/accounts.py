import pickle

from bookt_domain.model.commands import Register
from fastapi import APIRouter, Depends

from api.dependencies import jwt_bearer
from api.producer import producer

command_router = APIRouter(
    prefix="/command",
    tags=["Accounts"],
)


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush()."""
    if err is not None:
        print("Message delivery failed: {}".format(err))
    else:
        print("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


@command_router.post("/register")
async def register(command: Register):
    message = pickle.dumps(command)

    producer.produce(
        "messages", key=str(command.message_id), value=message, callback=delivery_report
    )
    producer.poll(1)
    producer.flush()

    return {"detail": "registration initiated"}


query_router = APIRouter(
    prefix="/query", tags=["Accounts"], dependencies=[Depends(jwt_bearer)]
)
