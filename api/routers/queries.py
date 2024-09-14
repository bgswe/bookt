# from fastapi import APIRouter, Depends
from fastapi import APIRouter

# from api.dependencies import jwt_bearer

# TODO: Utilize jwt_bearer auth
# command_router = APIRouter(prefix="/command", dependencies=[Depends(jwt_bearer)])
# query_router = APIRouter(prefix="/query", dependencies=[Depends(jwt_bearer)])

query_router = APIRouter(prefix="/query")
