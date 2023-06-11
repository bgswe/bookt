from abc import ABC
from datetime import datetime as dt
from uuid import UUID

from cosmos.contrib.pg.async_uow import AsyncPGRepository

from domain import Organization


class OrganizationRepository(AsyncPGRepository):
    async def _add(self, organization: Organization):
        
        now = dt.now()

        await self.connection.executemany(
            """
            INSERT INTO usr
                (id, created_at, updated_at, organization_id, email, password_hash, first_name, last_name)
            VALUES
                ($1, $2, $3, $4, $5, $6, $7, $8);
            """,
            [
                (
                    user.id,
                    now,
                    now,
                    organization.id,
                    user.email,
                    user.hashed_password,
                    user.first_name,
                    user.last_name,
                )
                for user in organization.users
            ]
        )

        await self.connection.execute(
            """
            INSERT INTO organization
                (id, created_at, updated_at, name)
            VALUES
                ($1, $2, $3, $4);
            """,
            organization.id,
            now,
            now,
            organization.name,
        )


