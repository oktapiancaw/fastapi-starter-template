from typing import Optional, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", env_prefix=""
    )

    POSTGRE_HOST: Optional[str] = Field("localhost")
    POSTGRE_PORT: Optional[Union[str, int]] = Field(5432)
    POSTGRE_USERNAME: Optional[str] = None
    POSTGRE_PASSWORD: Optional[str] = None
    POSTGRE_DATABASE: str


def env_settings(other_env: str = None) -> Settings:
    if other_env:
        return Settings(_env_file=other_env)
    return Settings()


envs = env_settings()
