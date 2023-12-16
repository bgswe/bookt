import pickle

from domain.service.commands import Register
from fastapi import APIRouter, Depends, Request

from api.dependencies import jwt_bearer
from api.producer import producer

command_router = APIRouter(
    prefix="/command",
    tags=["Accounts"],
)


@command_router.post("/register")
async def register(command: Register):
    message = pickle.dumps(command)

    producer.produce("messages", key=str(command.message_id), value=message)

    return {"detail": "registration initiated"}


query_router = APIRouter(
    prefix="/query", tags=["Accounts"], dependencies=[Depends(jwt_bearer)]
)
