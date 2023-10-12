from typing import Dict, List
from uuid import UUID

import pytest
from cosmos.domain import AggregateRoot, Command, Event, Message
from cosmos.repository import AggregateRepository
from cosmos.unit_of_work import UnitOfWork
from dependency_injector import containers, providers

from domain.service.command_handlers import COMMAND_HANDLERS
from domain.service.event_handlers import EVENT_HANDLERS


class MockProducer:
    def __init__(self, container):
        self._container = container
        self._queue = []
        self._uow = None

    async def produce(self, message: Message):
        self._queue = [message]

        while self._queue:
            current_message = self._queue.pop(0)

            if isinstance(current_message, Event):
                handlers = EVENT_HANDLERS.get(current_message.name)
                if handlers is not None:
                    for handler in handlers:
                        self._uow = self._container.unit_of_work()
                        await handler(uow=self._uow, event=current_message)
                        self._collect_events()
                        self._uow = None

            elif isinstance(current_message, Command):
                handler = COMMAND_HANDLERS.get(current_message.name)
                if handler is not None:
                    self._uow = self._container.unit_of_work()
                    await handler(uow=self._uow, command=current_message)
                    self._collect_events()
                    self._uow = None

    def _collect_events(self) -> List[Event]:
        aggs = self._uow.repository.seen
        for agg in aggs:
            self._queue.extend(agg.events)


class MockAggregateStore:
    def __init__(self):
        self._store = {}

    def get(self, id: UUID) -> AggregateRoot | None:
        return self._store.get(id)

    def save(self, agg: AggregateRoot):
        self._store[agg.id] = agg


class MockRepository(AggregateRepository):
    def __init__(self, aggregate_store: Dict):
        super().__init__()

        self._store = aggregate_store

    async def _get(self, id: UUID) -> AggregateRoot | None:
        return self._store.get(id)

    async def _save(self, agg: AggregateRoot):
        self._store.save(agg)


class MockUnitOfWork(UnitOfWork):
    async def __aenter__(self) -> UnitOfWork:
        print("__aenter__ from MockUnitOfWork")
        return self

    async def __aexit__(self, *args):
        print("__aexit__ from MockUnitOfWork")
        for agg in self.repository.seen:
            self.outbox.send(messages=agg.events)


class MockProcessedMessagesRepository:
    def __init__(self):
        self._store = set()

    async def is_processed(self, message_id: UUID) -> bool:
        return message_id in self._store

    async def mark_processed(self, message_id: UUID):
        self._store.add(message_id)


class MockTransactionalOutbox:
    def __init__(self):
        self._outbox = []

    def send(self, messages: List):
        for message in messages:
            self._outbox.append(message)


class MockDomainContainer(containers.DeclarativeContainer):
    aggregate_store = providers.Singleton(MockAggregateStore)
    processed_message_repo = providers.Singleton(MockProcessedMessagesRepository)
    outbox = providers.Singleton(MockTransactionalOutbox)

    repository = providers.Factory(
        MockRepository,
        aggregate_store=aggregate_store,
    )

    unit_of_work = providers.Factory(
        MockUnitOfWork,
        repository=repository,
        outbox=outbox,
        processed_message_repository=processed_message_repo,
    )


@pytest.fixture
def container():
    container = MockDomainContainer()

    return container


@pytest.fixture
def producer(container):
    return MockProducer(container=container)
