import asyncio

import asyncpg
from cosmos.contrib.pg.async_uow import AsyncUnitOfWorkPostgres
from cosmos.contrib.redis import get_redis_client, redis_publisher
from cosmos.message_bus import Message, MessageBus
from cosmos.unit_of_work import AsyncUnitOfWorkFactory
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import authentication, organizations
from handlers import COMMAND_HANDLERS, EVENT_HANDLERS

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
        database="bookt",
        user="postgres",
    )


@app.on_event("shutdown")
async def close_database_pool():
    await app.pool.close()


async def app_handle(message: Message):
    async with app.pool.acquire() as connection:
        mb = MessageBus(
            uow_factory=AsyncUnitOfWorkFactory[AsyncUnitOfWorkPostgres](
                uow_cls=AsyncUnitOfWorkPostgres,
                uow_kwargs={"connection": connection},
            ),
            command_handlers=COMMAND_HANDLERS,
            event_handlers=EVENT_HANDLERS,
            event_publish=redis_publisher(client=get_redis_client()),
        )

        await mb.handle(message=message)


app.handle = app_handle

app.include_router(authentication.router)
app.include_router(organizations.query_router)
app.include_router(organizations.signup_router)
