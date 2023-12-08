import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
STORAGE_DIR: str = os.path.join(BASE_DIR, "storages")
LOG_DIR: str = os.path.join(STORAGE_DIR, "logs")
SETUP_DIR: str = os.path.join(STORAGE_DIR, "setup")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str
    database_url: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore
