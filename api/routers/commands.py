import pickle

from bookt_domain.model.commands import RegisterTenant
from cosmos.domain import Command

# from fastapi import APIRouter, Depends
from fastapi import APIRouter

# from api.dependencies import jwt_bearer
from api.producer import producer

# TODO: Utilize jwt_bearer auth
# command_router = APIRouter(prefix="/command", dependencies=[Depends(jwt_bearer)])

command_router = APIRouter(prefix="/command")


def delivery_report(err, msg):
    """
    Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush().
    """

    if err is not None:
        print("Message delivery failed: {}".format(err))
    else:
        print("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


def send_command_to_message_bus(command: Command):
    message = pickle.dumps(command)

    producer.produce(
        "messages", key=str(command.message_id), value=message, callback=delivery_report
    )
    producer.poll(1)
    producer.flush()


@command_router.post("/register-tenant")
async def register(command: RegisterTenant):
    send_command_to_message_bus(command=command)
    return {"detail": "registration initiated"}
