import structlog
from pydantic_settings import BaseSettings

logger = structlog.get_logger()


class Settings(BaseSettings):
    kafka_host: str = "localhost:9092"

    event_store_host: str = "0.0.0.0"
    event_store_database: str = "event_store"
    event_store_user: str = "postgres"
    event_store_password: str = "postgres"
    event_store_port: int = 5432

    # database_host: str = "localhost"
    # database_name: str = "query_store"
    # database_user: str = "postgres"
    # database_password: str = "postgres"
    # database_port: int = 5432

    # hash_algorithm: str = "HS256"
    # access_token_duration: int = 86400
    # access_token_secret: str = "access_token_secret"
    # refresh_token_duration: int = 86400
    # refresh_token_secret: str = "refresh_token_secret"


settings = Settings()

logger.debug(settings)
