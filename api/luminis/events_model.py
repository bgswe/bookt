import json

from api.luminis.database import database


async def get_event_list() -> list[dict]:
    query = "SELECT * FROM events"
    async with database.pool.acquire() as connection:  # type: ignore
        rows = await connection.fetch(query)
        events = [json.loads(record["data"]) for record in rows]
        return events
