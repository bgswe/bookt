import structlog
from pydantic_settings import BaseSettings

logger = structlog.get_logger()


class Settings(BaseSettings):
    iteration_sleep_duration: float = 1.0

    database_host: str = "localhost"
    database_name: str = "event_store"
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_port: int = 5432

    kafka_host: str = "localhost:9092"
    kafka_group_id: str = "message-handler"


settings = Settings()

logger.debug(settings)
