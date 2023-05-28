import asyncio

import asyncpg
from fastapi import FastAPI
from cosmos.message_bus import MessageBus, Message
from cosmos.unit_of_work import AsyncUnitOfWorkFactory
from cosmos.contrib.pg.async_uow import AsyncUnitOfWorkPostgres

from repository import OrganizationRepository
from commands import CreateOrganization, COMMAND_HANDLERS


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

app = FastAPI()

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


@app.post("/command/create_organization/")
async def root(command: CreateOrganization):
    
    await app_handle(message=command)

    return {"status": "success", "message": "create organization initiated"}
