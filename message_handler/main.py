import asyncio
import logging
import pickle
from typing import Any, Callable, Protocol

import asyncpg
import structlog
from bookt_domain.model.command_handlers import COMMAND_HANDLERS
from bookt_domain.model.event_handlers import EVENT_HANDLERS
from confluent_kafka import Consumer
from cosmos import Command, Event, Message, UnitOfWork, UnitOfWorkFactory
from cosmos.contrib.pg import (
    PostgresEventStoreFactory,
    PostgresOutbox,
    PostgresProcessedMessageRepository,
    PostgresUnitOfWork,
)

from message_handler.settings import settings

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
logger = structlog.get_logger()


class MessageBusConsumeError(Exception):
    def __init__(self, consume_error: Any = None):
        self.consume_error = consume_error


class InvalidMessageError(Exception):
    def __init__(self, invalid_message: Any):
        self.message = invalid_message


class KafkaMessageBus:
    def __init__(self, hostname: str, group_id: str, topics: list[str]):
        self._consumer = Consumer(
            {
                "bootstrap.servers": hostname,
                "group.id": group_id,
                "auto.offset.reset": "earliest",
            }
        )
        self._consumer.subscribe(topics)

    def get_message(self) -> Message:
        while True:
            message = self._consumer.poll(timeout=1.0)

            if message is None:
                continue

            if error := message.error():
                raise MessageBusConsumeError(consume_error=error)

            return pickle.loads(message.value())


class IMessageBus(Protocol):
    def get_message(self: "IMessageBus") -> Message:
        ...


class IUnitOfWorkFactory(Protocol):
    def get(self: "IUnitOfWorkFactory") -> UnitOfWork:
        ...


class MessageManager:
    def __init__(
        self: "MessageManager",
        unit_of_work_factory: IUnitOfWorkFactory,
        event_handlers: dict[str, list[Callable]],
        command_handlers: dict[str, Callable],
    ):
        self._uow_factory = unit_of_work_factory
        self._event_handlers = event_handlers
        self._command_handlers = command_handlers

    async def handle_message(self: "MessageManager", message: Message) -> None:
        # enable ability to run ancillary code after command handled, under single transaction
        async with self._uow_factory.get() as uow:
            logger.debug(f"handling message ID: {message.message_id}")

            # ensure idempotency by checking if messages has been processed
            processed_record = await uow.processed_messages.is_processed(
                message_id=message.message_id,
            )

            if processed_record:
                logger.debug(f"message already processed ID: {processed_record}")
                return

            if isinstance(message, Event):
                await self._handle_event(unit_of_work=uow, event=message)
            elif isinstance(message, Command):
                await self._handle_command(unit_of_work=uow, command=message)
            else:
                log = logger.bind(message_type=type(message))
                log.error("message is not event, nor comand")

            # to ensure message idempotency we record message ID as processed
            await uow.processed_messages.mark_processed(message_id=message.message_id)

    async def _handle_event(
        self: "MessageManager",
        unit_of_work: UnitOfWork,
        event: Event,
    ) -> None:
        handlers = self._event_handlers.get(event.name)

        if handlers:
            for handler in handlers:
                await handler(uow=unit_of_work, event=event)

    async def _handle_command(
        self: "MessageManager",
        unit_of_work: UnitOfWork,
        command: Command,
    ) -> None:
        handler = self._command_handlers.get(command.name)

        if handler:
            await handler(unit_of_work=unit_of_work, command=command)


class IMessageManager(Protocol):
    async def handle_message(self: "IMessageManager", message: Message) -> None:
        ...


class Application:
    def __init__(
        self,
        message_bus: IMessageBus,
        message_manager: IMessageManager,
    ) -> None:
        self._message_bus = message_bus
        self._message_manager = message_manager

    async def start(self):
        while True:
            try:
                message = self._message_bus.get_message()
                await self._message_manager.handle_message(message=message)

            except MessageBusConsumeError as e:
                log = logger.bind(read_error=e.consume_error)
                log.error("MessageBusReadError")


async def create_and_start_app():
    try:
        pool = await asyncpg.create_pool(
            # host=settings.event_store_host,
            host="postgres",
            database=settings.event_store_database,
            user=settings.event_store_user,
            password=settings.event_store_password,
            port=settings.event_store_port,
        )

        app = Application(
            message_bus=KafkaMessageBus(
                hostname=settings.kafka_host,
                group_id=settings.kafka_group_id,
                topics=["messages"],
            ),
            message_manager=MessageManager(
                unit_of_work_factory=UnitOfWorkFactory(
                    unit_of_work_cls=PostgresUnitOfWork,
                    pool=pool,
                    processed_message_repository=PostgresProcessedMessageRepository(),
                    outbox=PostgresOutbox(),
                    repository=PostgresEventStoreFactory(),
                ),
                event_handlers=EVENT_HANDLERS,
                command_handlers=COMMAND_HANDLERS,
            ),
        )

        logger.info("starting app")

        await app.start()

    finally:
        if pool is not None:
            await pool.close()


if __name__ == "__main__":
    asyncio.run(create_and_start_app())
