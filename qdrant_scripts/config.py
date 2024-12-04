import os

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    LOG_CONFIG_FILE: str = "logging.yaml"

    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    HOAX_COLLECTION_NAME: str = "climate_hoax"
    FACT_COLLECTION_NAME: str = "climate_fact"

    CACHE_QUERY_EMBEDDING: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Config()
# openai.api_key = settings.OPENAI_API_KEY

if settings.CACHE_QUERY_EMBEDDING:
    try:
        os.mkdir(".cache")
    except FileExistsError:
        pass
