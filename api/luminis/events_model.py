import json

from api.luminis.database import database


async def get_unique_event_types() -> list[str]:
    query = "SELECT DISTINCT type FROM events"
    async with database.pool.acquire() as connection:  # type: ignore
        rows = await connection.fetch(query)
        return [record["type"] for record in rows]


async def get_event_list(event_type: str | None) -> list[dict]:
    query = "SELECT data FROM events"

    if event_type:
        query += f" WHERE type = $1"

    query += " ORDER BY created DESC"

    async with database.pool.acquire() as connection:  # type: ignore
        if event_type:
            rows = await connection.fetch(query, event_type)
        else:
            rows = await connection.fetch(query)

        events = [json.loads(record["data"]) for record in rows]
        return events
