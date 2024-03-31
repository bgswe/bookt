import structlog
from pydantic_settings import BaseSettings

logger = structlog.get_logger()


class Settings(BaseSettings):
    database_host: str = "localhost"
    database_name: str = "query_store"
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_port: int = 5432

    kafka_host: str = "localhost:9092"

    hash_algorithm: str = "HS256"
    access_token_duration: int = 86400
    access_token_secret: str = "access_token_secret"
    refresh_token_duration: int = 86400
    refresh_token_secret: str = "refresh_token_secret"


settings = Settings()

logger.debug(settings)
