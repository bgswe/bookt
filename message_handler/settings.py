import structlog
from pydantic_settings import BaseSettings

logger = structlog.get_logger()


class Settings(BaseSettings):
    event_store_host: str = "localhost"
    event_store_database: str = "event_store"
    event_store_user: str = "postgres"
    event_store_password: str = "postgres"
    event_store_port: int = 5432

    kafka_host: str = "localhost:9092"
    kafka_group_id: str = "message-handler"


settings = Settings()

logger.debug(settings)
