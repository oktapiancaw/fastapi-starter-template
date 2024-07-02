from contextlib import contextmanager

from loguru import logger
from pymongo import MongoClient

from src.common import envs
from src.models.base import DatabaseConnectionMeta


class MongoConnector:
    def __init__(self, meta: DatabaseConnectionMeta) -> None:
        self._meta: DatabaseConnectionMeta = meta
        if not self._meta.uri:
            self._meta.uri = self._meta.uri_string(base="mongodb", with_db=False)
        self.client = None

    @contextmanager
    def __call__(self, **kwargs):
        self.connect(**kwargs)
        yield self
        self.close()

    def connect(self, **kwargs):
        try:
            self.client: MongoClient = MongoClient(self._meta.uri, **kwargs)
            self.db = self.client[self._meta.database]
            logger.success("Database is connected")
        except:
            raise

    def close(self):
        if self.client:
            self.client.close()
        logger.success("Database is closed")


class MainMongo(MongoConnector):
    def __init__(self) -> None:
        super().__init__(
            meta=DatabaseConnectionMeta(
                host=envs.MONGO_HOST,
                port=envs.MONGO_PORT,
                username=envs.MONGO_USERNAME,
                password=envs.MONGO_PASSWORD,
                database=envs.MONGO_DATABASE,
            )
        )
