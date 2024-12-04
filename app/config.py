import os

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    LOG_LEVEL: str = "INFO"

    QDRANT_HOST: str = "127.0.0.1"
    QDRANT_PORT: int = 6333
    TOPN: int = 10
    HOAX_COLLECTION_NAME: str = "climate_hoax"
    FACT_COLLECTION_NAME: str = "climate_fact"
    CACHE_QUERY_EMBEDDING: bool = True
    VECTOR_SIZE: int = 1024
    USE_DB_SCORE: bool = True

    API_KEY: SecretStr = Field(
        default_factory=lambda: os.environ.get(
            "API_KEY", "ebce2698dadf0593c979a2798c84e49a0"
        )
    )
    API_VERSION: str = Field(
        default_factory=lambda: os.environ.get("API_VERSION", "0.1.0")
    )
    API_HOST: str = Field(default_factory=lambda: os.environ.get("API_HOST", "0.0.0.0"))
    API_PORT: int = Field(default_factory=lambda: os.environ.get("API_PORT", 8091))
    EMBEDDING_SERVING_URL: str
    STANCE_SERVING_URL: str
    TOPIC_SERVING_URL: str
    SUBTOPIC_SERVING_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Config()  # type: ignore

__import__("pprint").pprint(settings.__dict__)

if settings.CACHE_QUERY_EMBEDDING:
    try:
        os.mkdir(".cache")
    except FileExistsError:
        pass
