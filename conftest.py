from typing import Iterable

import pytest
from cosmos.domain import Event
from cosmos.repository import AsyncRepository
from cosmos.unit_of_work import Collect
from structlog import get_logger  # noqa

logger = get_logger()


def mock_collect(repository: AsyncRepository) -> Iterable[Event]:
    """Simple test collect that returns the seen aggregates in a new list."""

    return [*repository.seen]


class MockAsyncUnitOfWork:
    def __init__(self, repository: AsyncRepository, collect: Collect):
        """Takes in a repo and a Collector object for use in UnitOfWork."""

        self._repository = repository
        self._collect = collect

    async def __aenter__(self):
        """Simple test implementation."""

        logger.debug("MockAsyncUnitOfWork.__aenter__")

        return self

    async def __aexit__(self, *args):
        """Simple test implementation."""

        logger.debug("MockAsyncUnitOfWork.__aexit__")

    @property
    def repository(self) -> AsyncRepository:
        """Getter for the repository instance."""

        return self._repository

    def collect_events(self) -> Iterable[Event]:
        """Test implementation of collect_events."""

        return self._collect(repository=self._repository)


@pytest.fixture
def make_mock_uow():
    def make(repository: AsyncRepository):
        return MockAsyncUnitOfWork(
            repository=repository,
            collect=mock_collect,
        )

    return make
