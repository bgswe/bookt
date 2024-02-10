import structlog
from pydantic_settings import BaseSettings

logger = structlog.get_logger()


class Settings(BaseSettings):
    kafka_host: str = "localhost:9092"
    kafka_group_id: str = "read-manager"


settings = Settings()

logger.debug(settings)
