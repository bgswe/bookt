from abc import ABC
from datetime import datetime as dt
from uuid import UUID

from cosmos.contrib.pg.async_uow import AsyncPGRepository

from domain import Organization, User


class UserRepository(AsyncPGRepository):
    async def _add(self, user: User):
        now = dt.now()

        await self.connection.execute(
            """
            INSERT INTO bookt_user
                (id, created_at, updated_at, organization_id, email, password, first_name, last_name)
            VALUES
                ($1, $2, $3, $4, $5, $6, $7, $8);
            """,
            user.id,
            now,
            now,
            user.organization_id,
            user.email,
            user.password,
            user.first_name,
            user.last_name,
        )


class OrganizationRepository(AsyncPGRepository):
    async def _add(self, organization: Organization):
        now = dt.now()

        await self.connection.execute(
            """
            INSERT INTO bookt_organization
                (id, created_at, updated_at, name)
            VALUES
                ($1, $2, $3, $4);
            """,
            organization.id,
            now,
            now,
            organization.name,
        )

    async def _get(self, id: UUID):
        ...
