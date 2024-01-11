from typing import Optional, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", env_prefix="TEMPLATE_"
    )
    
    MONGO_HOST: str
    MONGO_PORT: int | str = Field(27017)
    MONGO_DATABASE: str


def env_settings(other_env: str = None) -> Settings:
    if other_env:
        return Settings(_env_file=other_env)
    return Settings()


envs = env_settings()
