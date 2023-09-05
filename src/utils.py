import json
from uuid import UUID

import asyncpg


def obj_encoder(o):
    if isinstance(o, UUID):
        return str(o)


def json_encode(data):
    """Specialized json serializer"""

    return json.dumps(data, default=obj_encoder)


async def generate_postgres_pool(
    database: str,
    user: str,
):
    """Async generator providing the PostgreSQL connection pool"""

    pool = await asyncpg.create_pool(
        database=database,
        user=user,
    )

    yield pool

    await pool.close()
