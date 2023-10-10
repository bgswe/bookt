import pickle

from fastapi import APIRouter, Depends, Request

from api.dependencies import jwt_bearer
from api.producer import producer
from domain.service.commands import Register

command_router = APIRouter(
    prefix="/command",
    tags=["Accounts"],
)


@command_router.post("/register")
async def register(request: Request, command: Register):
    message = pickle.dumps(command)

    producer.produce("messages", key=str(command.message_id), value=message)

    return {"detail": "registration initiated"}


query_router = APIRouter(
    prefix="/query", tags=["Accounts"], dependencies=[Depends(jwt_bearer)]
)
