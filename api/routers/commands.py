import pickle
from typing import Annotated

from bookt_domain.model.commands import (
    RegisterTenant,
    RegisterUser,
    ValidateTenantEmail,
)
from cosmos.domain import Command

# from fastapi import APIRouter, Depends
from fastapi import APIRouter, Body

# from api.dependencies import jwt_bearer
from api.producer import producer

# TODO: Utilize jwt_bearer auth
# command_router = APIRouter(prefix="/command", dependencies=[Depends(jwt_bearer)])

command_router = APIRouter(prefix="/command", tags=["Commands"])


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
async def register_tenant(
    command: Annotated[
        RegisterTenant,
        Body(
            examples=[
                {
                    "tenant_id": "39f8ccdc-97b3-4bb7-ae6b-8a75ea5cabff",
                    "tenant_name": "Tenant ABC",
                    "tenant_registration_email": "tenant@example.com",
                }
            ],
        ),
    ],
):
    send_command_to_message_bus(command=command)
    return {"detail": "tenant registration initiated"}


@command_router.post("/validate-tenant-registration-email")
async def validate_tenant_registration_email(
    command: Annotated[
        ValidateTenantEmail,
        Body(
            examples=[
                {
                    "validation_key": "7933bc0b-bd7a-4d1b-bbef-bf4659335dc7.8c109128d0a841a683bcf64ea3fde5d4",
                }
            ],
        ),
    ],
):
    send_command_to_message_bus(command=command)
    return {"detail": "tenant email validation initiated"}


@command_router.post("/register-user")
async def register_user(
    command: Annotated[
        RegisterUser,
        Body(
            examples=[
                {
                    "tenant_id": "39f8ccdc-97b3-4bb7-ae6b-8a75ea5cabff",
                    "user_id": "a14e84d0-882a-411b-bf88-841387832c58",
                    "email": "new_user@example.com",
                }
            ],
        ),
    ],
):
    send_command_to_message_bus(command=command)
    return {"detail": "user registration initiated"}
