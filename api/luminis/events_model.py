import json

from api.luminis.database import database


async def get_unique_event_types() -> list[str]:
    query = "SELECT DISTINCT type FROM events"
    async with database.pool.acquire() as connection:  # type: ignore
        rows = await connection.fetch(query)
        return [record["type"] for record in rows]


async def get_event_list() -> list[dict]:
    query = "SELECT data FROM events ORDER BY created DESC"
    async with database.pool.acquire() as connection:  # type: ignore
        rows = await connection.fetch(query)
        events = [json.loads(record["data"]) for record in rows]
        return events
