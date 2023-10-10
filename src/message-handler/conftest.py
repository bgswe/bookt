from typing import List

import pytest
from cosmos.contrib.pg.containers import MockDomainContainer
from cosmos.domain import Command, Event, Message

from domain.service.command_handlers import COMMAND_HANDLERS
from domain.service.event_handlers import EVENT_HANDLERS


@pytest.fixture
def container():
    container = MockDomainContainer()

    return container


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


@pytest.fixture
def producer(container):
    return MockProducer(container=container)
