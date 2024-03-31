import structlog
from pydantic_settings import BaseSettings

logger = structlog.get_logger()


class Settings(BaseSettings):
    database_host: str = "localhost"
    database_name: str = "query_store"
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_port: int = 5434

    kafka_host: str = "localhost:9092"
    kafka_group_id: str = "read-manager"


settings = Settings()

logger.debug(settings)
