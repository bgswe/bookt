from uuid import UUID
from fastapi import APIRouter, Depends, Request
from app.dependencies import jwt_bearer

from commands import Signup


signup_router = APIRouter(
    prefix="/command",
    tags=["Organizations"],
)


@signup_router.post("/signup")
async def signup(request: Request, command: Signup):
    await request.app.handle(message=command)

    return {"detail": "signup initiated"}


query_router = APIRouter(
    prefix="/query", tags=["Organizations"], dependencies=[Depends(jwt_bearer)]
)
