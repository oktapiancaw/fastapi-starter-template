from loguru import logger
from sqlalchemy import Engine, URL
from sqlmodel import create_engine, Session

from src.common.env import envs
from src.models.base import DatabaseConnectionMeta


class PostgreSQLConnector:
    def __init__(self, meta: DatabaseConnectionMeta) -> None:
        self._meta: DatabaseConnectionMeta = meta
        if not self._meta.uri:
            self._meta.uri = self._meta.uri_string(
                base="postgresql+psycopg2", with_db=True
            )
        self.client = None

    def connect(self, **kwargs):
        try:
            if "@" in self._meta.password:
                self.engine: Engine = create_engine(
                    URL.create(
                        drivername="postgresql+psycopg2",
                        username=self._meta.username,
                        password=self._meta.password,
                        host=self._meta.host,
                        port=self._meta.port,
                        database=self._meta.database,
                    )
                )
            else:
                self.engine: Engine = create_engine(self._meta.uri, **kwargs)
            self.client = Session(self.engine)
            logger.success("Database is connected")
        except Exception:
            raise ValueError("Failed to connect to PostgreSQL")

    def close(self):
        if self.client:
            self.client.close()
        logger.success("Database is closed")


class MainPostgre(PostgreSQLConnector):
    def __init__(self) -> None:
        super().__init__(
            DatabaseConnectionMeta(
                host=envs.POSTGRE_HOST,
                port=envs.POSTGRE_PORT,
                username=envs.POSTGRE_USERNAME,
                password=envs.POSTGRE_PASSWORD,
                database=envs.POSTGRE_DATABASE,
            )
        )
