import asyncio
import json
import logging
import pickle
from typing import Any, Callable, Protocol

import asyncpg
import structlog
from bookt_domain.model import (  # currently required to auto-register handlers
    command_handlers,
)
from bookt_domain.model.event_handlers import EVENT_HANDLERS
from confluent_kafka import Consumer
from cosmos import (
    Command,
    Event,
    Message,
    UnitOfWork,
    UnitOfWorkFactory,
    default_handlers,
)
from cosmos.contrib.pg import (
    PostgresEventStoreFactory,
    PostgresOutbox,
    PostgresProcessedMessageRepository,
    PostgresUnitOfWork,
)
from cosmos.domain import CommandResult, CommandResultStatus, MessageEncoder

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


class ICommandResultPublisher(Protocol):
    def publish(self: "ICommandResultPublisher", command_result: CommandResult):
        ...


class KafkaCommandResultPublisher:
    def __init__(self):
        from confluent_kafka import Producer

        from message_handler.settings import settings

        conf = {
            "bootstrap.servers": settings.kafka_host,
        }

        self._producer = Producer(conf)

    def _delivery_report(self, err, msg):
        """
        Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush().
        """

        if err is not None:
            print("Message delivery failed: {}".format(err))
        else:
            print("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))

    def publish(self, command_result: CommandResult):
        result_json = json.dumps(
            command_result.model_dump(),
            cls=MessageEncoder,
        )

        logger.bind(cmd_result=result_json).info("CMD RESULT")

        self._producer.produce(
            "command_results",
            key=str(command_result.message_id),
            value=result_json,
            callback=self._delivery_report,
        )


class MessageManager:
    def __init__(
        self: "MessageManager",
        unit_of_work_factory: IUnitOfWorkFactory,
        event_handlers: dict[str, list[Callable]],
        command_handlers: dict[str, Callable],
        command_result_publisher: ICommandResultPublisher,
    ):
        self._uow_factory = unit_of_work_factory
        self._event_handlers = event_handlers
        self._command_handlers = command_handlers
        self._command_result_publisher = command_result_publisher

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
        handlers = self._event_handlers.get(event.type_name)

        if handlers:
            for handler in handlers:
                try:
                    await handler(unit_of_work=unit_of_work, event=event)
                except Exception as e:
                    # TODO: Evaluate what to do when exception occurs
                    log = logger.bind(exception=str(e))
                    log.error("Error during command handler")

    async def _handle_command(
        self: "MessageManager",
        unit_of_work: UnitOfWork,
        command: Command,
    ) -> None:
        handler = self._command_handlers.get(command.type_name)

        if handler:
            try:
                await handler(unit_of_work=unit_of_work, command=command)
            except Exception as e:
                # TODO: Evaluate what to do when exception occurs
                log = logger.bind(exception=str(e))
                log.error("Error during command handler")

            self._command_result_publisher.publish(
                command_result=CommandResult(
                    command_id=command.message_id,
                    command_name=command.type_name,
                    status=CommandResultStatus.SUCCESS,
                )
            )


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
        # TODO: Is this how we should be starting the application?
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
                    repository=PostgresEventStoreFactory(
                        event_store_kwargs={
                            # TODO: Source this config from files
                            "singleton_config": {
                                "TenantRegistrar": "d77e1fc0-488b-4cc7-a264-528514ddaa09",
                                "UserRegistrar": "6a8782b5-8d7b-404c-b0e6-8457011bc8e7",
                            }
                        }
                    ),
                ),
                event_handlers=EVENT_HANDLERS,
                command_handlers=default_handlers,
                command_result_publisher=KafkaCommandResultPublisher(),
            ),
        )

        logger.info("starting app")
        logger.bind(handlers=default_handlers).info("DEFAULT HANDLERS")

        await app.start()

    finally:
        if pool is not None:
            await pool.close()


if __name__ == "__main__":
    asyncio.run(create_and_start_app())
