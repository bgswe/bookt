from abc import ABC
from uuid import UUID

from cosmos.contrib.pg.async_uow import AsyncPGRepository
from cosmos.domain import AggregateRoot


class OrganizationRepository(AsyncPGRepository):
    async def _add(self, aggregate: AggregateRoot):
        print(aggregate, self.connection)
