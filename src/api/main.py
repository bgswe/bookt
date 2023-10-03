import asyncio
from typing import Dict, List

import asyncpg
from app.routers import accounts, authentication
from cosmos.contrib.pg.async_uow import (
    PostgresEventStore,
    PostgresOutbox,
    PostgresUnitOfWork,
)
from cosmos.domain import Event, Message
from cosmos.repository import AggregateReplay
from dependency_injector import containers, providers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from service.command_handlers import COMMAND_HANDLERS
from service.event_handlers import EVENT_HANDLERS

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


async def app_handle(message: Message):
    async with app.pool.acquire() as connection:
        mb = MessageBus(
            uow_factory=AsyncUnitOfWorkFactory[AsyncUnitOfWorkPostgres](
                uow_cls=AsyncUnitOfWorkPostgres,
                uow_kwargs={"connection": connection},
            ),
            command_handlers=COMMAND_HANDLERS,
            event_handlers=EVENT_HANDLERS,
        )

        await mb.handle(message=message)


app.handle = app_handle

app.include_router(authentication.router)
app.include_router(accounts.query_router)
app.include_router(accounts.command_router)
