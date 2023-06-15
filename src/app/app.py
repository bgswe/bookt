import asyncio
from typing import Annotated

import asyncpg
import bcrypt
from fastapi import Cookie, Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from cosmos.message_bus import MessageBus, Message
from cosmos.unit_of_work import AsyncUnitOfWorkFactory
from cosmos.contrib.pg.async_uow import AsyncUnitOfWorkPostgres

from app.dependencies import jwt_bearer
from authentication import ExpiredToken, InvalidToken, decode_refresh_token, get_access_token, get_refresh_token
from repository import OrganizationRepository
from commands import Signup, COMMAND_HANDLERS


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def create_database_pool():
    app.pool = await asyncpg.create_pool(
        database='saas_application',
        user='postgres',
    )


@app.on_event("shutdown")
async def close_database_pool():
    await app.pool.close()


async def app_handle(message: Message):
    async with app.pool.acquire() as connection:
        mb = MessageBus(
            uow_factory=AsyncUnitOfWorkFactory[AsyncUnitOfWorkPostgres](
                uow_cls=AsyncUnitOfWorkPostgres,
                repository_cls=OrganizationRepository,
                uow_kwargs={"connection": connection},
                repository_kwargs={"connection": connection},
            ), 
            command_handlers=COMMAND_HANDLERS,
        )

        await mb.handle(message=message)


@app.post("/command/signup/")
async def root(command: Signup):

    await app_handle(message=command)

    return {"message": "signup initiated"}


@app.get("/command/refresh/")
async def refresh(refresh_token: Annotated[str, Cookie()]):
    try:
        payload = decode_refresh_token(token=refresh_token)
        access_token = get_access_token(client_id=payload["client_id"])

        # TODO: should this command also refresh the refresh token?
        # a configurable policy related to refresh token settings 
        # would be a powerful option

        return {"access_token": access_token}
    
    except (ExpiredToken, InvalidToken):
        # unsure if both exceptions should be handled together
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh token expired, please reauthenticate",
        )


@app.post("/command/login/")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """OAuth2 compliant user login"""

    async with app.pool.acquire() as connection:
        user = await connection.fetchrow(
            """
            SELECT
                *
            FROM 
                usr
            WHERE 
                email = $1;
            """,
            form_data.username,
        )

        failed_auth_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

        if user is None:
            raise failed_auth_exception

        is_password_correct = bcrypt.checkpw(
            form_data.password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        )

        if not is_password_correct:
            raise failed_auth_exception
        
        client_id = str(user["id"])
        
        access_token = get_access_token(client_id=client_id)
        refresh_token = get_refresh_token(client_id=client_id)

        # set refresh token as httpOnly cookie, used on backend when access expires
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    
        return {"access_token": access_token}
