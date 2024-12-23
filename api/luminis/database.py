import asyncpg

from api.settings import settings


class Postgres:
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=settings.event_store_host,
            database=settings.event_store_database,
            user=settings.event_store_user,
            password=settings.event_store_password,
            port=settings.event_store_port,
        )

    async def disconnect(self):
        await self.pool.close()  # type: ignore


database = Postgres()
