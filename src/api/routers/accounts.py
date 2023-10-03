from app.dependencies import jwt_bearer
from apps.domain.service.commands import Register
from fastapi import APIRouter, Depends, Request

command_router = APIRouter(
    prefix="/command",
    tags=["Accounts"],
)


@command_router.post("/register")
async def register(request: Request, command: Register):
    await request.app.handle(message=command)

    return {"detail": "registration initiated"}


query_router = APIRouter(
    prefix="/query", tags=["Accounts"], dependencies=[Depends(jwt_bearer)]
)
